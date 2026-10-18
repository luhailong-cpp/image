"""Worker-owned seam-centered native repair. Guides never enter final pixels."""
import os,sys,shutil
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
from PIL import ImageFilter
cmd=sys.argv[1]
if cmd=='prepare':
 tid,key,rev,box_s,mask_s,desc=sys.argv[2:]
 assert tid in ['r10_c10','r11_c10','r12_c10']
 box=json.loads(box_s);mask=json.loads(mask_s)
 assert box[2]-box[0]==1254 and box[3]-box[1]==1254 and min(box)>=0 and max(box)<=4096
 src=ROOT/'tiles'/f'{tid}.candidate-{rev}.png';im=Image.open(src).convert('RGB').crop(box)
 im.paste(im.crop(mask).filter(ImageFilter.GaussianBlur(24)),mask[:2])
 stem=f'{tid}_ov_{key}'
 guide=ROOT/'guides'/f'{stem}.png';assert not guide.exists();im.save(guide)
 meta={'tile':tid,'key':key,'candidate':str(src),'candidateSha256':sha(src),'candidateCrop':box,'guide':str(guide),'guideSha256':sha(guide),'guideMask':mask,'guideOnly':True,'finalSourceMustBeNewNative':True,'coreCrop':[115,115,1139,1139],'destinationBox':[box[0]+115,box[1]+115,box[0]+1139,box[1]+1139]}
 write(ROOT/'prompts'/f'{stem}.overlay.json',meta)
 prompt=f'''Use case: precise-object-edit. Generate one opaque image exactly1254x1254, same camera and scale as image1. Image1 is an exact cropped game-art repair target. Only the small blurred area needs to be painted into crisp new detail. Keep ALL sharp surroundings at their exact coordinates, especially all four outer115px edge bands. The blurred region hides a seam defect; repair it by completing the obvious continuous geometry, never preserve the broken endpoints. {desc} Do not redraw unrelated objects or change lighting/material/stone size. Clean detailed Q Daoist daylight game art, pale-grey stone and ivory architectural elements. No text/UI/people/watermark. Never zoom or move camera.'''
 args={'prompt':prompt,'referenced_image_paths':[str(guide)],'transparent_background':False}
 write(ROOT/'prompts'/f'{stem}.args.json',args);write(ROOT/'prompts'/f'{stem}.request.json',{'submittedArguments':args,'actualModel':None,'actualQuality':None,'guideProvenance':meta});print(guide)
elif cmd=='receive':
 tid,key,src_s,hint=sys.argv[2:];stem=f'{tid}_ov_{key}';src=Path(src_s);im=Image.open(src);assert im.size==(1254,1254)
 meta=read(ROOT/'prompts'/f'{stem}.overlay.json');f=ROOT/'native'/f'{stem}.png';assert not f.exists()
 shutil.copy2(src,f);receipt=ROOT/'receipts'/f'{stem}.wall-oct16.tool.json'
 write(receipt,{'tool':'image_gen.imagegen','route':'builtin','submittedArguments':read(ROOT/'prompts'/f'{stem}.args.json'),'output_hint':hint,'actualModel':None,'actualQuality':None,'receivedAt':now(),'sourceFile':str(src),'sourceSha256':sha(src),'copiedNative':str(f),'copiedNativeSha256':sha(f),'imageDataOmitted':True})
 write(Path(str(f)+'.generation.json'),{'file':str(f),'sha256':sha(f),'nativePixels':[1254,1254],'actualModel':None,'actualQuality':None,'receipt':str(receipt),'candidateGuide':meta,'operation':'unaltered built-in image generation output copied byte for byte'})
 d=read(ROOT/'progress-wall-oct16.json');d['inFlight']=[x for x in d.get('inFlight',[]) if x!=stem];write(ROOT/'progress-wall-oct16.json',d)
 print(json.dumps({'file':str(f),'sha256':sha(f),'nativePixels':[1254,1254]}))
elif cmd=='qa':
 tid,key=sys.argv[2:];stem=f'{tid}_ov_{key}';meta=read(ROOT/'prompts'/f'{stem}.overlay.json');f=ROOT/'native'/f'{stem}.png';im=Image.open(meta['candidate']).convert('RGB');ni=Image.open(f).convert('RGB');x,y,x1,y1=meta['destinationBox'];im.paste(ni.crop((115,115,1139,1139)),(x,y))
 q=ROOT/'qa'/'wall-oct16'/stem;q.mkdir();entries=[]
 for name,box in [('center',[x,y,x1,y1]),('left',[x-256,y,x+256,y1]),('right',[x1-256,y,x1+256,y1]),('top',[x,y-256,x1,y+256]),('bottom',[x,y1-256,x1,y1+256])]:
  box=[max(0,box[0]),max(0,box[1]),min(4096,box[2]),min(4096,box[3])]
  out=q/f'{name}.png';im.crop(box).save(out);entries.append({'file':str(out),'sha256':sha(out),'box':box,'kind':name,'status':'pending_visual_review'})
 write(q/'review.json',{'source':str(f),'sourceSha256':sha(f),'candidate':meta['candidate'],'candidateSha256':meta['candidateSha256'],'entries':entries,'status':'pending_visual_review','formalAccepted':False})
 print(q)

