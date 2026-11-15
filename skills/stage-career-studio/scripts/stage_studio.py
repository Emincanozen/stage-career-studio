#!/usr/bin/env python3
"""Local internship tracker toolkit. Standard library, no external requests."""
import argparse
import copy
import datetime as dt
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import tempfile
import threading
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlencode, urlsplit, unquote
import uuid
import zipfile

SKILL = Path(__file__).resolve().parents[1]
STATUSES = {'a_verifier','a_faire','envoyee','entretien','refus','offre','ecartee','expiree'}
KINDS = {'cv','letter','analysis','editable'}
LIMIT = 4 * 1024 * 1024


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def atomic_json(path, value, backup=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists():
        shutil.copy2(path, path.with_suffix('.backup.json'))
    fd, name = tempfile.mkstemp(prefix='.'+path.name, suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as out:
            json.dump(value, out, ensure_ascii=False, indent=2, allow_nan=False)
            out.flush()
            os.fsync(out.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def local_path(root, relative):
    if not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative:
        raise ValueError('Chemin de document relatif requis.')
    rel = Path(relative)
    if rel.is_absolute() or '..' in rel.parts or relative.startswith('/'):
        raise ValueError('Chemin extérieur au dossier refusé.')
    target = (root / rel).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('Lien de document extérieur refusé.')
    return target


def canonical(url):
    u = urlsplit(url)
    if u.scheme not in ('https','http') or not u.hostname or u.username or u.password:
        raise ValueError('Lien employeur HTTP(S) valide requis.')
    query = [(k,v) for k,v in parse_qsl(u.query, keep_blank_values=True)
             if not k.lower().startswith('utm_') and k.lower() not in ('gclid','fbclid','trackingid')]
    return (u.hostname.lower(), unquote(u.path).rstrip('/'), tuple(sorted(query)))


def offer_identity(offer):
    if offer.get('reference'):
        return ('ref', offer.get('employer_group',offer['company']).strip().casefold(), str(offer['reference']).casefold())
    return ('url', canonical(offer['url']))


def validate_offers(root, offers, facts):
    if not isinstance(offers,list):
        raise ValueError('offers.json doit être une liste.')
    confirmed = {f['id'] for f in facts.get('facts',[]) if f.get('status')=='confirmed'}
    ids, identities, urls = set(), set(), set()
    for o in offers:
        for k in ('id','company','title','url'):
            if not isinstance(o.get(k),str) or not o[k].strip():
                raise ValueError('Offre : champ manquant '+k)
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,159}',o['id']):
            raise ValueError('Identifiant stable invalide : '+o['id'])
        if any(k in o for k in ('status','note','sent_files')):
            raise ValueError('États personnels à placer dans state.json.')
        identity, url = offer_identity(o), canonical(o['url'])
        if o['id'] in ids or identity in identities or url in urls:
            raise ValueError('Offre en doublon : '+o['id'])
        ids.add(o['id']);identities.add(identity);urls.add(url)
        if o.get('availability','uncertain') not in ('open','closed','uncertain'):
            raise ValueError('Disponibilité invalide.')
        for key in ('publication_date','first_seen_at','checked_at'):
            value=o.get(key)
            if value is not None:
                try:dt.date.fromisoformat(value)
                except (ValueError,TypeError):raise ValueError('Date ISO invalide : '+key)
        if o.get('availability')=='open' and (not o.get('checked_at') or not o.get('source_note') or not o.get('summary')):
            raise ValueError('Offre ouverte sans contrôle décrit : '+o['id'])
        for m in o.get('matches',[]):
            if m.get('assessment') not in ('direct','transfer','gap','unknown'):
                raise ValueError('Type de correspondance invalide.')
            for fid in m.get('fact_ids',[]):
                if fid not in confirmed:raise ValueError('Fait non confirmé : '+fid)
        rating=o.get('rating') or {};score=rating.get('score')
        if score is not None:
            if isinstance(score,bool) or not isinstance(score,(int,float)) or not math.isfinite(score) or not 0<=score<=10:
                raise ValueError('Adéquation hors plage /10.')
            components=rating.get('components') or {};weights={'missions':4,'prerequisites':3,'motivation':2,'learning':1}
            if set(components)!=set(weights):raise ValueError('Quatre sous-notes requises.')
            for k,maxi in weights.items():
                n=components[k]
                if isinstance(n,bool) or not isinstance(n,(int,float)) or not math.isfinite(n) or not 0<=n<=maxi:
                    raise ValueError('Sous-note invalide : '+k)
            if abs(sum(components.values())-score)>0.011:raise ValueError('Somme des notes incohérente.')
            if not rating.get('explanation') or not any(m.get('fact_ids') for m in o.get('matches',[])):
                raise ValueError('Note sans explication et faits confirmés.')
            if score>=8 and o.get('blockers'):raise ValueError('Note prioritaire incompatible avec un blocage déclaré.')
        for doc in o.get('documents',[]):
            if doc.get('kind') not in KINDS or not doc.get('label'):
                raise ValueError('Type ou libellé du document invalide.')
            docpath=local_path(root,doc.get('path'))
            if not docpath.is_file():
                raise ValueError('Document absent : '+str(doc.get('path')))
            if doc.get('sha256') and hashlib.sha256(docpath.read_bytes()).hexdigest()!=doc['sha256']:
                raise ValueError('Document modifié sur place : créer une nouvelle version '+doc['path'])
            if any(fid not in confirmed for fid in doc.get('fact_ids',[])):
                raise ValueError('Document appuyé sur un fait non confirmé.')
    return offers


def load_workspace(root):
    root=Path(root).resolve()
    profile,facts,offers,state=[read(root/f) for f in ('profile.json','facts.json','offers.json','state.json')]
    if profile.get('schema_version')!=1 or not profile.get('workspace_id'):
        raise ValueError('Profil de dossier invalide.')
    if state.get('schema_version')!=1 or state.get('workspace_id')!=profile['workspace_id']:
        raise ValueError('Le suivi appartient à un autre dossier.')
    if type(state.get('version')) is not int or state['version']<0 or not isinstance(state.get('items'),dict):
        raise ValueError('État du suivi invalide.')
    if facts.get('schema_version')!=1 or not isinstance(facts.get('facts'),list):
        raise ValueError('Registre de faits invalide.')
    fact_ids=set()
    for fact in facts['facts']:
        if not isinstance(fact,dict) or not isinstance(fact.get('id'),str) or not fact['id'] or fact['id'] in fact_ids:
            raise ValueError('Identifiant de fait absent ou en doublon.')
        if fact.get('status') not in ('confirmed','ambiguous','planned') or not isinstance(fact.get('text'),str) or not fact['text'].strip():
            raise ValueError('Fait incomplet ou état inconnu.')
        if not isinstance(fact.get('source'),str) or not fact['source'].strip():raise ValueError('Source de fait requise.')
        fact_ids.add(fact['id'])
    validate_offers(root,offers,facts)
    ids={o['id'] for o in offers}
    for key,value in state['items'].items():
        if key not in ids or not isinstance(value,dict) or value.get('status') not in STATUSES:
            raise ValueError('État associé à une offre inconnue ou invalide.')
        if any(k in value and (not isinstance(value[k],str) or len(value[k])>20000) for k in ('note','date','sent_files')):
            raise ValueError('Champ texte du suivi invalide.')
        if 'favorite' in value and not isinstance(value['favorite'],bool):raise ValueError('Favori invalide.')
    return profile,facts,offers,state


def initialize(root):
    root=Path(root).resolve()
    if root.exists() and any(root.iterdir()):
        raise ValueError('Initialisation refusée : choisir un dossier vide ou neuf.')
    root.mkdir(parents=True,exist_ok=True)
    profile=read(SKILL/'assets/profile.template.json');profile['workspace_id']=str(uuid.uuid4())
    atomic_json(root/'profile.json',profile)
    atomic_json(root/'facts.json',{'schema_version':1,'facts':[],'open_questions':[]})
    atomic_json(root/'offers.json',[])
    atomic_json(root/'state.json',{'schema_version':1,'workspace_id':profile['workspace_id'],'version':0,'items':{}})
    (root/'documents').mkdir()
    (root/'REPRISE.md').write_text('# Reprise de recherche\n\nProfil à compléter depuis le CV et les réponses du candidat.\nAucune offre vérifiée ni candidature envoyée.\n\nOuvrir index.html ou lancer le serveur local du kit.\n',encoding='utf-8')
    build(root)


def upsert(root, incoming):
    root=Path(root).resolve();profile,facts,old,state=load_workspace(root)
    if not isinstance(incoming,list):raise ValueError('Lot de nouvelles offres : liste requise.')
    result=copy.deepcopy(old);byid={o['id']:o for o in result}
    for new in incoming:
        if new.get('id') in byid:
            o=byid[new['id']];docs={d['path']:d for d in o.get('documents',[])}
            if new.get('company',o['company']).strip().casefold()!=o['company'].strip().casefold():
                raise ValueError('Employeur différent sous une clé existante.')
            if o.get('family') and new.get('family',o['family'])!=o['family']:
                raise ValueError('Famille de métier différente sous une clé existante.')
            if state['items'].get(o['id'],{}).get('status') in {'envoyee','entretien','refus','offre','ecartee','expiree'} and new.get('title',o['title'])!=o['title']:
                raise ValueError('Titre d’une candidature traitée à préserver ; vérifier la référence avant migration.')
            for d in new.get('documents',[]):
                if d['path'] in docs and docs[d['path']].get('sha256'):
                    actual=hashlib.sha256(local_path(root,d['path']).read_bytes()).hexdigest()
                    if actual!=docs[d['path']]['sha256']:raise ValueError('Ancien document remplacé sur place.')
            docs.update({d['path']:d for d in new.get('documents',[])})
            merged={**o,**new,'documents':list(docs.values())}
            if offer_identity(o)!=offer_identity(merged):raise ValueError('Référence modifiée sous une clé existante.')
            result[result.index(o)]=merged;byid[new['id']]=merged
        else:result.append(copy.deepcopy(new));byid[new.get('id')]=result[-1]
    validate_offers(root,result,facts)
    for offer in result:
        for doc in offer.get('documents',[]):
            doc.setdefault('sha256',hashlib.sha256(local_path(root,doc['path']).read_bytes()).hexdigest())
    atomic_json(root/'offers.json',result,backup=True)
    build(root)
    return len(result)-len(old)


def build(root):
    root=Path(root).resolve();profile,facts,offers,state=load_workspace(root)
    payload={'profile':profile,'offers':offers,'state':state}
    # Escape script-closing tags even when untrusted offer text contains markup.
    encoded=json.dumps(payload,ensure_ascii=False,allow_nan=False).replace('<','\\u003c').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    page=(SKILL/'assets/dashboard.html').read_text('utf-8').replace('__STUDIO_PAYLOAD__',encoded)
    (root/'index.html').write_text(page,encoding='utf-8')


class Conflict(ValueError):pass


class StateStore:
    def __init__(self,root):self.root=Path(root).resolve();self.lock=threading.Lock()

    def get(self):
        return read(self.root/'state.json')

    def update(self,payload):
        with self.lock:
            current=self.get()
            if payload.get('workspace_id')!=current['workspace_id']:raise ValueError('Dossier incorrect.')
            if payload.get('expected_version')!=current['version']:raise Conflict('Suivi modifié ailleurs. Exporter les saisies puis recharger avant de réessayer.')
            updates=payload.get('items');ids={o['id'] for o in read(self.root/'offers.json')}
            if not isinstance(updates,dict) or not updates:raise ValueError('Aucune modification reçue.')
            result=copy.deepcopy(current)
            for key,value in updates.items():
                if key not in ids or not isinstance(value,dict):raise ValueError('Offre inconnue.')
                if set(value)-{'status','note','date','favorite','sent_files','updated_at'}:raise ValueError('Champ personnel inconnu.')
                if value.get('status','a_verifier') not in STATUSES:raise ValueError('Statut inconnu.')
                for field in ('note','date','sent_files'):
                    if field in value and (not isinstance(value[field],str) or len(value[field])>20000):raise ValueError('Texte de suivi invalide.')
                if 'favorite' in value and not isinstance(value['favorite'],bool):raise ValueError('Favori invalide.')
                clean={**current['items'].get(key,{}),**value,'updated_at':dt.datetime.now(dt.timezone.utc).isoformat()}
                clean.setdefault('status','a_verifier')
                result['items'][key]=clean
            result['version']+=1
            atomic_json(self.root/'state.json',result,backup=True)
            return result


def make_handler(root,store,port):
    root=Path(root).resolve()
    class Handler(SimpleHTTPRequestHandler):
        def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(root),**kwargs)

        def json_response(self,status,payload):
            data=json.dumps(payload,ensure_ascii=False).encode('utf-8')
            self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)))
            self.end_headers();self.wfile.write(data)

        def allowed_host(self):return self.headers.get('Host') in (f'127.0.0.1:{port}',f'localhost:{port}')

        def do_GET(self):
            if not self.allowed_host():self.send_error(403);return
            route=urlsplit(self.path).path
            if route=='/api/state':self.json_response(200,store.get());return
            rel=unquote(route).lstrip('/') or 'index.html'
            if rel!='index.html' and not rel.startswith('documents/'):
                self.send_error(404);return
            try:path=local_path(root,rel)
            except ValueError:self.send_error(403);return
            if not path.is_file():self.send_error(404);return
            return super().do_GET()

        def do_POST(self):
            origin=self.headers.get('Origin');expected=(f'http://127.0.0.1:{port}',f'http://localhost:{port}')
            if not self.allowed_host() or origin not in expected:
                self.json_response(403,{'error':'Origine locale attendue.'});return
            if self.path!='/api/state':self.json_response(404,{'error':'Route inconnue.'});return
            if self.headers.get_content_type()!='application/json':self.json_response(415,{'error':'JSON requis.'});return
            try:
                length=int(self.headers.get('Content-Length','0'))
                if not 0<length<=LIMIT:raise ValueError('Taille du suivi invalide.')
                result=store.update(json.loads(self.rfile.read(length)))
                self.json_response(200,result)
            except Conflict as exc:self.json_response(409,{'error':str(exc)})
            except (ValueError,TypeError,KeyError) as exc:self.json_response(400,{'error':str(exc)})
    return Handler


