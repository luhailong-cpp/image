from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFilter
import json,hashlib,shutil,numpy as np
B=Path(__file__).resolve().parent;T=B.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
raw=Path('C:/Users/luyua/.codex/generated_images/01a10bb2-5cf3-7db0-a7f1-5c85ef972ed1/exec-72f97f6e-cd23-416b-b218-b6a6f7bceeba.png')
dst=B/'generated-1254.png';shutil.copyfile(raw,dst)
a=np.array(Image.open(B/'edit-target-1254.png').convert('RGB'),dtype=np.int32)
z=np.array(Image.open(dst).convert('RGB'),dtype=np.int32)
assert a.shape==z.shape==(1254,1254,3)
roi=Image.new('L',(1254,1254));d=ImageDraw.Draw(roi)
d.polygon([(0,420),(60,454),(60,540),(322,703),(336,783),(245,816),(0,650)],fill=255)
d.polygon([(480,884),(527,884),(589,942),(592,1058),(568,1108),(493,1075),(480,1004)],fill=255)
r,g,b=a[:,:,0],a[:,:,1],a[:,:,2];nr,ng,nb=z[:,:,0],z[:,:,1],z[:,:,2]
wood=(r>g+24)&(g>b+18)&(r>140)
changed_red=(nr>ng+70)&(nr>100)&(ng<130)&((g-ng)>26)
# Include adjacent original gold highlights so mixed source/generated highlights
# do not leave tiny staircase fragments inside the otherwise continuous wood.
near_red=np.array(Image.fromarray(changed_red.astype('uint8')*255).filter(ImageFilter.MaxFilter(7)))>0
sel=(np.array(roi)>0)&wood&near_red
# One-pixel antialiased boundary inside the original wood support only.
inside=np.array(Image.fromarray(sel.astype('uint8')*255).filter(ImageFilter.MinFilter(3)))>0
alpha=np.where(inside,255,np.where(sel,176,0)).astype('uint8')
out=np.rint(z*alpha[:,:,None]/255+a*(255-alpha[:,:,None])/255).astype('uint8')
Image.fromarray(alpha).save(B/'mask-1254.png');Image.fromarray(out).save(B/'edited-1254.png')
ext=np.array(Image.open(T/'shared-geometry/extended4326.png').convert('RGB'));orig=ext.copy()
ext[3072:4326,0:1254]=out
mask=np.zeros((4326,4326),dtype='uint8');mask[3072:4326,0:1254]=alpha
Image.fromarray(ext).save(B/'candidate_with_halo.png');Image.fromarray(ext[115:4211,115:4211]).save(B/'candidate_4096.png')
Image.fromarray(mask).save(B/'mask-4326.png');Image.fromarray(mask[115:4211,115:4211]).save(B/'mask-4096.png')
assert np.array_equal(ext[mask==0],orig[mask==0])
meta=json.loads((B/'tool-result.json').read_text(encoding='utf-8'))
refs=[{'path':str(B/'edit-target-1254.png'),'role':'native1254 edit target; exact geometry and crop'}, {'path':'D:/work/image/designs/gameplay-ui/04-guild.png','role':'confirmed primary painting/material style'}]
for ref in refs:ref['sha256']=sha(ref['path'])
wr(B/'generated-1254.png.generation.json',{'file':str(dst),'sha256':sha(dst),'pixels':[1254,1254],'generatedAt':meta['completedAt'],'route':'builtin','tool':'image_gen.imagegen','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[r['path'] for r in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin tool does not expose model or quality selector or verifiable return values.','prompt':str(B/'prompt.txt'),'promptSha256':sha(B/'prompt.txt'),'references':refs,'toolResultMetadata':meta,'originalToolResultImagePath':str(raw),'originalToolResultImageSha256':sha(raw)})
wr(B/'processing.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(T/'shared-geometry/extended4326.png'),'sourceSha256':sha(T/'shared-geometry/extended4326.png'),'generated':str(dst),'generatedSha256':sha(dst),'cropInExtended':[0,3072,1254,4326],'mask':str(B/'mask-4326.png'),'maskSha256':sha(B/'mask-4326.png'),'maskDefinition':'Two bounded visible wood ROIs intersected with original orange wood color and generated red change; one-pixel inward alpha176 boundary','resampling':None,'warp':None,'outsideMaskByteEqual':True,'changedPixels':int(np.any(ext!=orig,axis=2).sum()),'outputs':[{'file':str(B/n),'sha256':sha(B/n)} for n in ['candidate_4096.png','candidate_with_halo.png']],'qa':'pending visual review','formalAccepted':False})
print(json.dumps({'edited':str(B/'edited-1254.png'),'maskPixels':int(sel.sum())}))
