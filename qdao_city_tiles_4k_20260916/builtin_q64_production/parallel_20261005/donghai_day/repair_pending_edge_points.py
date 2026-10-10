from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,sys,shutil
R=Path(__file__).resolve().parent
STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def spec(name):
 if name=='panel-notch':
  return R/'r07_c15/repairs/panel-notch-ai',[0,2600,1254,3854],R/'r07_c15/repairs/unified/candidate.png','0a677ad6deb2347659789f3c45a5055b1611ea0cffeff0d5a6e64c40e7df6a52'
 return R/('r07_c16/repairs/south-west-joint-masked' if name=='south-west-joint-masked' else 'r07_c16/repairs/south-west-joint-ai'),[443,3469,1697,4723],R/'r07_c16/repairs/integrated-south-v2/candidate.png','3f5be4ea2f6cb9e54121761646fc0b0c218af12738fa7493c198a1f4b9944bc2'
def prep(name):
 d,box,base,bsha=spec(name);d.mkdir(exist_ok=True);assert sha(base)==bsha
 refs=[{'file':str(base),'sha256':bsha}]
 im=Image.open(base).convert('RGB')
 if name=='panel-notch':
  src=im.crop(box);target=src.convert('RGBA')
  # Tiny transparent hole straddles the residual artificial 3px rail-underedge notch.
  target.paste((0,0,0,0),(575,432,615,468))
  roi=[570,3020,625,3080]
  prompt='Edit the FIRST image at its exact 1254x1254 native size. The small transparent hole near pixel (590,447) is the only intended repair: reconstruct the existing diagonal wooden rail lower edge so it is a single smooth straight diagonal continuation through the gap, including its thin dark underside border and immediately adjacent blue glass. Remove the artificial approximately3px stair at that point. Do not move the whole rail, do not add wood or hardware, and preserve every surrounding rail, wood grain, blue panel reflection and object geometry. Fill only this tiny hole with exact adjacent colors and brush style, no blur or new texture. Return a fully opaque1254x1254 image. The SECOND image is a style reference only, preserve the FIRST image composition; rounded bright clean Q-style painted wood and glass. No text or UI.'
 else:
  south=R/'r08_c16/output/r08_c16.png';assert sha(south)=='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de'
  canvas=Image.new('RGB',(4096,8192));canvas.paste(im,(0,0));canvas.paste(Image.open(south).convert('RGB'),(0,4096));src=canvas.crop(box);target=src
  refs.append({'file':str(south),'sha256':sha(south),'role':'immutable south reference'})
  roi=[700,3550,1320,4096]
  prompt='Precisely repair the FIRST1254x1254 native image, preserving camera/layout/scale. It is an actual joint between two neighboring finished map tiles. Horizontal line at local y627 is their boundary. The entire BOTTOM portion y627..1253 is immutable reference and must remain visually identical. The top150 pixels are also fixed. Only in the TOP half local x257..877,y150..626, remove the horizontal brightness/paint-color cut where the existing vertical wooden mast and diagonal wooden spar meet the lower tile at y627. The wooden mast/spar contours and rope endpoints must continue into the fixed lower image naturally, with matching warm wood colors and grain, preserving all original objects and shadows. Do not straighten intentional diagonal members, move the mast, grow new ropes, invent wood planks, or modify right-side rope/spar fittings. Repair only this small transition using neighboring true details; all water remains calm broad blue painted gradients, no fine grid or caustics. Keep right of localx877 unchanged. SECOND image is locked style reference only, rounded bright clean Q-style painted materials. Return exact1254x1254 opaque image; do not rescale or crop.'
 src.save(d/'source-crop.png');target.save(d/'input.png');(d/'prompt.txt').write_text(prompt,encoding='utf-8')
 v={'name':name,'file':str(d/'input.png'),'sha256':sha(d/'input.png'),'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceRectXYXY':box,'rawUnmodifiedCropRGBSha256':hashlib.sha256(src.tobytes()).hexdigest(),'derivedFrom':refs,'suggestedIntegrationROI':roi,'prompt':str(d/'prompt.txt'),'promptSha256':sha(d/'prompt.txt'),'references':[{'file':str(d/'input.png'),'sha256':sha(d/'input.png')},{'file':str(STYLE),'sha256':sha(STYLE)}],'preparedSource':'source-crop.png unscaled1254; input is identical except explicit small transparency repair mask for panel-notch'}
 save(d/'input.png.generation.json',v)
 print(json.dumps({'name':name,'prompt':prompt,'references':[str(d/'input.png'),str(STYLE)]}))
def record(name,source):
 d,box,base,bsha=spec(name);source=Path(source);im=Image.open(source)
 assert im.size==(1254,1254),f'Native size must remain1254: {im.size}'
 out=d/'edited-native.png';shutil.copyfile(source,out);v=json.loads((d/'input.png.generation.json').read_text())
 cfg=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
 g={'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'generatedAt':datetime.now(timezone.utc).isoformat(),'route':'builtin','configurationTarget':cfg,'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'evidence':{'tool':'image_gen.imagegen','toolResultFile':str(source),'toolResultSha256':sha(source),'selectorDisclosure':'Tool exposes no model/quality selectors or returned values'},'prompt':v['prompt'],'promptSha256':v['promptSha256'],'references':v['references'],'derivedFrom':v['derivedFrom'],'sourceRectXYXY':box,'rawUnmodifiedCropRGBSha256':v['rawUnmodifiedCropRGBSha256'],'suggestedIntegrationROI':v['suggestedIntegrationROI'],'resizedAfterGeneration':False,'finalArtUpscaled':False,'formalAccepted':False,'visualReview':'pending'}
 save(Path(str(out)+'.generation.json'),g);print(json.dumps({'name':name,'file':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 if sys.argv[1]=='prepare':prep(sys.argv[2])
 else:record(sys.argv[2],sys.argv[3])

