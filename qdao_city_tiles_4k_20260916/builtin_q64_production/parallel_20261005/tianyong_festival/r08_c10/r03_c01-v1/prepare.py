from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,shutil
import numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;T=O.parent.parent;R=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(n,o):
 with (O/n).open('x',encoding='utf8') as f:json.dump(o,f,ensure_ascii=False,indent=2)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--checkpoint-sha',required=True);a=ap.parse_args()
 cpfile=T/'source-checkpoint.json';assert sha(cpfile)==a.checkpoint_sha
 cp=read(cpfile);assert int(cp['version'][1:])>=10,'Wait for accepted r03c02 upper to commit'
 fref=cp['fragment'];lref=cp['coupledNeighbors']['r08_c09'];assert sha(fref['file'])==fref['sha256'] and sha(lref['file'])==lref['sha256']
 box=[-115,1933,1139,3187];glob=[36749,30605,38003,31859];fb=fref['tileLocalLTRB']
 ctx=Image.new('RGBA',(1254,1254),(0,0,0,0));fi=Image.open(fref['file']).convert('RGBA');left=Image.open(lref['file']).convert('RGBA')
 assert fi.size==(fb[2]-fb[0],fb[3]-fb[1]) and left.size==(4096,4096)
 ctx.paste(fi.crop((0-fb[0],1933-fb[1],1139-fb[0],3187-fb[1])),(115,0))
 ctx.paste(left.crop((3981,1933,4096,3187)),(0,0))
 known=np.asarray(ctx)[:,:,3]==255
 assert known[:,:115].all() and known[:,1024:].all() and known[1024:,:].all(),'All left115/right230/bottom230 must be accepted opaque native pixels'
 assert not known[:1024,115:1024].any(),'Unexpected preexisting center; inspect ownership before new generation'
 assert sha(cpfile)==a.checkpoint_sha
 ctx.save(O/'context.png');ctx.save(O/'original-context.png')
 master=R/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png';assert sha(master)=='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
 with Image.open(master) as im:im.convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in glob)).save(O/'layout-reference-only.png')
 style=R/'designs/gameplay-ui/04-guild.png';assert sha(style)=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
 refs=[O/'context.png',O/'layout-reference-only.png',style]
 prompt='''Use case: precise-object-edit/outpainting. Finish one native1254x1254 opaque square crop of the original Chinese fantasy game plaza. In image1, fill ONLY the transparent missing center. All visible pixels are the accepted native surroundings at their exact world coordinates: LEFT115 pixels, RIGHT230 pixels, and BOTTOM230 pixels. They are authoritative shape, endpoint, material and color anchors. Preserve their structures, framing, pixel scale, contours, bevel widths, tangent directions and stone-plane colors exactly.
Continue the existing broad gently curving ivory/gold stone bands and quiet slate-gray/ivory stone panels through the transparent gap. The bottom and right show the real adjacent stones, not a loose style sample. Follow the very same contour positions at each boundary; do not narrow the bands or shift the edges to fit a new composition. Use the visible original plane colors for each connected stone. A transparency boundary is not a stone seam or texture rectangle. There must be no line, jog, bevel or change of finish marking x115,x1024 or y1024.
Image2 is the low-resolution canonical LOCATION AND STRUCTURE reference of this same exact crop. It tells which stone divisions cross the missing area; preserve the broad layout but never enlarge/copy its pixels into finished artwork. Precise endpoints and thickness always come from image1. Render new original-scale details, not a blurred enlarged guide. No invented building, character, foliage, object, new paving seam, carving or decoration.
Image3 is the approved primary STYLE reference only: bright clean, full rounded Daoist Q-version fantasy painting, gentle warm ivory, restrained warm gold, soft clean bevel shading. Do not import its interface, lettering, figures, icons or frames. For this plaza crop, the actual native map textures in image1 take priority over any UI surface.
Materials should stay subtle and quiet, matching the native surrounding stone. No cracks, mosaic speckles, grunge, veins or heavy cloudy mottling. Maintain the exact1254-square native framing. No resize, global recolor, zoom, camera move, rotation, text, watermark, border or transparency in the final result. Return only the completed map crop at the highest finish available through the host.'''
 (O/'prompt.txt').write_text(prompt,encoding='utf8')
 write('source-checkpoint-snapshot.json',cp)
 write('request.json',{'preparedAtUtc':datetime.now(timezone.utc).isoformat(),'patch':'r03_c01','tile':'r08_c10','globalCropLTRB':glob,'tileLocalCropLTRB':box,'knownPixels':int(known.sum()),'missingPixels':int((~known).sum()),'payload':{'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False},'configSnapshot':read(R/'config/image-generation.json'),'submittedModel':None,'submittedQuality':None,'submittedSize':None})
 write('preparation.json',{'sourceCheckpoint':info(O/'source-checkpoint-snapshot.json'),'currentCheckpointShaAtFreeze':a.checkpoint_sha,'nativeInputs':[{**fref,'role':'right230 and bottom230 accepted current fragment','cropLTRB':[0-fb[0],1933-fb[1],1139-fb[0],3187-fb[1]],'pasteXY':[115,0]},{**lref,'role':'left115 accepted current coupled neighbor','cropLTRB':[3981,1933,4096,3187],'pasteXY':[0,0]}],'references':[{**info(p),'role':role} for p,role in zip(refs,['native edit target; left/right/bottom authoritative','canonical reference only; forbidden final pixels','approved primary style'])],'master':info(master),'nativeScale':1,'guidePixelsAllowedInFinal':False,'allWritesConfinedTo':str(O),'formalAccepted':False})
 for p in [O/'context.png',O/'original-context.png',O/'layout-reference-only.png']:
  write(p.name+'.generation.json',{'file':str(p),'sha256':sha(p),'derivedFrom':[fref,lref] if p.name!='layout-reference-only.png' else [info(master)],'operation':'Exact native context crop; no upscale' if p.name!='layout-reference-only.png' else 'Location-only canonical crop; prohibited as final pixels','newModelCalls':0,'nativeScale':1 if p.name!='layout-reference-only.png' else None})
 shutil.copy2(T/'r08_c10/r04_c01-v1/shifted-v1/capability-evidence.json',O/'capability-evidence.json')
 print(json.dumps({'directory':str(O),'knownPixels':int(known.sum()),'missingPixels':int((~known).sum()),'checkpointVersion':cp['version']}))
if __name__=='__main__':main()