def bundle(root,target):
    root=Path(root).resolve();load_workspace(root);target=Path(target).resolve()
    if target.exists():raise ValueError('Archive déjà présente : choisir un nouveau nom.')
    build(root)  # Embed the latest committed state for a fresh file:// browser.
    files=[root/f for f in ('profile.json','facts.json','offers.json','state.json','index.html','REPRISE.md')]
    files+=list((root/'documents').rglob('*'))
    target.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(target,'x',zipfile.ZIP_DEFLATED) as z:
        for p in files:
            if p.is_file():
                if not p.resolve().is_relative_to(root):raise ValueError('Fichier extérieur refusé.')
                z.write(p,p.relative_to(root).as_posix())


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('init','validate','build','upsert','serve','bundle'):
        s=sub.add_parser(name);s.add_argument('workspace',type=Path)
        if name=='upsert':s.add_argument('batch',type=Path)
        if name=='bundle':s.add_argument('output',type=Path)
        if name=='serve':s.add_argument('--port',type=int,default=8781)
    args=p.parse_args();root=args.workspace.resolve()
    try:
        if args.command=='init':initialize(root)
        elif args.command=='validate':
            profile,facts,offers,state=load_workspace(root)
            print(json.dumps({'offers':len(offers),'state_version':state['version'],'workspace':str(root)},ensure_ascii=False));return
        elif args.command=='build':build(root)
        elif args.command=='upsert':print('Nouvelles offres :',upsert(root,read(args.batch)))
        elif args.command=='bundle':bundle(root,args.output)
        elif args.command=='serve':
            build(root)
            if not 1024<=args.port<=65535:raise ValueError('Port attendu entre 1024 et 65535.')
            server=ThreadingHTTPServer(('127.0.0.1',args.port),make_handler(root,StateStore(root),args.port))
            print(f'Interface : http://127.0.0.1:{args.port}/index.html\nSauvegarde disque active. Arrêt : Ctrl+C.',flush=True)
            try:server.serve_forever()
            except KeyboardInterrupt:pass
            finally:server.server_close()
        print('OK :',root)
    except (ValueError,OSError,KeyError,TypeError) as exc:p.exit(1,'Erreur : '+str(exc)+'\n')


if __name__=='__main__':main()
