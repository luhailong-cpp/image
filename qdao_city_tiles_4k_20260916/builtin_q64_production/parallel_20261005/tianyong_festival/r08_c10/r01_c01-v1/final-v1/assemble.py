"""Source-preserving crop repair and <=1px registration of existing contours."""
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,json,hashlib,sys
from PIL import Image
P=Path(__file__).resolve().parent;D=P.parent;T=D.parent.parent
ROOT=next(p for p in D.parents if (p/'config/image-generation.json').exists())
sys.path.insert(0,str(ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor'))
import cv2
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ref=lambda p:{'file':str(p),'sha256':sha(p)}
write=lambda p,v:Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
smo=lambda z:np.clip(z,0,1)**2*(3-2*np.clip(z,0,1))
n=np.array(Image.open(D/'native.png').convert('RGB'))
repair=np.array(Image.open(D/'repair-v2/native.png').convert('RGB'))
c=np.array(Image.open(D/'context.png').convert('RGBA'))
assert n.shape==repair.shape==(1254,1254,3)
yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
# AI repair is only adopted within the requested upper structural change.
# Existing native edges outside the region are restored exactly.
rm=smo((xx-230)/40)*smo((930-xx)/40)*smo((yy-100)/40)*smo((900-yy)/40)
base=np.clip(np.rint(n*(1-rm[:,:,None])+repair*rm[:,:,None]),0,255).astype(np.uint8)
Image.fromarray(base).save(P/'repair-composite.png')
Image.fromarray(np.rint(rm*255).astype(np.uint8)).save(P/'repair-mask.png')
assert np.array_equal(base[:,1024:],n[:,1024:]) and np.array_equal(base[:,:115],n[:,:115])
# Reliable left corner displacement is0,-1px, lower corner0,0. Long diagonal
# edge NCC shifts are aperture-ambiguous and not used. Right corners are0,0.
left_ramp=1-smo((xx-115)/300)
right_ramp=smo((xx-660)/364)
dyp=np.interp(np.arange(1254),[0,115,180,250,320,900,1080,1160,1253],[0,-1,-1,-1,0,0,0,-1,-1]).astype(np.float32)
dyp=cv2.GaussianBlur(dyp[:,None],(1,0),sigmaX=0,sigmaY=16)[:,0]
dyp=np.clip(dyp,-1,0)
dx=np.zeros_like(xx);dy=dyp[:,None]*left_ramp
flow=np.stack([dx,dy],2).astype(np.float32)
aligned=cv2.remap(base,xx+dx,yy+dy,cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
known=c[:,:,3]==255
delta=c[:,:,:3].astype(np.float32)-aligned.astype(np.float32)
tone=np.zeros_like(delta)
for side,ramp in [('left',left_ramp),('right',right_ramp)]:
 km=known & ((xx<115) if side=='left' else (xx>=1024))
 diff=delta.copy();diff[~km]=0
 norm=cv2.GaussianBlur(km.astype(np.float32),(0,0),20)
 field=cv2.GaussianBlur(diff,(0,0),20)/np.maximum(norm[:,:,None],.001)
 if side=='left':
  field[:,115:]=field[:,114:115]
  field[:115]=field[115:116]
  field[:115]*=smo(yy[:115]/115)[:,:,None]
 else:field[:,:1024]=field[:,1024:1025]
 tone+=np.clip(field,-12,12)*ramp[:,:,None]
assert np.abs(tone).max()<=12.00001
corrected=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
alpha=np.ones_like(xx)
alpha[known&(xx<115)]=smo((xx-35)/80)[known&(xx<115)]
alpha[known&(xx>=1024)]=(1-smo((xx-1024)/80))[known&(xx>=1024)]
j=np.clip(np.rint(corrected*alpha[:,:,None]+c[:,:,:3]*(1-alpha[:,:,None])),0,255).astype(np.uint8)
assert np.array_equal(j[115:,:35],c[115:,:35,:3])
assert np.array_equal(j[:,1104:],c[:,1104:,:3])
Image.fromarray(j).save(P/'joined.png');Image.fromarray(np.rint(alpha*255).astype(np.uint8)).save(P/'mask.png')
np.save(P/'flow.npy',flow);np.save(P/'tone.npy',tone)
qa=[]
for name,box in [('left-full',[0,115,370,1254]),('right-full',[820,0,1254,1254]),('left-upper',[0,115,370,460]),('left-lower',[0,940,420,1254]),('right-upper',[820,0,1254,330]),('right-junction',[850,380,1254,780]),('right-cloud',[820,760,1254,1254]),('repair-upper',[210,80,970,690]),('top-full',[0,0,1254,200]),('bottom-full',[0,1030,1254,1254])]:
 Image.fromarray(j).crop(box).save(P/(name+'.png'))
 qa.append({**ref(P/(name+'.png')),'cropLTRB':box,'operation':'Exact native crop, no resize','derivedFrom':[ref(P/'joined.png')]})
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'Adopt AI structural repair only inside soft rectangular repair mask, restore all outer native pixels, then limited1px vertical registration and <=12 tone matching; exact source-preserving context returns.','source':[ref(D/'native.png'),ref(D/'repair-v2/native.png'),ref(D/'context.png')],'sourceRecords':[ref(D/'native.png.generation.json'),ref(D/'repair-v2/native.png.generation.json')],'output':ref(P/'joined.png'),'repairComposite':ref(P/'repair-composite.png'),'repairMask':ref(P/'repair-mask.png'),'repairAdoptionBoundsLTRB':[230,100,930,900],'repairFullyAdoptedBoundsLTRB':[270,140,890,860],'windowTileLocalLTRB':[-115,-115,1139,1139],'windowGlobalLTRB':[36749,28557,38003,29811],'nativePixels':[1254,1254],'nativeScale':1,'maximumAllowedShiftXY':[1,1],'actualMaxShiftXY':np.abs(flow).max(axis=(0,1)).tolist(),'maximumAllowedTone':12,'actualMaxToneRGB':np.abs(tone).max(axis=(0,1)).tolist(),'maxAdjacentFieldChangeAcrossX':np.abs(np.diff(flow,axis=1)).max(axis=(0,1)).tolist(),'maxAdjacentFieldChangeAcrossY':np.abs(np.diff(flow,axis=0)).max(axis=(0,1)).tolist(),'knownContextPreserved':{'left':{'joinedLTRB':[0,115,35,1254],'exact':True},'right':{'joinedLTRB':[1104,0,1254,1254],'exact':True}},'fields':[ref(P/f) for f in ['flow.npy','tone.npy','mask.png','repair-mask.png']],'resampling':'OpenCV INTER_CUBIC within same1254x1254; no enlargement. AI edit merged through saved mask.','qa':qa,'script':ref(Path(__file__)),'newModelCalls':0,'actualModel':None,'actualQuality':None,'formalAccepted':False,'localVisualAccepted':False}
write(P/'assembly.json',record)
for name in ['joined.png','repair-composite.png','repair-mask.png','mask.png']:
 write(P/(name+'.generation.json'),{'file':str(P/name),'sha256':sha(P/name),'derivedFrom':record['source'],'operation':record['operation'] if name=='joined.png' else 'Deterministic source selection / mask; see assembly','assembly':ref(P/'assembly.json'),'newModelCalls':0,'actualModel':None,'actualQuality':None,'nativeScale':1})
write(P/'qa-crops.json',qa)
print(json.dumps({'joined':ref(P/'joined.png'),'maxShift':record['actualMaxShiftXY'],'maxTone':record['actualMaxToneRGB']}))
