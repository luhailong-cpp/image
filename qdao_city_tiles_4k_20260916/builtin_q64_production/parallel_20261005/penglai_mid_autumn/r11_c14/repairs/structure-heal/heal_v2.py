from pathlib import Path
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image
from datetime import datetime,timezone
P=Path(__file__).resolve().parent; F=P.parents[1]; R=F/'references'
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def derived(im,p,sources,op):
 assert not p.exists();im.save(p);write(str(p)+'.generation.json',dict(**ref(p),createdAt=now(),derivedFrom=[ref(q) for q in sources],operation=op,productionPixels=False,nativeDetailCount=0))
def prepare():
 structure=R/'structure.png';anchor=R/'night-edit-target.png'
 assert sha(structure)=='7f71e214187a11eb40564a941df9d30354858c979413c846c70f27ccf5ecf553'
 a=np.array(Image.open(structure).convert('RGB'));old=np.array(Image.open(anchor).convert('RGB'))
 a[:85,:1170,:]=old[:85,:1170,:];a[:1170,:85,:]=old[:1170,:85,:]
 base=P/'fixed-anchor-base-v2.png';derived(Image.fromarray(a),base,[structure,anchor],dict(kind='restore actual planning-scale N/W/NW anchor pixels',fixedWholePixelRegion='N y<85,x<1170; W x<85,y<1170; NW included; outside-neighbor halo uses original structure',exactFrameGlobalXYWH=[52928,40640,4736,4736],planningScale=1254/4736))
 y,x=np.mgrid[:1254,:1254]
 hole=((x>=85)&(x<205)&(y>=85)&(y<1254))|((y>=85)&(y<190)&(x>=85)&(x<1254))
 rgba=np.concatenate([a,np.full((1254,1254,1),255,dtype=np.uint8)],axis=2);rgba[hole]=[255,255,255,0]
 target=P/'l-band-edit-target-v2.png';derived(Image.fromarray(rgba),target,[base],dict(kind='AI input transparent narrow current-side L mask; hidden RGB white',maskRectanglesLTRB=[[85,85,205,1254],[85,85,1254,190]],noPaintedReplacementGeometry=True))
 prompt='''Edit only Image 1, a 1254 x 1254 fixed-frame game-map planning image. Fill the transparent WHITE narrow L-shaped missing band with matching finished artwork. Return one opaque 1254-square image. Preserve every existing object position, crop, scale and illumination outside the holes. The image represents EXACT global frame [52928,40640,4736,4736]. Do not zoom, recenter, rotate or rearrange the scene.
The first 85 pixels of the TOP and LEFT are IMMUTABLE actual neighboring night artwork, including the true northwest corner. At their inner edges, CONTINUE each real contour, blue water cell, white rim, gold reflection, plank, hull edge, mast and rope into the missing current-side band. x85 and y85 are arbitrary tile cuts, NOT straight object boundaries. There must be no straight lighting step, rectangular patch, vertical sheet of water, or horizontal collage line. Paint large natural water cells across these cuts into the unchanged cobalt water interior, maintaining the current bright blue and warm gold color balance.
At the middle LEFT, the pale lavender quay coping and stone wall coming from the actual west must have a believable small terminal return, continuing just far enough into the missing band to close its real shape naturally beside the boat. Follow the real west stone thickness, sloping coping and lit edges; do not terminate it at a straight tile cut. Do not create a long new quay or wall across the open water. Continue the boat rim entering from the lower-left at exactly its current height, slope and thickness into the preserved boat. At the TOP, round wooden dock posts arriving from the north must remain cylindrical with curved round ends and rounded rope collars, not become square blocks at the cut. Continue the cream sail and spar exactly where they already cross the band. Keep the broad cream sail, single mast and existing ropes, hull footprint, all benches and current open water.
Image 2 shows the actual NORTH neighbor for continuity only. Image 3 shows the actual WEST neighbor for continuity only. Neither is the target frame. Image 4 is approved painted STYLE ONLY; no UI, lettering, icons or other content from it. Use polished rounded Daoist chibi material rendering, clean golden edge light, saturated cobalt water with organized broad blue ripples. Do not add new boats, posts, sails, quays, lanterns, people, decoration, sky, moon, horizon, border or text. Exact geometry and color outside the small holes must remain unchanged. Avoid blur, noise, sharpened halos and oversaturated new highlights.'''
 pp=P/'heal-v2.prompt.txt';pp.write_text(prompt,encoding='utf-8')
 refs=[target,R/'north-context-preview.png',R/'west-context-preview.png',Path('D:/work/image/designs/gameplay-ui/04-guild.png')]
 call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
 write(P/'heal-v2.call.json',call);write(P/'heal-v2.request.json',dict(preparedAt=now(),notSubmittedYet=True,submittedParameters=dict(model=None,quality=None,**call),configSnapshot=read(str(structure)+'.generation.json')['configSnapshot'],references=[ref(p) for p in refs],prompt=ref(pp),base=ref(base),originalStructure=ref(structure),productionPixels=False,nativeDetailCount=0,planUnchanged=True))
 print(P/'heal-v2.call.json')
