from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;T=D.parents[2];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
Q=D/'whole-qa';Q.mkdir(exist_ok=True);assert not any(Q.iterdir())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
plan=read(T/'plan.json');candidate=D/'bounded/p24-east-proposal.png';north=T/'native/p14.png';east=Path(plan['eastCandidate']);p=ar(candidate);n=ar(north);e=ar(east)
context=np.zeros_like(p);known=np.zeros((1254,1254),bool);context[:230]=n[1024:1254];known[:230]=True;context[:,1139:]=e[909:2163,:115];known[:,1139:]=True
assert np.array_equal(p[known],context[known])
layout=engine.base.Layout();owner=engine.owner_mask(known,['top','right'],layout);preview,flow,tone,stats=engine.register_native(context,p,known,owner,['top','right'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
identical=np.array_equal(p,preview);delta=np.abs(preview.astype(int)-p.astype(int));changed=np.any(delta>0,axis=2)
pp=Q/'p24-production-replay.png';Image.fromarray(preview).save(pp);operation=dict(kind='original multi_edge register_native replay with actual N230 and E115',engine=ref(R/'tools/multi_edge/engine.py'),baseEngine=ref(R/'native_assemble.py'),options=dict(max_shift=6,tone_cap=18,return_depth=256),statistics=stats,proposalPixelsIdentical=identical,maxReplayRGBDelta=int(delta.max()),changedPixelCount=int(changed.sum()),knownSupportExact=True,canonicalUnchanged=True)
write(str(pp)+'.generation.json',dict(**ref(pp),derivedFrom=[ref(candidate),ref(north),ref(east)],operation=operation,actualModel=None,actualQuality=None,nativeScale=1,actuallyViewed=False))
joint=Image.new('RGB',(1299,1766));joint.paste(Image.open(north).convert('RGB').crop((0,512,1254,1254)),(0,0));joint.paste(Image.fromarray(preview),(0,512));joint.paste(Image.open(east).convert('RGB').crop((0,397,160,2163)),(1139,0));jp=Q/'joint-context.png';joint.save(jp)
write(str(jp)+'.generation.json',dict(**ref(jp),derivedFrom=[ref(pp),ref(north),ref(east)],operation=dict(globalFrameXYWH=[43917,37261,1299,1766],pastes=[dict(source=str(north),cropLTRB=[0,512,1254,1254],pasteXY=[0,0]),dict(source=str(pp),cropLTRB=[0,0,1254,1254],pasteXY=[0,512]),dict(source=str(east),cropLTRB=[0,397,160,2163],pasteXY=[1139,0])]),nativeScale=1,actuallyViewed=False))
boxes=[('qa-north-owner',[0,467,1254,787]),('qa-north-support-return',[0,582,1254,902]),('qa-east',[979,512,1299,1766]),('qa-northeast-corner',[979,467,1299,907]),('qa-south-local-return',[0,1094,1254,1414]),('qa-left-stone',[0,690,320,1240]),('qa-east-local-return',[880,800,1200,1766])]
for name,box in boxes:
 q=Q/(name+'.png');joint.crop(box).save(q);write(str(q)+'.generation.json',dict(**ref(q),source=ref(jp),cropLTRB=box,nativeScale=1,actuallyViewed=False))
write(Q/'replay.json',dict(proposal=ref(candidate),plan=ref(T/'plan.json'),canonical=ref(T/'native/p24.png'),north=ref(north),east=ref(east),operation=operation,approvedForPromotion=False,formalAccepted=False))
print(json.dumps(dict(proposal=ref(candidate),replayRecord=ref(Q/'replay.json'),productionReplayIdentical=identical,maxReplayRGBDelta=int(delta.max()),changedPixelCount=int(changed.sum()),statistics=stats)))
