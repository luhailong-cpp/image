from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,importlib.util
R=Path(__file__).resolve().parent;L=R.parent;OUT=L/'joined_pair_v2';QA=OUT/'qa'
OUT.mkdir(exist_ok=True);QA.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('assembly',L/'assemble_builtin.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
entries=[];patches=[]
for i in range(1,5):
 rf=R/'native'/f'seam_r{i:02d}.record.json';r=json.loads(rf.read_text());p=Path(r['outputPath'])
 assert sha(p)==r['outputSha256']==sha(r['sourceOutputPath'])
 for k,h in [('promptPath','promptSha256'),('guidePath','guideSha256'),('submittedReferencePath','submittedReferenceSha256')]:assert sha(r[k])==r[h]
 for ref in r['actualInputReferences']:assert sha(ref['path'])==ref['sha256']
 im=Image.open(p);assert im.size==(1254,1254)
 if 'A' in im.getbands():assert im.getchannel('A').getextrema()==(255,255)
 patches.append(np.array(im.convert('RGB')));entries.append({'file':str(rf),'sha256':sha(rf)})
fn=m.load_seam_helper();strip=patches[0].transpose(1,0,2);metrics=[]
for i,p in enumerate(patches[1:],2):
 strip,metric=m.append_patch(strip,p.transpose(1,0,2),fn,f'repair_vertical_{i}');metrics.append(metric)
strip=strip.transpose(1,0,2);assert strip.shape==(4326,1254,3)
basepath=L/'joined_pair/extended-context-pair.png';base=np.array(Image.open(basepath).convert('RGB'))
pixels,metric=m.append_patch(base[:,:3814],strip,fn,'insert_left_border');metrics.append(metric)
pixels,metric=m.append_patch(pixels,base[:,4608:],fn,'insert_right_border');metrics.append(metric)
assert pixels.shape==base.shape==(4326,8422,3)
assert np.array_equal(pixels[:,:3584],base[:,:3584]) and np.array_equal(pixels[:,4838:],base[:,4838:])
im=Image.fromarray(pixels);outputs=[]
def save(name,img,role,box=None):
 p=OUT/name;img.save(p);e={'file':str(p),'sha256':sha(p),'pixels':list(img.size),'role':role}
 if box:e['cropXYXY']=box
 outputs.append(e)
save('extended-context-pair.png',im,'native_pair_with_four_native_seam_repairs')
core=im.crop((115,115,8307,4211));save('paired-core8192x4096.png',core,'paired_4k_tiles_core',[115,115,8307,4211])
for ident,box in [('r08_c08',[115,115,4211,4211]),('r08_c09',[4211,115,8307,4211])]:
 save(ident+'.png',im.crop(box),'4096_candidate_cut_after_native_pair_repair',box)
 x=0 if ident.endswith('08') else 4096
 save(ident+'-extended-context.png',im.crop((x,0,x+4326,4326)),'joined_neighbor_context',[x,0,x+4326,4326])
qa=[]
for i,y in enumerate([0,800,1600,2400,3196],1):
 box=[3196,y,4996,y+900];p=QA/f'repair-and-insertion-edges-{i:02d}.png';crop=core.crop(box);crop.save(p);crop.save(p.with_suffix('.jpg'),quality=85)
 qa.append({'file':str(p),'sha256':sha(p),'pixels':[1800,900],'cropXYXY':box,'kind':'native_pixel_crop_including_both_insertion_edges'})
p=QA/'overview.png';core.resize((1536,768),Image.Resampling.LANCZOS).save(p);Image.open(p).save(p.with_suffix('.jpg'),quality=85)
qa.append({'file':str(p),'sha256':sha(p),'pixels':[1536,768],'kind':'overview_only_downsampled'})
manifest={'status':'candidate_pending_visual_QA_not_runtime_accepted','accepted':False,'runtimePublished':False,'sources':[{'path':str(basepath),'sha256':sha(basepath)}],'nativeRepairRecords':entries,'composition':{'repairStripBoxXYXY':[3584,0,4838,4326],'minimumErrorSeam':True,'overlap':230,'featherPixels':2,'artResampling':False,'artUpscaling':False,'colorCorrection':False,'outsideRepairStripUnchanged':True},'seamMetrics':metrics,'outputs':outputs,'qa':qa,'scriptSha256':sha(__file__),'scope':'Two neighboring Donghai lantern candidates r08_c08,c09. Only shared boundary reviewed; other neighbors and runtime not accepted.'}
(OUT/'assembly.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
for e in outputs:
 with Image.open(e['file']) as s:
  assert list(s.size)==e['pixels']
  if e.get('cropXYXY'):assert np.array_equal(np.array(s),np.array(im.crop(e['cropXYXY'])))
print(json.dumps({'passed':True,'outputs':outputs,'repairNativeCount':4,'qaCount':len(qa)}))

