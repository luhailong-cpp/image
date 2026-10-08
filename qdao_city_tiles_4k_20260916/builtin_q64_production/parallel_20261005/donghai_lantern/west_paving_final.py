from pathlib import Path
import sys,json,hashlib,shutil
from datetime import datetime,timezone
import numpy as np
from PIL import Image

OWN=Path(__file__).resolve().parent
ROOT=OWN/'r08_c13/repairs/west-paving-final'
DAY=OWN.parent/'donghai_day'
RECT=(3469,1770,4723,3024)
ROI=(3650,2110,4590,2610)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p,role=None):
 d={'file':str(p),'sha256':sha(p)}
 if role:d['role']=role
 return d
def savej(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
def prep():
 ROOT.mkdir(parents=True,exist_ok=True)
 left=OWN/'r08_c13/west-final/output/r08_c12.png'
 right=OWN/'r08_c13/right-stone-sync/tone-matched/output/r08_c13.png'
 assert sha(left)=='c24b061459e3dc89d45fc101c8ddd9d8606433a35ff8fcc29565bf3cce15ddf6'
 assert sha(right)=='9f88ba04a1f50ca198bd368060d2cba6f83a29bb3f75e2df702504fb8190732f'
 base=Image.new('RGB',(8192,4096));base.paste(Image.open(left),(0,0));base.paste(Image.open(right),(4096,0))
 target=ROOT/'festival-edit-target.png';base.crop(RECT).save(target)
 sources=[meta(left),meta(right)]
 savej(target.with_suffix('.png.generation.json'),{'file':str(target),'sha256':sha(target),'generatedByAI':False,'operation':'exact native crop of pinned latest festival pair','derivedFrom':sources,'pairRectXYXY':RECT,'resized':False})
 # Existing repaired DAY common strip is exact same scene window.
 ds=Image.new('RGB',(1254,4096))
 dayleft=DAY/'tiles/r08_c12.png';dayright=DAY/'tiles/r08_c13.png'
 dp=Image.new('RGB',(8192,4096));dp.paste(Image.open(dayleft),(0,0));dp.paste(Image.open(dayright),(4096,0))
 daycrop=ROOT/'day-same-window.png';dp.crop(RECT).save(daycrop)
 savej(daycrop.with_suffix('.png.generation.json'),{'file':str(daycrop),'sha256':sha(daycrop),'generatedByAI':False,'operation':'exact native crop of current DAY pair','derivedFrom':[meta(dayleft),meta(dayright)],'pairRectXYXY':RECT,'resized':False})
 style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
 prompt='''Use case: precise-object-edit. Asset: a native-resolution local repair to an established bright rounded Chinese Q-style festival town game map. Edit image 1, keep its EXACT 1254x1254 frame, scale and warm gold/purple festival rendering. Image 2 is the exact same DAY window only for existing stone and object geometry; it contains the same erroneous paving joint. Image 3 is the confirmed painting/material/style reference, not a new composition.
ONLY repair the two disconnected ends of the diagonal mortar joint in the central stone pavement, approximately image x=280..990,y=330..710. The upper-left incoming dark gray diagonal joint presently fades at about x=640,y=480; the lower-right outgoing joint starts around x=630,y=606. Join those misplaced ends into ONE plausible uninterrupted stone-slab boundary with a neat rounded offset corner/short connecting return, natural same-width gray mortar and warm beveled edge. You may locally reshape the immediately adjacent stone edges to make this specific connection geometrically coherent. It must be a physical continuous slab boundary, not two dead ends hidden under purple mottling, not a disconnected pair of parallel strokes. Keep all distant slab joints exactly at their current locations. Preserve all mottled purple stone texture except what is necessary for that narrow joint repair, preserve illumination, brush finish and shadows. Do not change wood/rope/cloth, add objects, reframe, zoom, replace the scene, or alter overall color. Preserve all pixels outside the repair neighborhood as closely as possible. Return only the repaired full-frame image, no annotations, grids, letters, text, borders or watermark.'''
 (ROOT/'prompt.txt').write_text(prompt,encoding='utf-8')
 req={'prompt':prompt,'referenced_image_paths':[str(target),str(daycrop),str(style)],'transparent_background':False}
 savej(ROOT/'request.json',req)
 h,w=ROI[3]-ROI[1],ROI[2]-ROI[0]
 yy,xx=np.mgrid[:h,:w];alpha=np.minimum.reduce([xx,yy,w-1-xx,h-1-yy]).astype(np.float32)/48
 alpha=np.clip(alpha,0,1);alpha=alpha*alpha*(3-2*alpha)
 np.savez_compressed(ROOT/'integration-mask.npz',alpha=alpha)
 Image.fromarray(np.rint(alpha*255).astype(np.uint8)).save(ROOT/'integration-mask.png')
 plan={'sources':sources,'pairOriginGlobalXY':[45056,28672],'nativePairRectXYXY':RECT,'integrationPairRectXYXY':ROI,'nativeCropXYXY':[ROI[0]-RECT[0],ROI[1]-RECT[1],ROI[2]-RECT[0],ROI[3]-RECT[1]],'mask':meta(ROOT/'integration-mask.npz'),'maskKey':'alpha','featherWidthPx':48,'blend':'round(base*(1-alpha)+edited*alpha) per channel; no scaling or geometric transforms','outsideIntegrationRectMustStayIdentical':True,'formalAccepted':False,'geometrySyncRequired':True,'note':'DAY source has the inherited disconnect. This festival local repair requires later matching DAY geometry before cross-appearance acceptance; DAY assets not modified.'}
 savej(ROOT/'integration-plan.json',plan)
 savej(ROOT/'geometry-sync-required.json',{'id':'C12-C13-PAVING-JOINT-02','DAYModified':False,'crossAppearanceAcceptance':False,'requiredAction':'Synchronize this exact small joint geometry and insertion mask into the matching DAY appearance after visual acceptance; never claim existing DAY pixels have been fixed.','pairRectXYXY':ROI,'globalRectXYXY':[ROI[0]+45056,ROI[1]+28672,ROI[2]+45056,ROI[3]+28672]})
 print(json.dumps(req))
def record(raw):
 raw=Path(raw);out=ROOT/'edited-native.png';shutil.copyfile(raw,out)
 im=Image.open(out);assert im.size==(1254,1254),im.size
 req=json.loads((ROOT/'request.json').read_text(encoding='utf-8'))
 rec={'file':str(out),'sha256':sha(out),'generatedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露型号与质量，无可核实元数据。','evidence':{'toolResultSourcePath':str(raw),'sourceSha256':sha(raw)},'prompt':str(ROOT/'prompt.txt'),'references':[meta(Path(p),r) for p,r in zip(req['referenced_image_paths'],['edit target: pinned festival same-window','same-window DAY geometry; inherited joint defect','confirmed style'])],'formalAccepted':False,'visualQA':'pending','integrationPlan':str(ROOT/'integration-plan.json'),'geometrySyncRequired':True}
 savej(out.with_suffix('.png.generation.json'),rec)
 plan=json.loads((ROOT/'integration-plan.json').read_text(encoding='utf-8'))
 plan.update({'name':'paving','native':meta(out),'nativePairXY':list(RECT[:2]),'roiPairXYXY':list(ROI),'featherPixels':48,'type':'local-paving-joint-correction','generationRecord':str(out.with_suffix('.png.generation.json'))})
 savej(ROOT/'integration-plan.json',plan)
 base=np.array(Image.open(ROOT/'festival-edit-target.png').convert('RGB'))
 edited=np.array(im.convert('RGB'))
 l,t,r,b=plan['nativeCropXYXY'];alpha=np.load(ROOT/'integration-mask.npz')['alpha'][...,None]
 local=base.copy();local[t:b,l:r]=np.rint(base[t:b,l:r]*(1-alpha)+edited[t:b,l:r]*alpha).astype(np.uint8)
 test=ROOT/'local-integration-check.png';Image.fromarray(local).save(test)
 savej(test.with_suffix('.png.generation.json'),{'file':str(test),'sha256':sha(test),'generatedByAI':False,'operation':'local-only 48px bounded alpha integration preview; no full pair or global files changed','derivedFrom':[meta(ROOT/'festival-edit-target.png'),meta(out)],'integrationPlan':str(ROOT/'integration-plan.json'),'outsideROIExactlyIdentical':True,'formalAccepted':False})
 print(json.dumps({'output':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prep()
 elif sys.argv[1]=='record':record(sys.argv[2])
