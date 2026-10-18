from pathlib import Path
from PIL import Image,ImageDraw
from datetime import datetime,timezone
import numpy as np,json,hashlib,sys,shutil
Q=Path(__file__).resolve().parent;Z=Q.parents[2]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,indent=2),encoding='utf-8')
v=sys.argv[1];source=Path(sys.argv[2]);raw=Q/f'jamb-{v}-raw.png';assert not raw.exists();shutil.copy2(source,raw)
inp=json.loads((Q/'jamb-input-v1.json').read_text());frame=inp['frameGlobalBox'];a=np.array(Image.open(raw).convert('RGB'));base=np.array(Image.open(inp['image']).convert('RGB'));assert a.shape==base.shape==(1254,1254,3)
box=[900,620,1004,1040];mask=np.zeros((1254,1254),bool);mask[box[1]:box[3],box[0]:box[2]]=True
polygon=None
if v in ('v1-surface','v1-surface-v2'):
 polygon=[(900,620),(1003,620),(1003,1207),(956,1221),(951,1221),(900,1200)]
 mi=Image.new('1',(1254,1254));ImageDraw.Draw(mi).polygon(polygon,fill=1);mask=np.array(mi,dtype=bool);box=[900,620,1004,1222]
trim_polygon=None
if v=='v1-surface-v2':
 trim_polygon=[(1008,500),(1022,505),(1022,1225),(1015,1214),(1008,1209)]
 ImageDraw.Draw(mi).polygon(trim_polygon,fill=1);mask=np.array(mi,dtype=bool);box=[900,500,1023,1226]
maskfile=Q/f'jamb-{v}-binary-mask.png';Image.fromarray((mask*255).astype('uint8')).save(maskfile)
joint=base.copy();joint[mask]=a[mask];jointfile=Q/f'jamb-{v}-exact-joint-candidate.png';Image.fromarray(joint).save(jointfile)
proof=[]
for tile,t in inp['targetPatches'].items():
 p=Path(t['file']);assert sha(p)==t['sha256'];sel=json.loads(Path(t['selection']).read_text(encoding='utf-8-sig'));assert (Z/tile/sel['patches'][t['patch']]).resolve()==p.resolve()
 old=np.array(Image.open(p).convert('RGB'));out=old.copy();pid=t['patch'];ox=(int(tile[5:7])-1)*4096+(int(pid[2])-1)*1024-115;oy=(int(tile[1:3])-1)*4096+(int(pid[1])-1)*1024-115
 yy,xx=np.where(mask);gx,gy=xx+frame[0],yy+frame[1];u=(gx>=ox+115)&(gx<ox+1139)&(gy>=oy+115)&(gy<oy+1139)
 sx,sy=xx[u],yy[u];dx,dy=gx[u]-ox,gy[u]-oy;pm=np.zeros((1254,1254),bool);pm[dy,dx]=True;out[dy,dx]=a[sy,sx]
 assert np.array_equal(out[~pm],old[~pm]);assert np.array_equal(out[dy,dx],a[sy,sx]);halo=np.ones_like(pm);halo[115:1139,115:1139]=False;assert np.array_equal(out[halo],old[halo])
 dest=Q/f'{tile}-{pid}-jamb-{v}-candidate.png';Image.fromarray(out).save(dest)
 proof.append({'tile':tile,'patch':pid,'source':str(p),'sourceSha256':sha(p),'sourceNativeOrigin':[ox,oy],'candidate':str(dest),'candidateSha256':sha(dest),'maskPixels':int(pm.sum()),'changedPixels':int(np.any(out!=old,axis=2).sum()),'outsideMaskPixelExact':True,'insideMaskSameCoordinateRawPixelExact':True,'haloUnchanged':True})
evidence=[]
boxes={'post-with-perimeter':[860,560,1045,1100],'top-perimeter':[860,570,1045,690],'bottom-perimeter':[860,970,1045,1090],'left-perimeter':[850,570,930,1090],'right-perimeter':[974,570,1054,1090],'actual-shared-seam':[860,711,1045,887],'window-protection':[570,520,1018,1110]}
if v in ('v1-surface','v1-surface-v2'):boxes.update({'post-with-perimeter':[860,560,1045,1254],'bottom-perimeter':[860,1140,1045,1254],'left-perimeter':[850,570,930,1240],'right-perimeter':[974,570,1054,1240]})
if v=='v1-surface-v2':boxes.update({'trim-full-perimeter':[992,475,1036,1254],'trim-top-perimeter':[992,475,1036,560],'trim-bottom-perimeter':[992,1170,1036,1254]})
for name,b in boxes.items():
 p=Q/f'{name}-{v}-100pct.png';Image.fromarray(joint).crop(b).save(p);evidence.append({'file':str(p),'sha256':sha(p),'frameBox':b,'resized':False,'visualReview':'pending'})
generation_version='v1' if v in ('v1-surface','v1-surface-v2') else v
write(raw.with_suffix('.png.generation.json'),{'source':str(source),'sourceSha256':sha(source),'rawSha256':sha(raw),'route':'builtin image_gen__imagegen','actualModel':None,'actualQuality':None,'dimensions':[1254,1254],'request':str(Q/f'jamb-{generation_version}.request.json'),'receipt':str(Q/f'jamb-{generation_version}.receipt.json'),'generationVersion':generation_version,'extractionVersion':v})
write(Q/f'jamb-{v}-proof.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'frameGlobalBox':frame,'raw':str(raw),'rawSha256':sha(raw),'input':inp['image'],'inputSha256':sha(inp['image']),'binaryMask':str(maskfile),'binaryMaskSha256':sha(maskfile),'maskFrameBox':box,'maskPolygonFrameCoordinates':polygon,'additionalTrimPolygonFrameCoordinates':trim_polygon,'generationVersion':generation_version,'extractionVersion':v,'jointCandidate':str(jointfile),'jointCandidateSha256':sha(jointfile),'patches':proof,'evidence':evidence,'canonicalModified':False,'noResampling':True,'noBlur':True,'noBlend':True,'noWarp':True,'formalAccepted':False})
print(json.dumps({'patches':proof,'evidenceCount':len(evidence)}))
