// Node built-ins only; no browser permission or network request is used.
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('assert');
const template=fs.readFileSync(path.join(__dirname,'../assets/dashboard.html'),'utf8');
const app=template.match(/<\/script><script>([\s\S]*?)<\/script>/)[1].replace(/boot\(\);\s*$/,'');
const offers=Object.keys({a_verifier:1,a_faire:1,envoyee:1,entretien:1,refus:1,offre:1,ecartee:1,expiree:1}).map((s,i)=>({id:'DEMO-'+i,company:'Entreprise fictive '+i,title:'Stage fictif '+i,url:'https://example.com/'+i,summary:'<script>unsafe</script>',family:'Famille fictive',rating:{score:i===0?null:8,explanation:'Fictif'},documents:i===0?[{label:'CV fictif',kind:'cv',path:'documents/cv.txt'}]:[]}));
const states=Object.fromEntries(['a_verifier','a_faire','envoyee','entretien','refus','offre','ecartee','expiree'].map((s,i)=>['DEMO-'+i,{status:s,note:'original'}]));
const payload={profile:{workspace_id:'fictitious-user',candidate:{name:'Candidat fictif'}},offers,state:{schema_version:1,workspace_id:'fictitious-user',version:0,items:states}};
const nodes={};function node(id){return nodes[id]??={value:'',checked:false,textContent:'',innerHTML:'',addEventListener(){}};}
node('payload').textContent=JSON.stringify(payload);node('sort').value='priority';
let stored,visible=[];
const ctx={document:{getElementById:node,querySelectorAll:()=>visible,createElement:()=>({click(){}})},location:{protocol:'file:',hostname:''},URL,Blob,structuredClone,setTimeout,console,localStorage:{getItem:()=>null,setItem:(k,v)=>{stored=v;}},confirm:()=>false};
vm.createContext(ctx);vm.runInContext(app,ctx);const run=s=>vm.runInContext(s,ctx);
assert.equal(run('filtered().length'),8);run('render()');assert.equal((nodes.cards.innerHTML.match(/class="offer"/g)||[]).length,8);
assert(!nodes.cards.innerHTML.includes('<script>unsafe</script>'));assert(nodes.cards.innerHTML.includes('&lt;script&gt;unsafe&lt;/script&gt;'));
assert.equal((nodes.cards.innerHTML.match(/>CV fictif<\/a>/g)||[]).length,1);assert(!nodes.cards.innerHTML.includes('>Lettre'));
nodes.status.value='envoyee';assert.equal(run('filtered().length'),1);nodes.status.value='expiree';assert.equal(run('filtered().length'),1);
nodes.status.value='';nodes.minimum.value='8';assert.equal(run('filtered().length'),7);nodes.minimum.value='';nodes.q.value='DEMO';assert.equal(run('filtered().length'),8);nodes.q.value='';
assert.equal(run('safeURL("javascript:alert(1)")'),'');assert.equal(run('docURL("../private")'),'');assert.equal(run('docURL("C:/secret")'),'');
run('drafts["DEMO-7"]={status:"expiree",note:"brouillon sur une autre page"};render()');assert.equal(run('drafts["DEMO-7"].note'),'brouillon sur une autre page');
visible=[{dataset:{id:'DEMO-2'},querySelectorAll:()=>[{dataset:{field:'status'},value:'envoyee',type:'select'},{dataset:{field:'note'},value:'Saisie non enregistrée',type:'textarea'},{dataset:{field:'sent_files'},value:'CV v1',type:'text'}]}];
run('render()');visible=[];nodes.family.value='Autre famille';run('render()');assert.equal(run('snapshot().items["DEMO-2"].note'),'Saisie non enregistrée');nodes.family.value='';
assert.throws(()=>run('checkImport({schema_version:1,workspace_id:"another-user",items:{}})'));
(async()=>{
 await run('persist({"DEMO-0":{status:"envoyee",note:"new"}})');assert(stored);assert.equal(JSON.parse(stored).items['DEMO-1'].note,'original');assert.equal(run('state.items["DEMO-0"].note'),'new');
 const before=run('JSON.stringify(state)');ctx.localStorage.setItem=()=>{throw Error('Quota refusé');};
 await assert.rejects(()=>run('persist({"DEMO-0":{status:"expiree",note:"lost"}})'));assert.equal(run('JSON.stringify(state)'),before);
 const old=structuredClone(payload.state);old.items['DEMO-0'].status='a_verifier';ctx.localStorage.getItem=()=>JSON.stringify(old);run('D.state.version=5;D.state.items["DEMO-0"].status="envoyee"');await run('boot()');assert.equal(run('ready'),false);assert.equal(nodes['storage-choice'].hidden,false);assert.equal(run('branches.page.items["DEMO-0"].status'),'envoyee');assert.equal(run('branches.browser.items["DEMO-0"].status'),'a_verifier');
 ctx.localStorage.setItem=(k,v)=>stored=v;run('chooseBranch("page")');assert.equal(run('ready'),true);assert.equal(run('state.items["DEMO-0"].status'),'envoyee');assert.equal(JSON.parse(stored).version,5);
 console.log('Interface : 8 statuts visibles, filtres, liens conditionnels, protection du HTML, refus inter-candidats et échec de sauvegarde sans perte contrôlés.');
})().catch(e=>{console.error(e);process.exitCode=1;});
