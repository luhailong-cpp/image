from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,shutil,numpy as np
from datetime import datetime,timezone
Q=Path(__file__).resolve().parent;Z=Q.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf-8')
source=Path('C:/Users/luyua/.codex/generated_images/01a14301-2056-7ca3-a69d-e1681f4f28d4/exec-6524dcb5-7590-4a81-ac9e-cee73b8fadeb.png')
raw=Q/'window-joint-v1-raw.png';assert not raw.exists();shutil.copy2(source,raw)
inp=json.loads((Q/'joint-input-v1.json').read_text());frame=inp['frameGlobalBox']
a=np.array(Image.open(raw).convert('RGB'));base=np.array(Image.open(inp['image']).convert('RGB'));assert a.shape==base.shape==(1254,1254,3)
poly=[(617,535),(897,584),(897,1100),(598,989),(598,556)]
maskim=Image.new('1',(1254,1254));ImageDraw.Draw(maskim).polygon(poly,fill=1);mask=np.array(maskim,dtype=bool)
Image.fromarray((mask*255).astype('uint8')).save(Q/'window-joint-v1-binary-mask.png')
joint=base.copy();joint[mask]=a[mask];Image.fromarray(joint).save(Q/'window-joint-v1-exact-candidate.png')
proof=[]
for tile,t in inp['targetPatches'].items():
 p=Path(t['file']);assert sha(p)==t['sha256'];orig=np.array(Image.open(p).convert('RGB'));out=orig.copy();pid=t['patch']
 ox=(int(tile[5:7])-1)*4096+(int(pid[2])-1)*1024-115
 oy=(int(tile[1:3])-1)*4096+(int(pid[1])-1)*1024-115
 yy,xx=np.where(mask);gx=xx+frame[0];gy=yy+frame[1]
 # Replace only actual selected core ownership, never halo-only pixels.
 use=(gx>=ox+115)&(gx<ox+1139)&(gy>=oy+115)&(gy<oy+1139)
 sx=xx[use];sy=yy[use];dx=gx[use]-ox;dy=gy[use]-oy
 out[dy,dx]=a[sy,sx]
 pm=np.zeros((1254,1254),bool);pm[dy,dx]=True
 assert np.array_equal(out[~pm],orig[~pm]) and np.array_equal(out[dy,dx],a[sy,sx])
 dest=Q/(tile+'-'+pid+'-window-joint-v1-candidate.png');Image.fromarray(out).save(dest)
 proof.append({'tile':tile,'patch':pid,'source':str(p),'sourceSha256':sha(p),'sourceNativeOrigin':[ox,oy],'candidate':str(dest),'candidateSha256':sha(dest),'maskPixels':int(pm.sum()),'actuallyChangedPixels':int(np.any(out!=orig,axis=2).sum()),'outsideMaskPixelExact':True,'insideMaskSameCoordinateNativeRawPixelExact':True,'haloUnchanged':True})
 # Re-assemble edited cores into a complete joint to prove both candidates jointly match.
 coreRegion=(max(frame[0],ox+115),max(frame[1],oy+115),min(frame[2],ox+1139),min(frame[3],oy+1139))
 x0,y0,x1,y1=coreRegion
 assert np.array_equal(out[y0-oy:y1-oy,x0-ox:x1-ox],joint[y0-frame[1]:y1-frame[1],x0-frame[0]:x1-frame[0]])
boxes={'window-with-perimeter':[535,480,962,1164],'north-perimeter':[535,485,962,650],'south-perimeter':[535,934,962,1160],'west-perimeter':[550,500,670,1140],'east-perimeter':[838,500,958,1140],'actual-shared-seam':[550,671,950,927]}
evidence=[]
for name,b in boxes.items():
 p=Q/(name+'-v1-100pct.png');Image.fromarray(joint).crop(b).save(p);evidence.append({'file':str(p),'sha256':sha(p),'frameBox':b,'resized':False,'visualReview':'pending'})
write(raw.with_suffix('.png.generation.json'),{'source':str(source),'sourceSha256':sha(source),'rawSha256':sha(raw),'route':'builtin image_gen__imagegen','actualModel':None,'actualQuality':None,'dimensions':[1254,1254],'request':str(Q/'window-joint-v1.request.json'),'receipt':str(Q/'window-joint-v1.receipt.json')})
write(Q/'window-joint-v1-proof.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'frameGlobalBox':frame,'raw':str(raw),'rawSha256':sha(raw),'inputSha256':sha(inp['image']),'maskPolygonFrameCoordinates':poly,'binaryMask':str(Q/'window-joint-v1-binary-mask.png'),'binaryMaskSha256':sha(Q/'window-joint-v1-binary-mask.png'),'jointCandidate':str(Q/'window-joint-v1-exact-candidate.png'),'jointCandidateSha256':sha(Q/'window-joint-v1-exact-candidate.png'),'proof':proof,'evidence':evidence,'canonicalModified':False,'noResampling':True,'noWarp':True,'noBlend':True,'noBlur':True,'formalAccepted':False})
print(json.dumps({'proof':proof,'evidenceCount':len(evidence)}))
