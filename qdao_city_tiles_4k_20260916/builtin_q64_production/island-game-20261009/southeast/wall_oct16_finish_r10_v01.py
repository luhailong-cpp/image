import os
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
tid='r10_c10';rev='wall-oct16-v01';q=ROOT/'qa'/f'{tid}-{rev}'
proof=read(q/'source-proof.json');candidate=Path(proof['candidate'])
assert sha(candidate)==proof['candidateSha256']
failed={'h13':'Paving joint stops at p13 east endpoint; two local repairs exhausted, retain best v03.','h21':'Lower paving joint stops at p22 west boundary.','h31':'Upper paving joint starts at p32 west boundary.','h32':'Middle paving joint terminates at p32 east boundary.','h33':'Two paving joints terminate at p33 east boundary.','h42':'Paving joint terminates at p42 east boundary.','v24':'Post corner and inset frame shift sideways at24/34 join; v04 repair failed and regressed east, retain34v03.','v33':'Paving joint terminates at33/43 join.'}
edges=[]
for f in (ROOT/'qa'/'wall-oct16').glob('r10_c10*-review.json'):
 d=read(f)
 for e in d.get('edges',[]):
  if all(sha(Path(s['file']))==s['sha256'] for s in e['sources']):
   edges.append((f,e))
seams=read(q/'seams.json')
for e in seams['entries']:
 matches=[(f,x) for f,x in edges if x['sha256']==e['sha256']]
 assert matches,e['id']
 e.update(status='not_passed' if e['id'] in failed else 'passed_actual_native_core_join_visual_review',note=failed.get(e['id'],'Actual native core join inspected; exact seam pixels match reviewed evidence.'),evidence=[{'file':str(f),'fileSha256':sha(f),'edgeFile':x['file'],'edgeSha256':x['sha256'],'sources':x['sources']} for f,x in matches],reviewedAt=now())
write(q/'seams.json',seams)
js=[]
for f in sorted(q.glob('junction_*.png')):
 bad=f.stem in ['junction_13','junction_21','junction_23']
 js.append({'file':str(f),'sha256':sha(f),'status':'not_passed_known_adjoining_seam' if bad else 'passed_actual_512px_visual_review','note':'All nine actual native-pixel junctions viewed. Failed locations coincide with recorded adjacent seam endpoints.'})
write(q/'internal-review.json',{'candidate':str(candidate),'candidateSha256':sha(candidate),'reviewedAt':now(),'reviewer':'wall_oct16','status':'not_passed','seamCount':24,'passedSeams':16,'notPassedSeams':failed,'junctions':js,'sourceReplayMismatch':0,'formalAccepted':False})
ex=[]
for direction,name in [('N','r09_c10.candidate-wall-oct16-v01.png'),('E','r10_c11.candidate-v04.png')]:
 nf=ROOT/'tiles'/name;ni=Image.open(nf).convert('RGB');ci=Image.open(candidate).convert('RGB')
 for i in range(4):
  if direction=='N':
   im=Image.new('RGB',(1024,512));im.paste(ni.crop((i*1024,3840,(i+1)*1024,4096)),(0,0));im.paste(ci.crop((i*1024,0,(i+1)*1024,256)),(0,256))
  else:
   im=Image.new('RGB',(512,1024));im.paste(ci.crop((3840,i*1024,4096,(i+1)*1024)),(0,0));im.paste(ni.crop((0,i*1024,256,(i+1)*1024)),(256,0))
  f=q/f'external-{direction}{i+1}.png';assert not f.exists();im.save(f)
  matches=[(rf,e) for rf,e in edges if e['sha256']==sha(f)]
  assert matches,(direction,i+1)
  ex.append({'direction':direction,'segment':i+1,'file':str(f),'sha256':sha(f),'neighbor':str(nf),'neighborSha256':sha(nf),'status':'passed_exact_hash_reuse_of_actual_reviewed_join','evidence':[{'review':str(rf),'edgeFile':e['file'],'sources':e['sources']} for rf,e in matches]})
write(q/'external-review.json',{'candidate':str(candidate),'candidateSha256':sha(candidate),'northEastStatus':'passed','edges':ex,'west':'pending_neighbor_available','south':'pending_neighbor_available','formalAccepted':False})
s=ROOT/f'selected-native-{tid}-{rev}.json';d=read(s);d.update(internalAccepted=False,externalAccepted=False,internalReview=str(q/'internal-review.json'),externalReview=str(q/'external-review.json'));write(s,d)
d=read(ROOT/'progress-wall-oct16.json');d.setdefault('completedCandidates',{})[tid]={'file':str(candidate),'sha256':sha(candidate),'dimensions':[4096,4096],'sourceProof':str(q/'source-proof.json'),'internalAccepted':False,'externalAccepted':False,'formalAccepted':False,'notPassedSeams':list(failed)};write(ROOT/'progress-wall-oct16.json',d)
print(json.dumps({'candidateSha256':sha(candidate),'internal':'not_passed','passedSeams':16,'notPassedSeams':list(failed),'externalNorthEast':'passed_hash_reuse','formalAccepted':False}))

