"""Generate synthetic demonstration data, never using a local installed brain."""
import json,os,pathlib,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
DEMO=pathlib.Path(tempfile.mkdtemp(prefix='altair-portfolio-demo-'))
topics={
 'engineering':['architecture','contracts','retrieval','routing','versioning','observability'],
 'research':['sources','evidence','hypotheses','experiments','validation','synthesis'],
 'editorial':['brief','outline','draft','revision','provenance','publication']}
colors=['#22d3ee','#a78bfa','#34d399']
def write(rel,text):
 p=DEMO/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')
write('brain.json',json.dumps({'schema_version':1,'nome':'Synthetic portfolio demo','motore':(ROOT/'VERSION').read_text().strip(),'training':None}))
write('areas.json',json.dumps({'schema_version':1,'areas':[{'id':a,'label':a.title(),'status':'active','keywords':[a],'colore':colors[i]} for i,a in enumerate(topics)]}))
provenance=[]
for area,names in topics.items():
 for i,name in enumerate(names):
  refs=' '.join('[['+n+']]' for n in names if n!=name)
  front='---\narea: '+area+'\nsource: synthetic demonstration\n---\n'
  write(f'raw/{area}/{name}.md',front+f'# {name.title()}\n\nSynthetic portfolio example for the {area} workflow.\n\n## Inputs\nDocument assumptions and source material.\n\n## Decision\nCompare alternatives and keep supporting evidence.\n\n## Connections\n'+refs+'\n')
  write(f'wiki/{area}/{name}.md',front+f'# {name.title()}\n\nDemonstration summary, not personal knowledge.\n\n## Workflow\n'+refs+'\n')
  provenance.append({'wiki':f'wiki/{area}/{name}.md','fonti':[f'raw/{area}/{name}.md']})
# Use same file anchors as the real provenance pipeline.
write('engine/provenance.json',json.dumps({'schema_version':1,'ancoraggi_area':[],'mappe_dirette':provenance}))
write('engine/bridges.json',json.dumps({'schema_version':1,'bridges':[
 {'concetto':'evidence-led design','from':{'area':'engineering','page':'contracts'},'to':{'area':'research','page':'validation'}},
 {'concetto':'traceable publication','from':{'area':'research','page':'sources'},'to':{'area':'editorial','page':'provenance'}},
 {'concetto':'review process','from':{'area':'engineering','page':'versioning'},'to':{'area':'editorial','page':'revision'}}]}))
write('engine/lessons.jsonl','')
env={**os.environ,'ALTAIR_BRAIN':str(DEMO),'PYTHONIOENCODING':'utf-8'}
for tool in ['extract_graph','graph_prune','apply_bridges','apply_provenance','sync_extended_view','build_area_graphs','altair_compact_view','build_atlas_view','build_views_index','build_search_index']:
 p=subprocess.run([sys.executable,str(ROOT/'tools'/f'{tool}.py')],env=env,cwd=ROOT,capture_output=True,text=True,encoding='utf8')
 if p.returncode: print(p.stdout,p.stderr);sys.exit(p.returncode)
g=json.loads((DEMO/'graphify-out/graph.json').read_text())
(ROOT/'output/playwright/demo.json').write_text(json.dumps({'path':str(DEMO),'nodes':len(g['nodes']),'edges':len(g['links']),'areas':len(topics),'notes':18},indent=2),encoding='utf8')
print(DEMO)
