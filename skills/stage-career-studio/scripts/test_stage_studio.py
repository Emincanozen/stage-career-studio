"""Run with Python; only synthetic data inside TemporaryDirectory."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
import stage_studio as studio


class StudioTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'candidate'
        studio.initialize(self.root)
        studio.atomic_json(self.root/'facts.json',{'schema_version':1,'facts':[{'id':'F001','text':'Projet fictif de test','status':'confirmed','source':'Fixture fictive'},{'id':'F002','text':'Prévu','status':'planned','source':'Fixture fictive'}]})
        self.offer={'id':'DEMO-01','company':'Entreprise fictive','reference':'01','title':'Stage fictif','city':'Ville fictive','url':'https://example.com/jobs?id=01','summary':'Description fictive de test','availability':'uncertain','documents':[],'rating':{'score':None},'matches':[]}

    def tearDown(self):self.temp.cleanup()

    def add(self):studio.upsert(self.root,[self.offer])

    def test_init_does_not_overwrite(self):
        content=(self.root/'state.json').read_bytes()
        with self.assertRaises(ValueError):studio.initialize(self.root)
        self.assertEqual((self.root/'state.json').read_bytes(),content)

    def test_build_and_upsert_preserve_sent_state(self):
        self.add();store=studio.StateStore(self.root);state=store.get()
        result=store.update({'workspace_id':state['workspace_id'],'expected_version':0,'items':{'DEMO-01':{'status':'envoyee','note':'Texte à conserver','sent_files':'CV v1'}}})
        before=(self.root/'state.json').read_bytes();new={**self.offer,'summary':'Description actualisée'}
        studio.upsert(self.root,[new]);studio.build(self.root)
        self.assertEqual((self.root/'state.json').read_bytes(),before)
        self.assertEqual(result['items']['DEMO-01']['status'],'envoyee')

    def test_version_conflict_no_loss(self):
        self.add();store=studio.StateStore(self.root);s=store.get()
        payload={'workspace_id':s['workspace_id'],'expected_version':0,'items':{'DEMO-01':{'status':'expiree'}}}
        store.update(payload);before=(self.root/'state.json').read_bytes()
        with self.assertRaises(studio.Conflict):store.update(payload)
        self.assertEqual((self.root/'state.json').read_bytes(),before)
        self.assertEqual(studio.read(self.root/'state.backup.json')['version'],0)

    def test_unknown_offer_and_foreign_workspace_refused(self):
        self.add();store=studio.StateStore(self.root);s=store.get()
        for wid,key in [('another-user','DEMO-01'),(s['workspace_id'],'NONEXISTENT')]:
            with self.assertRaises(ValueError):store.update({'workspace_id':wid,'expected_version':0,'items':{key:{'status':'envoyee'}}})
        self.assertEqual(store.get()['version'],0)

    def test_duplicate_reference_or_tracking_url_refused(self):
        self.add();before=(self.root/'offers.json').read_bytes()
        for other in [{**self.offer,'id':'DEMO-02','url':'https://example.com/other'},{**self.offer,'id':'DEMO-02','reference':'02','url':self.offer['url']+'&utm_source=copy'}]:
            with self.assertRaises(ValueError):studio.upsert(self.root,[other])
        self.assertEqual((self.root/'offers.json').read_bytes(),before)

    def test_query_identity_preserved(self):
        self.add();other={**self.offer,'id':'DEMO-02','reference':'02','url':'https://example.com/jobs?id=02'}
        self.assertEqual(studio.upsert(self.root,[other]),1)

    def test_missing_document_and_path_traversal_refused(self):
        for path in ['documents/missing.pdf','../secret.txt','C:/private.pdf','documents/../../secret']:
            other={**self.offer,'documents':[{'kind':'cv','label':'CV','path':path}]}
            with self.assertRaises(ValueError):studio.upsert(self.root,[other])
        self.assertEqual(studio.read(self.root/'offers.json'),[])

    def test_old_documents_preserved(self):
        for n in ('v1.txt','v2.txt'):(self.root/'documents'/n).write_text('Fichier fictif',encoding='utf-8')
        first={**self.offer,'documents':[{'kind':'cv','label':'Ancienne version fictive','path':'documents/v1.txt'}]}
        second={**self.offer,'documents':[{'kind':'cv','label':'Nouvelle version fictive','path':'documents/v2.txt'}]}
        studio.upsert(self.root,[first]);studio.upsert(self.root,[second])
        self.assertEqual(len(studio.read(self.root/'offers.json')[0]['documents']),2)

    def test_unconfirmed_fact_cannot_support_cv(self):
        other={**self.offer,'matches':[{'requirement':'Compétence','assessment':'direct','fact_ids':['F002']}]}
        with self.assertRaises(ValueError):studio.upsert(self.root,[other])

    def test_scores_require_consistent_evidence_and_no_blocker(self):
        valid={**self.offer,'matches':[{'requirement':'Compétence','assessment':'transfer','fact_ids':['F001']}],'rating':{'score':8,'explanation':'Explication fictive','components':{'missions':3,'prerequisites':2,'motivation':2,'learning':1}}}
        studio.upsert(self.root,[valid])
        for changes in [{'blockers':['Indispensable absent']},{'rating':{'score':9,'explanation':'Sans détail'}},{'rating':{**valid['rating'],'score':9}},{'matches':[]}]:
            with self.assertRaises(ValueError):studio.upsert(self.root,[{**valid,**changes}])

    def test_untrusted_html_escaped_in_embedded_payload(self):
        malicious='</script><script>alert("unsafe")</script>'
        studio.upsert(self.root,[{**self.offer,'summary':malicious}])
        page=(self.root/'index.html').read_text('utf-8')
        self.assertNotIn(malicious,page);self.assertIn('\\u003c/script>',page)

    def test_bundle_roundtrip_and_no_overwrite(self):
        self.add();store=studio.StateStore(self.root);s=store.get()
        store.update({'workspace_id':s['workspace_id'],'expected_version':0,'items':{'DEMO-01':{'status':'envoyee'}}})
        target=Path(self.temp.name)/'private.zip';studio.bundle(self.root,target)
        with zipfile.ZipFile(target) as z:
            self.assertIsNone(z.testzip());self.assertEqual(json.loads(z.read('offers.json'))[0]['id'],'DEMO-01')
            self.assertIn('state.json',z.namelist())
            self.assertIn('"status": "envoyee"',z.read('index.html').decode('utf-8'))
        with self.assertRaises(ValueError):studio.bundle(self.root,target)

    def test_invalid_facts_and_states_refused(self):
        self.add();facts=studio.read(self.root/'facts.json');state=studio.read(self.root/'state.json')
        bad=copy.deepcopy(facts);bad['facts'].append(copy.deepcopy(bad['facts'][0]));studio.atomic_json(self.root/'facts.json',bad)
        with self.assertRaises(ValueError):studio.load_workspace(self.root)
        studio.atomic_json(self.root/'facts.json',facts)
        state['items']['unknown']=None;studio.atomic_json(self.root/'state.json',state)
        with self.assertRaises(ValueError):studio.build(self.root)

    def test_sent_offer_identity_not_reused(self):
        self.add();store=studio.StateStore(self.root);s=store.get()
        store.update({'workspace_id':s['workspace_id'],'expected_version':0,'items':{'DEMO-01':{'status':'envoyee'}}})
        for changes in [{'company':'Autre employeur'},{'title':'Autre métier'}]:
            with self.assertRaises(ValueError):studio.upsert(self.root,[{**self.offer,**changes}])

    def test_indexed_document_integrity_checked(self):
        path=self.root/'documents/cv.txt';path.write_text('Version envoyée fictive',encoding='utf-8')
        studio.upsert(self.root,[{**self.offer,'documents':[{'kind':'cv','label':'CV fictif','path':'documents/cv.txt'}]}])
        path.write_text('Écrasement accidentel',encoding='utf-8')
        with self.assertRaises(ValueError):studio.build(self.root)


if __name__=='__main__':unittest.main(verbosity=2)
