from pathlib import Path
from PIL import Image
import numpy as np,hashlib,json,sys,datetime
R=Path(__file__).resolve().parent;key=sys.argv[1];D=R/key
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
def write(p,j):assert not p.exists();p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
def png(p,im):assert not p.exists();im.save(p)
P=read(D/'preparation.json');N=Image.open(D/'native.png');assert N.format=='PNG' and N.size==(1254,1254)
assert 'A' not in N.getbands() or N.getextrema()[-1]==(255,255)
src=Path(sys.argv[2]);assert sha(src)==sha(D/'native.png')
write(D/'receipt.json',{'tool':'image_gen.imagegen','route':'builtin','originalOutputPath':str(src),'originalSha256':sha(src),'saved':ref(D/'native.png'),'size':[1254,1254],'actualModel':None,'actualQuality':None,'resized':False,'recordedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()})
B=Image.open(P['sources']['child']['path']).convert('RGB');original=np.asarray(B).copy();target=Image.open(D/'target-native-1254.png').convert('RGB')
x0,y0,x1,y1=P['editRegionInChildCoordinates'];bx,by,_,_=P['cropBoxInChildCoordinates'];crop=[x0-bx,y0-by,x1-bx,y1-by]
a=np.full((y1-y0,x1-x0),255,dtype=np.uint8)
for i in range(3):
 v=round((i+1)*255/4)
 if x0>0:a[:,i]=np.minimum(a[:,i],v)
 a[:,-i-1]=np.minimum(a[:,-i-1],v)
 if y0>0:a[i,:]=np.minimum(a[i,:],v)
 a[-i-1,:]=np.minimum(a[-i-1,:],v)
old=np.asarray(B.crop((x0,y0,x1,y1))).astype(np.uint32);new=np.asarray(N.convert('RGB').crop(crop)).astype(np.uint32);A=a.astype(np.uint32)[:,:,None]
piece=((new*A+old*(255-A)+127)//255).astype(np.uint8);B.paste(Image.fromarray(piece),(x0,y0))
png(D/'alpha.png',Image.fromarray(a));png(D/'trial-core-4096.png',B)
target.paste(B.crop((x0,y0,x1,y1)),(x0-bx,y0-by));png(D/'trial-real-neighbor-1254.png',target)
current=np.asarray(B);mask=np.zeros((4096,4096),bool);mask[y0:y1,x0:x1]=True
assert not np.any(np.any(current!=original,axis=2)&~mask)
assert np.array_equal(original[:,650:],current[:,650:])
assert np.array_equal(original[:,:],np.asarray(Image.open(P['sources']['child']['path']).convert('RGB')))
if key.startswith('W01'):
 north=Image.open(P['sources']['north']['path']).convert('RGB');join=Image.new('RGB',(850,400));join.paste(north.crop((0,3896,850,4096)),(0,0));join.paste(B.crop((0,0,850,200)),(0,200));png(D/'north-join-after.png',join)
for name,box in [('right-boundary',[max(0,x1-100),max(0,y0-50),min(4096,x1+100),min(4096,y1+50)]),('lower-boundary',[x0,max(0,y1-120),min(4096,x1+100),min(4096,y1+120)]),('upper-boundary',[x0,max(0,y0-120),min(4096,x1+100),min(4096,y0+120)])]:png(D/(name+'.png'),B.crop(box))
out={'tile':'r16_c16','repair':key,'status':'trial_not_selected_pending_visual_qa','base':P['sources']['child'],'native':ref(D/'native.png'),'receipt':ref(D/'receipt.json'),'preparation':ref(D/'preparation.json'),'nativeCrop':crop,'tilePlacement':[x0,y0,x1,y1],'alpha':ref(D/'alpha.png'),'formula':'uint8((new_uint32*alpha_uint32 + old_uint32*(255-alpha_uint32)+127)//255)','candidate':ref(D/'trial-core-4096.png'),'realNeighborPreview':ref(D/'trial-real-neighbor-1254.png'),'resize':False,'warp':False,'colorCorrection':False,'entireChildOutsideMaskUnchanged':True,'childX650AndBeyondUnchanged':True,'neighborsNotModified':True,'formalAccepted':False,'actualModel':None}
write(D/'composition.json',out)
replay=Image.open(out['base']['path']).convert('RGB');replay.paste(Image.fromarray(((new*A+old*(255-A)+127)//255).astype(np.uint8)),(x0,y0));assert np.array_equal(np.asarray(replay),current)
write(D/'replay-verification.json',{'composition':ref(D/'composition.json'),'verifiedCandidateSha256':sha(D/'trial-core-4096.png'),'pixelReplayExact':True,'changedPixelsOnlyInsideMask':True,'allSourcesPreserved':True,'noSelectionChanged':True,'formalAccepted':False})
print(json.dumps({'key':key,'candidate':out['candidate'],'manifest':ref(D/'composition.json'),'replay':ref(D/'replay-verification.json')}))
