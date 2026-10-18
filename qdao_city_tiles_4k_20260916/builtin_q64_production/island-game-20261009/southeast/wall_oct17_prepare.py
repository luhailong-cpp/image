import os,sys
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
pid,v,desc=sys.argv[1:];tid=pid[:7];assert tid in ['r11_c10','r12_c10','r08_c09','r09_c09','r10_c09','r11_c09']
assert not (ROOT/'native'/f'{pid}_{v}.png').exists()
p=patch(pid);box=p['nativeGlobalBox'];base=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(base).convert('RGB');parts=[{'file':str(base),'sha256':sha(base),'role':'layout only, not final pixels'}]
neighbors=[]
if tid=='r11_c10':neighbors=[('r10_c10','r10_c10.candidate-wall-oct17-v02.png'),('r11_c11','r11_c11.candidate-v02.png')]
for nt,name in neighbors:
 f=ROOT/'tiles'/name; r=int(nt[1:3]);c=int(nt[5:7]);nb=[(c-1)*4096,(r-1)*4096,c*4096,r*4096];inter=[max(box[0],nb[0]),max(box[1],nb[1]),min(box[2],nb[2]),min(box[3],nb[3])]
 if inter[0]>=inter[2] or inter[1]>=inter[3]:continue
 crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]];im.paste(Image.open(f).convert('RGB').crop(crop),dest);parts.append({'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destination':dest,'role':'actual selected neighbor pixels, only outside own core'})
for other in read(ROOT/'progress-wall-oct16.json').get('selected',{}).values():
 f=Path(other['file'])
 if not f.name.startswith(tid+'_') or f.name.startswith(pid+'_'):continue
 rec=read(Path(str(f)+'.generation.json'));nb=rec['coordinate']['nativeGlobalBox'];cb=rec['coordinate']['coreGlobalBox'];inter=[max(box[0],cb[0]),max(box[1],cb[1]),min(box[2],cb[2]),min(box[3],cb[3])]
 if inter[0]>=inter[2] or inter[1]>=inter[3]:continue
 assert sha(f)==other['sha256'];crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]];im.paste(Image.open(f).convert('RGB').crop(crop),dest);parts.append({'file':str(f),'sha256':sha(f),'sourceCrop':crop,'destination':dest,'role':'selected core only, never unselected halo'})
guide=ROOT/'guides'/f'{pid}.selected-core-wall17-{v}.png';assert not guide.exists();im.save(guide);write(Path(str(guide)+'.generation.json'),{'file':str(guide),'sha256':sha(guide),'nativeGlobalBox':box,'derivedFrom':parts,'usableAsFinalArt':False})
prompt=f'''Use case: precise-object-edit. Generate one exactly1254x1254 opaque game-art close-up. Image1 is the exact coordinate crop and camera. Keep the sharp outer115px bands unchanged: those are actual selected neighboring art. Replace only the blurry central area with crisp native hand-painted detail that connects perfectly to the sharp strips, preserving all contour endpoints, scale and perspective. LOCAL CONTENT: {desc} Do not zoom out or fit a whole object inside this tiny crop. Images2-4 are full-map layout and material/style references only, never add their unrelated objects. Q Daoist daylight game art, natural pale-grey stone, warm wood/gold where present, clean jade foliage. No new buildings, people, animals, UI, text, labels or watermark; no remaining blur or rectangular guide edges. Patch {pid}, final used core local[115,115,1139,1139).'''
refs=[{'file':str(guide),'sha256':sha(guide),'role':'exact edit target and camera; selected outer core context'}]+read(ROOT/'references.json')
pf=ROOT/'prompts'/f'{pid}_{v}.prompt.txt';pf.write_text(prompt,encoding='utf-8');write(ROOT/'prompts'/f'{pid}_{v}.request.json',{'promptPath':str(pf),'references':refs,'transparent_background':False,'submittedParameters':{'model':None,'quality':None}});write(ROOT/'prompts'/f'{pid}_{v}.args.json',{'prompt':prompt,'referenced_image_paths':[x['file'] for x in refs],'transparent_background':False});print(guide)
