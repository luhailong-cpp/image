from pathlib import Path
import sys,json,numpy as np
from datetime import datetime,timezone
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;R=T/'repairs';sys.path.insert(0,str(T));import helper as h
p=h.p;O=R/'shared-output-v7';state=p.read(R/'shared-boundary-state.json');items=[]
for k,s in state.items():
 base=Path(s['file']);assert p.sha(base)==s['sha256'],(k,'base modified')
 candidate=O/f'{k}-candidate.png';old=np.asarray(Image.open(base).convert('RGB'));new=np.asarray(Image.open(candidate).convert('RGB'));assert old.shape==new.shape==(4096,4096,3)
 mask=np.any(new!=old,axis=2);mp=O/f'{k}-exact-delta-mask.png';im=Image.fromarray(mask.astype('uint8')*255);im.save(mp);bb=list(im.getbbox());p.derived(mp,[base,candidate],{'method':'exact nonzero pixel difference; binary, no feather','globalOriginXY':s['origin']})
 replay=old.copy();replay[mask]=new[mask];assert np.array_equal(replay,new)
 if k=='r09_c12':assert not mask[:3469].any() and not mask[:,627:].any()
 if k=='r10_c12':assert not mask[:,627:].any()
 items.append({'tile':k,'base':str(base),'baseSha256':s['sha256'],'replacement':str(candidate),'candidate':str(candidate),'sha256':p.sha(candidate),'mask':str(mp),'maskSha256':p.sha(mp),'maskBBoxLTRB':bb,'changedPixels':int(mask.sum()),'globalOriginXY':s['origin'],'globalBBoxLTRB':[s['origin'][0]+bb[0],s['origin'][1]+bb[1],s['origin'][0]+bb[2],s['origin'][1]+bb[3]],'exactReplayVerified':True,'dimensions':[4096,4096]})
raw=T/'tiles/r10_c11-candidate.png';candidate=O/'r10_c11-candidate.png';m=np.any(np.asarray(Image.open(raw))!=np.asarray(Image.open(candidate)),axis=2);mp=O/'r10_c11-exact-delta-vs-raw-mask.png';im=Image.fromarray(m.astype('uint8')*255);im.save(mp);p.derived(mp,[raw,candidate],{'method':'exact final changes versus raw16core composition'});rawEntry={'base':str(raw),'baseSha256':p.sha(raw),'replacement':str(candidate),'mask':str(mp),'maskSha256':p.sha(mp),'maskBBoxLTRB':list(im.getbbox()),'globalOriginXY':[40960,36864],'changedPixels':int(m.sum())}
native=[]
for d in [T/'native',R/'native',R/'north-joint/native',R/'east-joint/native',R/'corner-joint/native']:
 for f in sorted(d.glob('*.png')):
  rec=Path(str(f)+'.generation.json');j=p.read(rec);assert p.sha(f)==j['sha256'];assert Image.open(f).size==(1254,1254)
  src=Path(j['toolResultPath']);assert src.exists() and p.sha(src)==j['sha256']
  assert j['actualModel'] is None and j['actualQuality'] is None
  for ref in j['references']:assert Path(ref['file']).exists() and p.sha(ref['file'])==ref['sha256'],str(ref)
  native.append({'file':str(f),'sha256':j['sha256'],'record':str(rec),'sourceVerified':True,'actualModel':None,'actualQuality':None})
review={'nativeScale':True,'internalLines':[str(T/'qa'/f'shared-v7-{axis}{v}.png') for axis in ['x','y'] for v in [1024,2048,3072]],'junctions':str(T/'qa/shared-v7-junctions.png'),'sharedEdges':[str(O/f'{axis}-s{i}-review.png') for axis in ['north','east'] for i in range(1,5)],'corner':str(O/'corner-review.png'),'returnBoards':[str(R/'shared-output-v4/corner-edges-native.png'),str(R/'shared-output-v4/leaf-edges-native.png'),str(R/'shared-output-v6/right-return-edges.png'),str(O/'cliff-return-edges.png')],'findings':['North guide seam through wood/foliage/wall/water and eastern split wooden post redrawn with native AI and exact ownership masks.','Fourtile water junction redrawn together; shared-edge and corner outputs reviewed at native1254 scale.','Additional previously missed internal L-shaped canopy and cliff material discontinuities were found during return QA and repaired in stages4-7; prior internal-v2 completion wording is superseded.','Final six-line and nine-junction review found no disconnected major contour or unresolved straight panel cut in reviewed regions. Natural changes in painterly strokes remain.','r09_c12 changes restricted to left627 and last627 rows; no overlap with root rightmost627 bottom repair.','West/south external edges and other regional corners remain outside this delegated acceptance scope.']}
j={'status':'local_native_qa_complete_ready_for_masked_region_merge','createdAt':datetime.now(timezone.utc).isoformat(),'owner':'repair_southeast','sourceState':str(R/'shared-boundary-state.json'),'entries':items,'r10_c11AgainstRaw':rawEntry,'nativeSources':native,'nativeSourceCount':len(native),'sharedRepairSourceCount':sum('/native/' in x['file'].replace(chr(92),'/') and '-joint/' in x['file'].replace(chr(92),'/') for x in native),'stageRecords':[str(R/f'shared-output-v{i}/record.json') for i in range(1,8)],'nativePatchPixels':[1254,1254],'coreCropLTRB':[115,115,1139,1139],'processing':{'geometry':'AI redrawing and binary source ownership only','resampling':False,'geometricWarp':False,'imageBlur':False,'imageFeather':False,'colourFields':'bounded RGB low-frequency fields; real field arrays retained with each patch'},'review':review,'formalAccepted':False,'clientAccepted':False,'wholeCityComplete':False,'mergeInstruction':'Apply replacement only where its exact delta mask is255, after checking overlap against current region. Do not replace whole neighbor tiles. r10_c11AgainstRaw additionally includes earlier internal-v2 repairs.'}
p.write(R/'handoff-shared-v7.json',j)
print(json.dumps({'manifest':str(R/'handoff-shared-v7.json'),'nativeSources':len(native),'sharedRepairSources':j['sharedRepairSourceCount'],'entries':[{k:e[k] for k in ['tile','sha256','maskBBoxLTRB','changedPixels']} for e in items]},indent=2))