def save(src):
 src=Path(src);dst=P/'heal-v2-source.png';assert not dst.exists();assert Image.open(src).size==(1254,1254)
 req=read(P/'heal-v2.request.json')
 for q in req['references']:assert sha(q['file'])==q['sha256']
 shutil.copy2(src,dst)
 write(str(dst)+'.generation.json',dict(**ref(dst),generatedAt=now(),tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Builtin host does not expose actual model/quality selectors or returned values.',prompt=req['prompt'],references=req['references'],evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),sourceUpscaled=False,resizedAfterGeneration=False,productionPixels=False,nativeDetailCount=0))
 write(P/'heal-v2.submission-completion.json',dict(submitted=True,completedAt=now(),request=ref(P/'heal-v2.request.json'),source=ref(dst),call=ref(P/'heal-v2.call.json'),actualModel=None,actualQuality=None))
 print(json.dumps(ref(dst)))
def proposal():
 base=P/'fixed-anchor-base-v2.png';source=P/'heal-v2-source.png';a=np.array(Image.open(base).convert('RGB'));b=np.array(Image.open(source).convert('RGB'));y,x=np.mgrid[:1254,:1254]
 smooth=lambda t: np.clip(t,0,1)**2*(3-2*np.clip(t,0,1))
 left=smooth((205-x)/30)*((x>=85)&(y>=85)&(y<1254))
 top=smooth((190-y)/30)*((y>=85)&(x>=85)&(x<1254))
 alpha=np.maximum(left,top);out=np.rint(a*(1-alpha[:,:,None])+b*alpha[:,:,None]).astype('uint8');assert np.array_equal(out[:85],a[:85]);assert np.array_equal(out[:,:85],a[:,:85])
 mask=P/'proposal-v2-selection-mask.png';derived(Image.fromarray(np.rint(alpha*255).astype('uint8')),mask,[base,source],dict(kind='current-side L selection with 30 pixel smooth return; no warp or tone; exact fixed neighbor pixels'))
 dst=P/'structure-proposal-v2.png';derived(Image.fromarray(out),dst,[base,source,mask],dict(kind='select only AI-generated narrow L geometry into existing planning frame',flow=0,tone=0,neighborPixelsUnchanged=True,notCanonical=True))
 qa=P/'qa-v2';qa.mkdir(exist_ok=True);im=Image.fromarray(out);items=[]
 boxes={'north-join':[0,0,1254,250],'west-join':[0,0,250,1254],'northwest-corner':[0,0,330,330],'west-wall-detail':[0,360,300,840],'north-post-detail':[475,0,665,250],'west-boat-detail':[0,685,320,1010]}
 for name,box in boxes.items():
  p=qa/(name+'.png');derived(im.crop(box),p,[dst],dict(kind='actual 1:1 crop of planning proposal; NOT native game production',cropLTRB=box,scale=1));items.append(dict(**ref(p),cropLTRB=box,actuallyViewed=False))
 diff=np.any(out!=a,axis=2);ys,xs=np.where(diff)
 write(P/'proposal-v2.json',dict(createdAt=now(),candidate=ref(dst),source=ref(source),base=ref(base),mask=ref(mask),changedBBox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],fixedNandWPlanningPixelsUnchanged=True,flow=0,tone=0,actualModel=None,actualQuality=None,productionPixels=False,nativeDetailCount=0,canonicalStructureUnchanged=ref(R/'structure.png'),planUnchanged=ref(F/'plan.json'),qa=items,reviewPending=True))
 print(json.dumps(ref(dst)))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare()
 elif sys.argv[1]=='save':save(sys.argv[2])
 elif sys.argv[1]=='proposal':proposal()

