from pathlib import Path
import sys,json,shutil,numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parent.parent;sys.path.insert(0,str(R/'repairs/internal'));import quilt as q
I=R/'repairs/internal';src=I/'r11_c14-internal-candidate-v3.png';raw=R/'tiles/r11_c14-candidate.png'
a=np.asarray(Image.open(src));b=np.asarray(Image.open(raw));m=np.any(a!=b,axis=2);mp=I/'internal-v3-actual-diff-mask.png';Image.fromarray((m*255).astype('uint8')).save(mp);q.record(mp,[src,raw],{'method':'exact binary changed-pixel mask; copy candidate where255, preserve base elsewhere'})
(I/'handoff-internal-v3.json').write_text(json.dumps({'base':str(raw),'baseSha256':q.sha(raw),'candidate':str(src),'sha256':q.sha(src),'actualDiffMask':str(mp),'maskSha256':q.sha(mp),'changedPixels':int(m.sum()),'protectedTopCorners627Verified':True,'visualQA':'six full seams, nine junctions, all ten native1254 AI contexts and batten return inspected; no visible remaining assembly break; outer guide band delegated to shared edges','formalAccepted':False},indent=2),encoding='utf8')
sources={}
for nm in ['nw','ne']:
 st=json.loads((R/'repairs/external-root'/f'{nm}-corner-state.json').read_text(encoding='utf8'));sources.update(st['sources'])
for k,v in sources.items():assert q.sha(v['file'])==v['sha256']
ims={k:Image.open(v['file']).convert('RGB') for k,v in sources.items()};ims['r11_c14']=Image.open(src).convert('RGB')
ops=[]
for nm in ['nw','ne']:
 st=json.loads((R/'repairs/external-root'/f'{nm}-corner-state.json').read_text(encoding='utf8'));cp=R/'repairs/external-root'/f'{nm}-corner-composite-v1.png';co=Image.open(cp).convert('RGB')
 for i,k in enumerate(st['order']):
  cx=(i%2)*627;cy=(i//2)*627;tx=3469 if i%2==0 else 0;ty=3469 if i//2==0 else 0
  ims[k].paste(co.crop((cx,cy,cx+627,cy+627)),(tx,ty));ops.append({'corner':str(cp),'sha256':q.sha(cp),'tile':k,'sourceBox':[cx,cy,cx+627,cy+627],'dest':[tx,ty]})
for k,im in ims.items():
 p=O/(k+'-corner-base.png');im.save(p);q.record(p,[Path(sources[k]['file'])]+([src] if k=='r11_c14' else [])+[Path(v['corner']) for v in ops if v['tile']==k],{'method':'paste already-composited627 quadrants without repeat alpha','operations':[v for v in ops if v['tile']==k],'noResampling':True})
(O/'state-v1.json').write_text(json.dumps({'originalSources':sources,'internal':{'file':str(src),'sha256':q.sha(src)},'cornerOperations':ops,'current':{k:str(O/(k+'-corner-base.png')) for k in ims}},indent=2),encoding='utf8')
shutil.copy2(I/'ai_helper.py',O/'ai_helper.py')
print('corner bases and internal handoff complete')

