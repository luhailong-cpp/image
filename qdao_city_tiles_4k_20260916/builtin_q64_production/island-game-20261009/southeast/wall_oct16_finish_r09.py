import os
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
import numpy as np

tid='r09_c10';rev='wall-oct16-v01';q=ROOT/'qa'/f'{tid}-{rev}'
spec=read(ROOT/'wall-oct16-r09c10-v01.spec.json')
proof=read(q/'source-proof.json');candidate=Path(proof['candidate'])
assert sha(candidate)==proof['candidateSha256']
byrc={Path(s['file']).stem.split('_p')[1][:2]:s for s in proof['sources']}
reviewed={}
for f in (ROOT/'qa'/'wall-oct16').glob('r09_c10*-review.json'):
 d=read(f)
 if d.get('status')!='quick_layout_and_edges_passed':continue
 for e in d.get('edges',[]):
  ss=e.get('sources',e.get('source',[]))
  if len(ss)!=2:continue
  if all(sha(Path(s['file']))==s['sha256'] for s in ss):
   reviewed[tuple(sorted(s['sha256'] for s in ss))]={'review':str(f),'reviewSha256':sha(f),'edgeFile':e['file'],'edgeSha256':sha(Path(e['file']))}
seams=read(q/'seams.json');missing=[]
for e in seams['entries']:
 r,c=map(int,e['id'][1:]);other=f'{r}{c+1}' if e['id'][0]=='h' else f'{r+1}{c}'
 key=tuple(sorted([byrc[f'{r}{c}']['sha256'],byrc[other]['sha256']]))
 evidence=reviewed.get(key)
 if evidence:
  assert e['sha256']==evidence['edgeSha256'],e['id']
  e.update(status='passed_actual_pixel_visual_review',evidence=evidence)
 else:missing.append(e['id'])
write(q/'seams.json',seams)
assert not missing,missing
junctions=[{'file':str(f),'sha256':sha(f),'status':'passed_actual_512px_visual_review'} for f in sorted(q.glob('junction_*.png'))]
assert len(junctions)==9
internal={'candidate':str(candidate),'candidateSha256':sha(candidate),'reviewedAt':now(),'reviewer':'wall_oct16','status':'internal_pass','seamCount':24,'junctionCount':9,'seams':str(q/'seams.json'),'junctions':junctions,'sourceReplayMismatch':0,'finding':'Actual newly changed joins h21,h31,v11,v21,v31 and all nine junctions viewed. Remaining joins reuse previously viewed native-core seam images only after both selected-source hashes and exact candidate seam image hashes matched. Wall caps, posts, timber, firecracker tube and foliage connect; no major geometry cut or hard rectangular material boundary observed. Fine paving brush variation retained.','formalAccepted':False}
write(q/'internal-review.json',internal)
external=[]
for direction,name in [('N','r08_c10.candidate-wall-recover-20261013-v02.png'),('E','r09_c11.candidate-v05.png')]:
 nf=ROOT/'tiles'/name;ni=Image.open(nf).convert('RGB');ci=Image.open(candidate).convert('RGB')
 for i in range(4):
  if direction=='N':
   e=Image.new('RGB',(1024,512));e.paste(ni.crop((i*1024,3840,(i+1)*1024,4096)),(0,0));e.paste(ci.crop((i*1024,0,(i+1)*1024,256)),(0,256))
   rc=f'1{i+1}'
  else:
   e=Image.new('RGB',(512,1024));e.paste(ci.crop((3840,i*1024,4096,(i+1)*1024)),(0,0));e.paste(ni.crop((0,i*1024,256,(i+1)*1024)),(256,0))
   rc=f'{i+1}4'
  dest=q/f'external-{direction}{i+1}.png';assert not dest.exists();e.save(dest)
  matches=[v for k,v in reviewed.items() if byrc[rc]['sha256'] in k and v['edgeSha256']==sha(dest)]
  external.append({'direction':direction,'segment':i+1,'file':str(dest),'sha256':sha(dest),'neighbor':str(nf),'neighborSha256':sha(nf),'status':'passed_hash_identical_to_actual_viewed_native_core_join' if matches else 'pending_visual_review','evidence':matches})
write(q/'external-review.json',{'candidate':str(candidate),'candidateSha256':sha(candidate),'reviewedAt':now(),'edges':external,'west':'pending_neighbor_available','south':'pending_neighbor_available','formalAccepted':False})
selected=ROOT/f'selected-native-{tid}-{rev}.json';d=read(selected);d['internalAccepted']=True;d['internalReview']=str(q/'internal-review.json');d['externalReview']=str(q/'external-review.json');write(selected,d)
d=read(ROOT/'progress-wall-oct16.json');d.setdefault('completedCandidates',{})[tid]={'file':str(candidate),'sha256':sha(candidate),'dimensions':[4096,4096],'sourceProof':str(q/'source-proof.json'),'internalAccepted':True,'externalAccepted':False,'formalAccepted':False};write(ROOT/'progress-wall-oct16.json',d)
print(json.dumps({'internal':'passed','externalPending':[f"{x['direction']}{x['segment']}" for x in external if x['status']=='pending_visual_review'],'candidateSha256':sha(candidate)}))
