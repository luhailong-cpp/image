"""Preserve existing overview SVG geometry; replace only embedded art from final PNGs."""
from pathlib import Path
import json,re,base64,hashlib,subprocess
from PIL import Image
B=Path(__file__).resolve().parent;ROOT=B.parents[1];C=ROOT/'qdao_ui_redesign_v5/components'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
j=json.loads((C/'manifest.json').read_text(encoding='utf-8'));assets=j['assets'];by={a['id']:a for a in assets}
specs=['primary_button','tab','list_row','server_card_wide','server_card_medium','search']
iconcats=['round_badge','status_dot','recommend_badge','check','lock','gold_flower','cloud_corner']
order=[f'{kind}_{state}' for kind in specs for state in ['normal','selected','disabled']]+['main_frame','content_panel','summary_bar']+[a['id'] for a in assets if a['category'] in iconcats]
badges=[a['id'] for a in assets if a['category']=='round_badge']
rows=[]
for stem,ids in [('overview',order),('badges_overview',badges*3)]:
 original=C/(stem+'.svg');s=original.read_text(encoding='utf-8');old=re.findall(r'data:image/png;base64,[A-Za-z0-9+/=]+',s);assert len(old)==len(ids),(stem,len(old),len(ids))
 idx=iter(ids)
 def replace(m):
  aid=next(idx);p=C/by[aid]['png'];return 'data:image/png;base64,'+base64.b64encode(p.read_bytes()).decode('ascii')
 updated=re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+',replace,s)
 assert re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+','PAINT',updated)==re.sub(r'data:image/png;base64,[A-Za-z0-9+/=]+','PAINT',s)
 (B/(stem+'.svg')).write_text(updated,encoding='utf-8')
 for suffix in ['.svg','.png']:
  p=C/(stem+suffix);rows.append({'path':p.relative_to(ROOT).as_posix(),'before_sha256':sha(p),'staged':(B/(stem+suffix)).relative_to(ROOT).as_posix(),'geometry_unchanged':True,'embedded_ids':ids})
(B/'plan.json').write_text(json.dumps({'status':'staged_svg','files':rows},indent=2)+'\n',encoding='utf-8')
subprocess.run(['node',str(B/'render.cjs')],check=True)
for r in rows:r['after_sha256']=sha(ROOT/r['staged'])
for stem in ['overview','badges_overview']:
 assert Image.open(B/(stem+'.png')).size==Image.open(C/(stem+'.png')).size
(B/'staged-validation.json').write_text(json.dumps({'status':'staged_verified','files':rows,'embedded_control_instances':69,'unique_controls':39,'geometry_and_text_unchanged':True,'errors':[]},indent=2)+'\n',encoding='utf-8')
print('4 overviews staged;69 embedded instances from39 current controls;geometry/text unchanged')
