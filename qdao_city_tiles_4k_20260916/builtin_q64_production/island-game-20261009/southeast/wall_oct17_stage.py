import os,sys,subprocess
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
def record(key,status,note):
 p=ROOT/'qa'/'wall-oct16'/('r10_c10_ov_'+key)/'review.json';d=read(p)
 for e in d['entries']:assert sha(Path(e['file']))==e['sha256']
 d.update(status=status,note=note,reviewedAt=now(),reviewer='wall_oct17');write(p,d)
if sys.argv[1]=='select':
 pid,v,status,note=sys.argv[2:];f=ROOT/'native'/f'{pid}_{v}.png';assert Image.open(f).size==(1254,1254)
 d=read(ROOT/'progress-wall-oct16.json');d['selected'][pid]={'version':v,'file':str(f),'sha256':sha(f),'status':status,'note':note,'reviewedAt':now()};d['updatedAt']=now();write(ROOT/'progress-wall-oct16.json',d)
 q=ROOT/'qa'/'wall-oct17'/f'{pid}-{v}-review.json';d=read(q)
 for e in d['edges']:
  assert sha(Path(e['file']))==e['sha256']
  for s in e['sources']:assert sha(Path(s['file']))==s['sha256']
  e['status']=status
 d.update(status=status,note=note,reviewedAt=now(),reviewer='wall_oct17');write(q,d);print(pid,status)
elif sys.argv[1]=='stage':
 record('h21h31_v01','passed_local_repair','Both original lower h21 and upper h31 paving terminations now connected. Native target and all four actual source insertion edges viewed; geometry and material connect.')
 record('h42_v02','not_passed_deferred_after_two_repairs','Upper partial paving now complete, but right replacement boundary at x256 in right.png has a new diagonal joint offset near y250. v01 retained as best local improvement, not adopted into candidate because its upper incomplete joint remains. Keep original selected base for now; continue independent missing work.')
 spec=read(ROOT/'wall-oct16-r10c10-v01.spec.json'); entries=[]
 for key in ['v24_v01','h21h31_v01']:
  m=read(ROOT/'prompts'/('r10_c10_ov_'+key+'.overlay.json'));f=ROOT/'native'/('r10_c10_ov_'+key+'.png')
  entries.append({'file':str(f),'sha256':sha(f),'sourceCrop':m['coreCrop'],'destinationBox':m['destinationBox'],'review':str(ROOT/'qa'/'wall-oct16'/('r10_c10_ov_'+key)/'review.json')})
 mf=ROOT/'adopted-overlay-r10_c10-wall-oct17-v02.json';write(mf,{'tile':'r10_c10','overlays':entries,'formalAccepted':False});spec['overlayManifests']=[str(mf)]
 sp=ROOT/'wall-oct17-r10c10-v02.spec.json';write(sp,spec)
 subprocess.run([sys.executable,str(ROOT/'assemble_native_overlay_candidate_20261012.py'),str(sp),'wall-oct17-v02'],check=True)
elif sys.argv[1]=='layout':
 tid=sys.argv[2];tile=next(t for t in read(ROOT/'coordinate-plan.json')['tiles'] if t['id']==tid);ref=Path(read(ROOT/'references.json')[0]['file']); im=Image.open(ref)
 box=[n*1254/57344 for n in tile['coreGlobalBox']];out=ROOT/'guides'/f'{tid}.tile-layout-wall17.png';assert not out.exists()
 im.transform((1024,1024),Image.Transform.EXTENT,tuple(box),Image.Resampling.BICUBIC).save(out);print(out)
