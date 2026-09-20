from pathlib import Path
from PIL import Image
import numpy as np, json, hashlib, importlib.util
L=Path(__file__).resolve().parent;R=L/'cross_seam_repair';B=L/'cloth_seam_repair';OUT=L/'joined_pair_v3';QA=OUT/'qa'
OUT.mkdir(exist_ok=True);QA.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(n,p):
 spec=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
m=module('assembly',L/'assemble_builtin.py');reg=module('join',L.parents[1]/'tools/mechanical_join.py')
def source(p):
 r=json.loads(p.read_text());im=Image.open(r['outputPath']);assert im.size==(1254,1254)
 assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
 assert sha(r['outputPath'])==r['outputSha256']==sha(r['sourceOutputPath'])
 for k,h in [('promptPath','promptSha256'),('guidePath','guideSha256'),('submittedReferencePath','submittedReferenceSha256')]:assert sha(r[k])==r[h]
 for a in r['actualInputReferences']:assert sha(a['path'])==a['sha256']
 return np.array(im.convert('RGB')),{'file':str(p),'sha256':sha(p)}
entries=[];patches=[]
for i in range(1,5):
 a,r=source(R/'native'/f'seam_r{i:02d}.record.json');patches.append(a);entries.append(r)
strip=patches[0].transpose(1,0,2);metrics=[]
for i,p in enumerate(patches[1:],2):
 strip,v=m.append_patch(strip,p.transpose(1,0,2),m.load_seam_helper(),f'cross_strip_row_{i}');metrics.append(v)
strip=strip.transpose(1,0,2)
base=L/'joined_pair/extended-context-pair.png';original=np.array(Image.open(base).convert('RGB'));pixels=original.copy();reports=[]
def insert(patch,box,edges,name):
 x0,y0,x1,y1=box;context=pixels[y0:y1,x0:x1].copy();h,w=context.shape[:2];yy,xx=np.mgrid[:h,:w]
 ds={'left':xx,'right':w-1-xx,'top':yy,'bottom':h-1-yy}
 dist=np.minimum.reduce([ds[e] for e in edges]);v=np.clip((dist-24)/144,0,1);v=v*v*(3-2*v);mask=np.rint(v*255).astype(np.uint8)
 result,flow,tone,report=reg.registered_join(context,patch,mask,edges=edges,max_shift=8,flow_inner=300,flow_full=120,tone_inner=330,tone_full=150,match_tone=True)
 pixels[y0:y1,x0:x1]=result
 Image.fromarray(mask).save(OUT/(name+'-mask.png'))
 reports.append(dict(id=name,boxXYXY=box,mechanical=report))
insert(strip,[3584,0,4838,4326],('left','right'),'cross_4k_strip')
for name,y in [('cloth_upper',512),('cloth_lower',1536)]:
 patch,r=source(B/'native'/f'{name}.record.json');entries.append(r)
 insert(patch,[7168,y,8422,y+1254],('left','right','top','bottom'),name)
assert np.array_equal(pixels[:,:3584],original[:,:3584])
assert np.array_equal(pixels[:,4838:7168],original[:,4838:7168])
im=Image.fromarray(pixels);outputs=[]
def save(name,img,role,box=None):
 p=OUT/name;img.save(p);e=dict(file=str(p),sha256=sha(p),pixels=list(img.size),role=role)
 if box:e['cropXYXY']=box
 outputs.append(e)
save('extended-context-pair.png',im,'native_pair_with_six_native_repairs_and_registered_edges')
core=im.crop((115,115,8307,4211));save('paired-core8192x4096.png',core,'paired_4k_tiles_core',[115,115,8307,4211])
for ident,box in [('r08_c08',[115,115,4211,4211]),('r08_c09',[4211,115,8307,4211])]:
 save(ident+'.png',im.crop(box),'4096_candidate_cut_after_pair_native_repair',box)
 x=0 if ident.endswith('08') else 4096
 save(ident+'-extended-context.png',im.crop((x,0,x+4326,4326)),'joined_neighbor_context',[x,0,x+4326,4326])
qa=[]
boxes=[(f'cross-and-insertion-{i}',[3196,y,4996,y+900]) for i,y in enumerate([0,800,1600,2400,3196],1)]
boxes += [(n,[x-115,y-115,x+1254-115,y+1254-115]) for n,x,y in [('cloth_upper',7168,512),('cloth_lower',7168,1536)]]
for name,box in boxes:
 p=QA/(name+'.png')
 if name.startswith('cloth_'):box=[v+115 for v in box];crop=im.crop(box)
 else:crop=core.crop(box)
 crop.save(p);crop.save(p.with_suffix('.jpg'),quality=85)
 qa.append(dict(file=str(p),sha256=sha(p),pixels=list(crop.size),cropXYXY=box,kind='native_pixel_crop',coordinateSpace='extended_pair' if name.startswith('cloth_') else 'paired_core'))
p=QA/'overview.png';core.resize((1536,768),Image.Resampling.LANCZOS).save(p);Image.open(p).save(p.with_suffix('.jpg'),quality=85);qa.append(dict(file=str(p),sha256=sha(p),pixels=[1536,768],kind='overview_only_downsampled'))
manifest=dict(status='candidate_pending_visual_QA_not_runtime_accepted',accepted=False,runtimePublished=False,sources=[dict(path=str(base),sha256=sha(base))],nativeRepairRecords=entries,composition=dict(artUpscaling=False,artResampling='Limited subpixel registration only at repaired edges; native patch interiors unchanged',localColorCorrection='Maximum18RGB near repair edges only, taper to zero at330pixels',minimumErrorSeamInsideStrip=True,overlap=230,featherInsideStripPixels=2),registeredRepairs=reports,seamMetrics=metrics,outputs=outputs,qa=qa,scriptSha256=sha(__file__),scope='Donghai lantern r08_c08 and r08_c09 candidates only. Other outer neighbors and runtime unverified.')
(OUT/'assembly.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for e in outputs:
 assert sha(e['file'])==e['sha256']
 if e.get('cropXYXY'):assert np.array_equal(np.array(Image.open(e['file'])),np.array(im.crop(e['cropXYXY'])))
print(json.dumps({'passed':True,'outputs':outputs,'repairCount':len(entries),'qaCount':len(qa)}))

