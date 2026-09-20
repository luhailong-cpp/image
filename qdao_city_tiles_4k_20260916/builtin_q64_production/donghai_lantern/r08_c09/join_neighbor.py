from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, importlib.util, sys
ROOT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
LEFT=Path(sys.argv[1]); RIGHT=ROOT/'output'/'extended-context.png'
OUT=ROOT/'joined_pair'; QA=OUT/'qa'; OUT.mkdir(exist_ok=True);QA.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('assembly',ROOT/'assemble_builtin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
a=np.array(Image.open(LEFT).convert('RGB'));b=np.array(Image.open(RIGHT).convert('RGB'))
assert a.shape==b.shape==(4326,4326,3)
pixels,metric=m.append_patch(a,b,m.load_seam_helper(),'cross_4k_r08_c08_c09')
im=Image.fromarray(pixels);assert im.size==(8422,4326)
outputs=[]
def save(name,img,role,box=None):
 p=OUT/name;img.save(p)
 e={'file':str(p),'sha256':sha(p),'pixels':list(img.size),'role':role}
 if box:e['cropXYXY']=box
 outputs.append(e);return p
save('extended-context-pair.png',im,'native_pair_before_outer_crop')
core=im.crop((115,115,8307,4211));save('paired-core8192x4096.png',core,'paired_4k_tiles_core',[115,115,8307,4211])
for ident,box in [('r08_c08',[115,115,4211,4211]),('r08_c09',[4211,115,8307,4211])]:
 save(ident+'.png',im.crop(box),'4096_candidate_cut_after_pair_join',box)
 x=0 if ident.endswith('08') else 4096
 save(ident+'-extended-context.png',im.crop((x,0,x+4326,4326)),'joined_neighbor_context',[x,0,x+4326,4326])
qa=[]
for i,y in enumerate([0,800,1600,2400,3196],1):
 box=[3646,y,4546,y+900];p=QA/f'cross-boundary-{i:02d}.png';core.crop(box).save(p);core.crop(box).save(p.with_suffix('.jpg'),quality=85)
 qa.append({'file':str(p),'sha256':sha(p),'kind':'native_pixel_crop','cropXYXY':box,'pixels':[900,900]})
p=QA/'overview.png';core.resize((1536,768),Image.Resampling.LANCZOS).save(p);Image.open(p).save(p.with_suffix('.jpg'),quality=85)
qa.append({'file':str(p),'sha256':sha(p),'kind':'overview_only_downsampled','pixels':[1536,768]})
manifest={'status':'candidate_pending_visual_QA_not_runtime_accepted','accepted':False,'runtimePublished':False,
 'scope':'Donghai adjacent r08_c08 and r08_c09 only, joined before 4096 cuts; other neighbor seams unverified',
 'sources':[{'path':str(p),'sha256':sha(p),'pixels':[4326,4326]} for p in (LEFT,RIGHT)],
 'composition':{'offsetXY':[4096,0],'overlap':230,'minimumErrorSeam':True,'featherPixels':2,'artResampling':False,'artUpscaling':False,'colorCorrection':False},
 'seamMetric':metric,'outputs':outputs,'qa':qa,'scriptSha256':sha(__file__)}
(OUT/'assembly.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for e in outputs:
 with Image.open(e['file']) as s:
  assert list(s.size)==e['pixels']
  if e.get('cropXYXY'):assert np.array_equal(np.array(s),np.array(im.crop(e['cropXYXY'])))
print(json.dumps({'passed':True,'outputs':outputs,'qaCount':len(qa)}))

