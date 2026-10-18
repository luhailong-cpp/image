from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent;Z=T.parent;R=T/'repairs/local-seams-20261016-v1';O=R/'trial';O.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
P=read(T/'progress.json');basepath=Path(P['candidate']);ctxpath=Path(P['context']);base=np.array(Image.open(basepath).convert('RGB'));out=base.copy();support=np.zeros((4096,4096),dtype=bool);entries=[]
def fade_rect(box,feather,openleft=False):
 x0,y0,x1,y1=box; yy,xx=np.mgrid[y0:y1,x0:x1];d=np.minimum.reduce([xx-x0,np.full_like(xx,feather) if openleft else xx-x0,x1-1-xx,yy-y0,y1-1-yy]);
 if openleft:d=np.minimum.reduce([x1-1-xx,yy-y0,y1-1-yy])
 return np.clip(d/feather,0,1).astype(np.float32)
for key,origin,boxes in [('I01',(1010,1460),[(1580,1930,1690,2190,16,False)]),('W01',(-192,0),[(0,16,650,118,12,True),(0,268,650,355,12,True)])]:
 nativepath=R/(key+'-native.png');native=np.array(Image.open(nativepath).convert('RGB'));alpha=np.zeros((1254,1254),dtype=np.float32)
 for x0,y0,x1,y1,f,openleft in boxes:
  ax,ay=x0-origin[0],y0-origin[1];a=fade_rect((x0,y0,x1,y1),f,openleft);alpha[ay:ay+y1-y0,ax:ax+x1-x0]=a
  sample=native[ay:ay+y1-y0,ax:ax+x1-x0];out[y0:y1,x0:x1]=np.rint(base[y0:y1,x0:x1]*(1-a[...,None])+sample*a[...,None]).astype(np.uint8);support[y0:y1,x0:x1]|=(a>0)
 mp=O/(key+'-alpha.npy');np.save(mp,alpha,allow_pickle=False)
 entries.append({'id':key,'native':str(nativepath),'nativeSha256':sha(nativepath),'sourceOriginInCore':list(origin),'alpha':str(mp),'alphaSha256':sha(mp),'rectangles':boxes})
assert np.array_equal(out[~support],base[~support]);assert np.array_equal(out[:,3712:],base[:,3712:]);assert np.array_equal(out[:16],base[:16])
dest=O/'r16_c15-4k-I01-W01-trial.png';Image.fromarray(out).save(dest)
ctx=Image.open(ctxpath).convert('RGB');ctx.paste(Image.fromarray(out),(115,115));cp=O/'r16_c15-context-I01-W01-trial.png';ctx.save(cp)
Image.fromarray(out[1850:2250,1450:1820]).save(O/'I01-local.png')
Image.fromarray(out[0:550,0:900]).save(O/'W01-local.png')
westpath=Path(read(Z/'r16_c14/progress.json')['candidate']);west=Image.open(westpath).convert('RGB');pair=Image.new('RGB',(1092,550));pair.paste(west.crop((3904,0,4096,550)),(0,0));pair.paste(Image.fromarray(out).crop((0,0,900,550)),(192,0));pair.save(O/'W01-real-west-pair.png')
northpath=Z/'r15_c15/candidate/r15_c15-4k-south-v2-west-v1-20261016.png';north=Image.open(northpath).convert('RGB')
for q in [0,2]:
 pair=Image.new('RGB',(1024,384));pair.paste(north.crop((q*1024,3904,(q+1)*1024,4096)),(0,0));pair.paste(Image.fromarray(out).crop((q*1024,0,(q+1)*1024,192)),(0,192));pair.save(O/f'north-v2-q{q}.png')
manifest={'base':{'path':str(basepath),'sha256':sha(basepath)},'baseContext':{'path':str(ctxpath),'sha256':sha(ctxpath)},'repairs':entries,'candidate':{'path':str(dest),'sha256':sha(dest)},'context':{'path':str(cp),'sha256':sha(cp)},'north':{'path':str(northpath),'sha256':sha(northpath)},'west':{'path':str(westpath),'sha256':sha(westpath)},'changedPixels':int(np.any(out!=base,axis=2).sum()),'outsideMasksUnchanged':True,'east384Unchanged':True,'north16Unchanged':True,'actualModel':None,'status':'trial_pending_visual_QA','formalAccepted':False}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest))
