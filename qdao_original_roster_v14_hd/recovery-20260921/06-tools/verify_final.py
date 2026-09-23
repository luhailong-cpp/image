"""Verify only the shipped files, without a dependency on discarded working images."""
from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
FINAL=Path(__file__).resolve().parent.parent/'06-final'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
m=read(FINAL/'manifest.json');rows=m['files'];assert len(rows)==136;restored=m.get('legacy_final_copies_ai_restored',False)
keys={r['path'] for r in rows};dirs=['N','NE','E','SE','S','SW','W','NW']
assert keys=={*[f'walk/{d}/{n:02}.png' for d in dirs for n in range(1,17)],*[f'idle/{d}.png' for d in dirs]}
assert len({r['sha256'] for r in rows})==136
heights={};areas={}
for r in rows:
 p=FINAL/'runtime'/r['path'];assert sha(p)==r['sha256']
 im=Image.open(p);assert im.mode=='RGBA' and list(im.size)==r['size']
 a=np.array(im)[:,:,3];assert a.max()==255 and a.min()==0
 assert not any(np.any(x) for x in (a[0],a[-1],a[:,0],a[:,-1]))
 assert im.size==((512,512) if not restored and r['path'].startswith(('walk/S/','idle/')) else (1024,1024))
 y,x=np.where(a>8);h=int(y.max()-y.min()+1);axis=float(np.median(x[y<int(y.min())+max(1,int((h-1)*.42))]))
 assert abs(axis-im.width/2)<=.5 and int(y.max())==(942 if im.width==1024 else 471)
 heights[r['path']]=h*1024/im.width;areas[r['path']]=float(np.sqrt(np.count_nonzero(a[:,im.width//4:3*im.width//4])/(im.width*im.width)))
base=read(FINAL/'provenance/preserved-old-byte-baseline.json')
for r in base:
 p=Path(r['path']);k='idle/'+p.name if p.parent.name=='idle' else 'walk/S/'+p.name
 assert sha(Path(r['path']) if restored else FINAL/'runtime'/k)==r['sha256']
prov=read(FINAL/'provenance/selected-sources.json')
new=[r for r in prov if r['final_size']==[1024,1024]]
assert len(new)==(136 if restored else 112) and len({r['processing_record']['source']['sha256'] for r in new})==len(new)
assert all(min(r['processing_record']['source']['native_size'])>=1024 for r in new)
assert all(r['processing_record']['common_scale']==.88 for r in new)
direction_geometry={}
for d in dirs:
 hs=[heights[f'walk/{d}/{n:02}.png'] for n in range(1,17)];ar=[areas[f'walk/{d}/{n:02}.png'] for n in range(1,17)]
 cv=float(np.std(ar)/np.mean(ar));drift=abs(heights[f'idle/{d}.png']/float(np.mean(hs))-1)
 assert cv<=.08 and drift<=.08
 direction_geometry[d]={'body_scale_cv':cv,'subject_height_mean':float(np.mean(hs)),'idle_walk_height_drift':drift}
cross_ratio=max(r['subject_height_mean'] for r in direction_geometry.values())/min(r['subject_height_mean'] for r in direction_geometry.values())
assert cross_ratio<=1.10
for r in m['gif_checks']:
 p=FINAL/r['path'];assert sha(p)==r['sha256'];im=Image.open(p);assert im.n_frames==16
 durations=[]
 for n in range(16):im.seek(n);durations.append(im.info['duration'])
 assert durations==[30]*16
assert len(m['gif_checks'])==16
for d in dirs:
 for mode in ['light','dark']:
  assert (FINAL/f'preview/{d}-contact-{mode}.png').exists()
  assert (FINAL/f'preview/{d}-seam15-16-01-02-{mode}.png').exists()
report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'manifest_sha256':sha(FINAL/'manifest.json'),'walk':128,'idle':8,'unique_pngs':136,'new_native_single_sources':len(new),'final_1024_outputs':len(new),'legacy_final_copies_ai_restored':restored,'preserved_original_old_512_bytes':24,'transparent_boundary_touches':0,'direction_geometry':direction_geometry,'cross_direction_mean_height_ratio':cross_ratio,'gif_count':16,'gif_frames':16,'frame_ms':30,'cycle_ms':480,'all_checks_passed':True,'scope':'file contract and provenance only; see REVIEW.md for offline visual findings','unity_client_tested':False}
(FINAL/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report))
