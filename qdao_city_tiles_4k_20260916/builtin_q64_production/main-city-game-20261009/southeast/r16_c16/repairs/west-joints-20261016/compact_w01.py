from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
R=Path(__file__).resolve().parent;D=R/'W01-v1';O=D/'compact-mask-v2';O.mkdir(exist_ok=False)
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':str(p),'sha256':sha(p)}
P=read(D/'preparation.json');B=Image.open(P['sources']['child']['path']).convert('RGB');N=Image.open(D/'native.png').convert('RGB')
region=[0,0,340,280];nc=[400,200,740,480];alpha=np.full((280,340),255,dtype=np.uint8)
for i in range(16):
 val=round((i+1)*255/17);alpha[:,-i-1]=np.minimum(alpha[:,-i-1],val);alpha[-i-1,:]=np.minimum(alpha[-i-1,:],val)
A=alpha.astype(np.uint32)[:,:,None];old=np.asarray(B.crop(region)).astype(np.uint32);new=np.asarray(N.crop(nc)).astype(np.uint32);piece=((new*A+old*(255-A)+127)//255).astype(np.uint8);B.paste(Image.fromarray(piece),(0,0))
Image.fromarray(alpha).save(O/'alpha.png');B.save(O/'trial-core-4096.png')
target=Image.open(D/'target-native-1254.png').convert('RGB');target.paste(B.crop(region),(400,200));target.save(O/'trial-real-neighbor-1254.png')
north=Image.open(P['sources']['north']['path']).convert('RGB');J=Image.new('RGB',(850,400));J.paste(north.crop((0,3896,850,4096)),(0,0));J.paste(B.crop((0,0,850,200)),(0,200));J.save(O/'north-join-after.png')
B.crop((260,0,420,360)).save(O/'right-boundary.png');B.crop((0,200,420,380)).save(O/'lower-boundary.png')
original=np.asarray(Image.open(P['sources']['child']['path']).convert('RGB'));cur=np.asarray(B);allowed=np.zeros((4096,4096),bool);allowed[:280,:340]=True;assert not np.any(np.any(cur!=original,axis=2)&~allowed)
M={'tile':'r16_c16','repair':'W01-v1-compact-mask-v2','status':'trial_not_selected_pending_root_visual_review','base':P['sources']['child'],'native':ref(D/'native.png'),'receipt':ref(D/'receipt.json'),'preparation':ref(D/'preparation.json'),'nativeCrop':nc,'tilePlacement':region,'alpha':ref(O/'alpha.png'),'formula':'uint8((new_uint32*alpha_uint32 + old_uint32*(255-alpha_uint32)+127)//255)','alphaPurpose':'Restrict imported native pixels to actual closed coping and cast shadow; 16px right/bottom alpha transition. No generated-detail claim for alpha operation.','candidate':ref(O/'trial-core-4096.png'),'realNeighborPreview':ref(O/'trial-real-neighbor-1254.png'),'resize':False,'warp':False,'colorCorrection':False,'formalAccepted':False,'actualModel':None};(O/'composition.json').write_text(json.dumps(M,indent=2),encoding='utf-8')
replay=Image.open(P['sources']['child']['path']).convert('RGB');replay.paste(Image.fromarray(((new*A+old*(255-A)+127)//255).astype(np.uint8)),(0,0));assert np.array_equal(np.asarray(replay),cur)
(O/'replay-verification.json').write_text(json.dumps({'composition':ref(O/'composition.json'),'verifiedCandidate':M['candidate'],'pixelReplayExact':True,'outsideMaskPixelIdentical':True,'allChildX340AndBeyondUnchanged':True,'noSelectionChanged':True,'formalAccepted':False},indent=2),encoding='utf-8')
print(json.dumps({'candidate':M['candidate'],'composition':ref(O/'composition.json'),'replay':ref(O/'replay-verification.json')}))
