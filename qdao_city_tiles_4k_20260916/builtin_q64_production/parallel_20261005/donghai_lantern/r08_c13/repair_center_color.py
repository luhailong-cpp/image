from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
T=ROOT/'r08_c13';R=T/'repairs/west-center-color-final';OUT=T/'completed-candidate-v2'
SOURCE=T/'completed-candidate/output/pair-r08_c12-c13.png'
EXPECTED='1e4e4a3da27413bcc76a244ff2d8e5b795d3adc7e2ed3f396f6e46dfed4d3a10'
CROP=[3469,1440,4723,2694];ROI=[3990,1900,4220,2220]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def ref(p):return {'file':str(p),'sha256':sha(p)}
def save(p,im,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);im.save(p);i={**ref(p),'width':im.width,'height':im.height,**d};write(str(p)+'.generation.json',i);return i
def prepare():
 assert sha(SOURCE)==EXPECTED
 src=Image.open(SOURCE).convert('RGB');f=save(R/'festival-target.png',src.crop(CROP),{'operation':'exact native crop','derivedFrom':[ref(SOURCE)],'pairCropXYXY':CROP,'resized':False})
 day=ROOT.parent/'donghai_day/tiles';a=day/'r08_c12.png';b=day/'r08_c13.png';d=Image.new('RGB',(8192,4096));d.paste(Image.open(a),(0,0));d.paste(Image.open(b),(4096,0))
 g=save(R/'day-geometry.png',d.crop(CROP),{'operation':'exact native DAY pair crop; source has historical paving defect outside color ROI','derivedFrom':[ref(a),ref(b)],'pairCropXYXY':CROP,'resized':False})
 style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
 refs=[{**f,'role':'edit target; latest festival pair with approved continuous paving geometry'},{**g,'role':'same-window DAY structural reference only; do not copy old broken paving joint'},{**ref(style),'role':'confirmed rounded clean Daoist Q style only'}]
 prompt='Use case: precise-object-edit. Edit image1, an exact 1254 square native fishing village Lantern Festival map crop. Fix ONLY the very faint artificial perfectly vertical paint/color cutoff at image x627, about y510..730, inside the lavender mottled stone surface. This small straight vertical line is a pasted appearance seam, NOT a stone edge, grout, shadow contour or crack. Continue the existing lavender/peach painted patches and soft tone across that line naturally. Keep all real stone joints, outlines, stone sizes, rounded corners, bevels, texture scale and the exact current image1 paving geometry unchanged. In particular, do not move, reopen or reshape the already fixed continuous paving joint below this small color defect. Image2 is the same native window of the DAY geometry; it contains an OLD broken paving joint that must NOT be copied. Image1 wins for all geometry and all festival appearance. Image3 supplies only the confirmed clean rounded hand-painted Daoist Q rendering style, no UI content. Preserve image1 colors, shading, composition, field of view and every pixel region outside the tiny vertical paint seam as closely as possible. No new objects, lanterns, lines, text, UI, framing, camera changes, zoom, rescaling, sharpening, blur, bloom, orange wash, or changed shadows. Output one opaque1254 by1254 image with the same field of view. Correct color and brushwork continuity only; geometry must stay fixed.'
 write(R/'references.json',refs);(R/'prompt.txt').write_text(prompt,encoding='utf8');write(R/'request.json',{'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False});print(json.dumps(read(R/'request.json')))
def record(raw):
 raw=Path(raw);p=R/'native.png';assert not p.exists();im=Image.open(raw);assert im.size==(1254,1254);shutil.copyfile(raw,p);req=read(R/'request.json')
 write(str(p)+'.generation.json',{**ref(p),'width':1254,'height':1254,'generatedAt':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','configSnapshot':read(ROOT/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**req},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin path exposes no selectors or actual model/quality metadata.','evidence':{'toolResultSourcePath':str(raw),'sha256':sha(raw)},'prompt':str(R/'prompt.txt'),'promptSha256':sha(R/'prompt.txt'),'references':read(R/'references.json'),'resizedAfterGeneration':False,'geometryChangeAllowed':False})
 print(json.dumps(ref(p)))
def compose():
 assert sha(SOURCE)==EXPECTED;base=np.asarray(Image.open(SOURCE).convert('RGB'));result=base.copy();native=np.asarray(Image.open(R/'native.png').convert('RGB'));assert native.shape==(1254,1254,3)
 x,y,_,_=CROP;l,t,r,b=ROI;yy,xx=np.mgrid[:1254,:1254];d=np.minimum.reduce((xx+x-l,yy+y-t,r-1-xx-x,b-1-yy-y)).astype(np.float32);w=np.clip(d/48,0,1);w=w*w*(3-2*w);alpha=np.rint(w*255).astype(np.uint8)
 view=result[y:y+1254,x:x+1254];view[:]=((view.astype(np.uint32)*(255-alpha[:,:,None])+native.astype(np.uint32)*alpha[:,:,None]+127)//255).astype(np.uint8)
 support=np.zeros(base.shape[:2],bool);support[y:y+1254,x:x+1254]=alpha>0;assert np.array_equal(result[~support],base[~support])
 mask=save(R/'integration-mask.png',Image.fromarray(alpha),{'operation':'48px smoothstep return mask','boundsPairXYXY':ROI,'nativePairCropXYXY':CROP})
 common={'derivedFrom':[ref(SOURCE),ref(R/'native.png')],'operation':'Native patch insertion with local 48px returns for paint continuity only','mask':mask,'roiPairXYXY':ROI,'outsideMaskPixelIdentical':True,'approvedWallAndPavingRepairPreservedOutsideColorROI':True,'artResampled':False,'artUpscaled':False,'blurred':False,'geometryChangeAllowed':False,'formalAccepted':False,'completePixelCandidate':True,'visualReview':'pending','geometrySyncRequired':'Inherited paving repair needs DAY synchronization; this color operation authorizes no geometry change.'}
 pair=save(OUT/'output/pair-r08_c12-c13.png',Image.fromarray(result),{**common,'globalRectXYWH':[45056,28672,8192,4096]})
 tiles=[]
 for n,i in [(12,0),(13,1)]:tiles.append(save(OUT/'output'/f'r08_c{n}.png',Image.fromarray(result[:,i*4096:(i+1)*4096]),{**common,'derivedFrom':[pair],'operation':'Exact native tile crop','globalRectXYWH':[45056+i*4096,28672,4096,4096]}))
 boxes={'complete-return':CROP,'top-return':[l-96,t-96,r+96,t+96],'bottom-return':[l-96,b-96,r+96,b+96],'left-return':[l-96,t-96,l+96,b+96],'right-return':[r-96,t-96,r+96,b+96]};qa=[]
 for name,box in boxes.items():qa.append(save(OUT/'qa'/f'color-{name}.png',Image.fromarray(result).crop(box),{'operation':'Exact native repair return crop','derivedFrom':[pair],'pairCropXYXY':box,'resized':False}))
 manifest={**common,'pair':pair,'tiles':tiles,'qa':qa,'changedPixels':int(np.any(base!=result,axis=2).sum()),'script':ref(__file__)};write(OUT/'output/integration-manifest.json',manifest);print(json.dumps({'tiles':[ref(Path(i['file'])) for i in tiles],'pair':ref(Path(pair['file'])),'changedPixels':manifest['changedPixels'],'outsideMaskPixelIdentical':True},indent=2))
if __name__=='__main__':
 {'prepare':prepare,'record':lambda:record(sys.argv[2]),'compose':compose}[sys.argv[1]]()
