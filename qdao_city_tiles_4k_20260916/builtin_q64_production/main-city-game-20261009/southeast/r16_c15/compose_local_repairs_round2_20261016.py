from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
T=Path(__file__).resolve().parent;Z=T.parent;R=T/'repairs/local-seams-20261016-v1';O=R/'trial-v2';O.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(R/'trial/manifest.json');bp=Path(m['candidate']['path']);base=np.array(Image.open(bp).convert('RGB'));out=base.copy();support=np.zeros((4096,4096),bool);entries=[]
for key,origin,boxes in [('W02',(-192,0),[(448,40,630,125,12,False)]),('N01',(1600,-384),[(2105,0,2380,365,10,True)])]:
 p=R/(key+'-native.png');native=np.array(Image.open(p).convert('RGB'));mask=np.zeros((1254,1254),np.float32)
 for x0,y0,x1,y1,f,opentop in boxes:
  yy,xx=np.mgrid[y0:y1,x0:x1];ds=[xx-x0,x1-1-xx,y1-1-yy]
  if not opentop:ds.append(yy-y0)
  a=np.clip(np.minimum.reduce(ds)/f,0,1).astype(np.float32);ax=x0-origin[0];ay=y0-origin[1];mask[ay:ay+y1-y0,ax:ax+x1-x0]=a
  out[y0:y1,x0:x1]=np.rint(base[y0:y1,x0:x1]*(1-a[...,None])+native[ay:ay+y1-y0,ax:ax+x1-x0]*a[...,None]).astype(np.uint8);support[y0:y1,x0:x1]|=a>0
 mp=O/(key+'-alpha.npy');np.save(mp,mask,allow_pickle=False);entries.append({'id':key,'native':str(p),'nativeSha256':sha(p),'sourceOriginInCore':list(origin),'alpha':str(mp),'alphaSha256':sha(mp),'rectangles':boxes})
assert np.array_equal(out[~support],base[~support]);assert np.array_equal(out[:,3712:],base[:,3712:])
dest=O/'r16_c15-4k-I01-W02-N01-trial.png';im=Image.fromarray(out);im.save(dest)
ctx=Image.open(m['context']['path']).convert('RGB');ctx.paste(im,(115,115));cp=O/'r16_c15-context-I01-W02-N01-trial.png';ctx.save(cp)
for label,box in [('W02-local',(380,0,870,420)),('N01-local',(2000,0,2520,470)),('I01-unchanged',(1450,1850,1820,2250))]:im.crop(box).save(O/(label+'.png'))
west=Image.open(m['west']['path']).convert('RGB');pair=Image.new('RGB',(1092,550));pair.paste(west.crop((3904,0,4096,550)),(0,0));pair.paste(im.crop((0,0,900,550)),(192,0));pair.save(O/'west-final-q0.png')
north=Image.open(m['north']['path']).convert('RGB')
for q in (0,2):
 pair=Image.new('RGB',(1024,500));pair.paste(north.crop((q*1024,3904,(q+1)*1024,4096)),(0,0));pair.paste(im.crop((q*1024,0,(q+1)*1024,308)),(0,192));pair.save(O/f'north-final-q{q}.png')
pair=Image.new('RGB',(650,720));pair.paste(north.crop((1970,3904,2620,4096)),(0,0));pair.paste(im.crop((1970,0,2620,528)),(0,192));pair.save(O/'north-final-local.png')
manifest={'base':{'path':str(bp),'sha256':sha(bp)},'baseContext':m['context'],'parentManifest':{'path':str(R/'trial/manifest.json'),'sha256':sha(R/'trial/manifest.json')},'repairs':entries,'candidate':{'path':str(dest),'sha256':sha(dest)},'context':{'path':str(cp),'sha256':sha(cp)},'north':m['north'],'west':m['west'],'changedPixels':int(np.any(out!=base,axis=2).sum()),'outsideMasksUnchanged':True,'east384Unchanged':True,'actualModel':None,'formalAccepted':False,'status':'trial_pending_visual_QA'}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(json.dumps(manifest))
