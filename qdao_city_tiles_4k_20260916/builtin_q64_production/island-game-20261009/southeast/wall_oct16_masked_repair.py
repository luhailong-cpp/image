import os,sys
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
pid,v,target,mask,desc,*neighbors=sys.argv[1:]
assert pid[:7] in ['r09_c10','r10_c10','r11_c10','r12_c10']
src=ROOT/'native'/target;layout=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(src).convert('RGB');rect=json.loads(mask)
im.paste(Image.open(layout).convert('RGB').crop(rect),(rect[0],rect[1]))
box=patch(pid)['nativeGlobalBox'];parts=[{'file':str(src),'sha256':sha(src),'role':'unaltered native target outside masked repair area'},{'file':str(layout),'sha256':sha(layout),'crop':rect,'role':'blurry layout guide placeholder only, regenerate every pixel in this area'}]
for name in neighbors:
 f=ROOT/'native'/name;rec=read(Path(str(f)+'.generation.json'));nb=rec['coordinate']['nativeGlobalBox'];cb=rec['coordinate']['coreGlobalBox'];it=[max(box[0],cb[0]),max(box[1],cb[1]),min(box[2],cb[2]),min(box[3],cb[3])]
 crop=[it[0]-nb[0],it[1]-nb[1],it[2]-nb[0],it[3]-nb[1]];dest=[it[0]-box[0],it[1]-box[1]];im.paste(Image.open(f).convert('RGB').crop(crop),dest);parts.append({'file':str(f),'sha256':sha(f),'crop':crop,'destination':dest})
guide=ROOT/'guides'/f'{pid}.masked-repair-wall16-{v}.png';assert not guide.exists();im.save(guide)
write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'usableAsFinalArt':False,'operation':'native crop/paste with blurry layout-only placeholder for repair; no final-art contribution','derivedFrom':parts})
prompt=f'''Use case: precise-object-edit. Output exactly one opaque 1254 x 1254 crop with identical camera and scale. Image 1 is exact edit target. Repaint the blurred rectangular area into truly crisp original detail. Keep all sharp surrounding geometry fixed, especially the rightmost115px and top/bottom115px strips that come from true neighboring cores. Every stone edge and joint must connect to the visible endpoint at the blurred rectangle boundary without a break. Do not reproduce any rectangular guide boundary. LOCAL REPAIR: {desc} Preserve all other features. Do not zoom, move, shrink or fit whole objects into the cropped view. No text/UI/people/watermark. Same clean hand-painted Q Daoist daylight materials.'''
pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';pf.write_text(prompt,encoding='utf-8');refs=[{'file':str(guide),'sha256':sha(guide),'role':'repair target; sharp native context authoritative; blurry rectangle must be generated, never final pixels'}]
write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}})
write(ROOT/'prompts'/f'{pid}_{v}.args.json',{'prompt':prompt,'referenced_image_paths':[str(guide)],'transparent_background':False})
print(guide)
