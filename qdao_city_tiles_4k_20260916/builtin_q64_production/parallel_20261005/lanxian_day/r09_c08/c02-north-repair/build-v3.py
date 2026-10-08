from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import sys,hashlib,json,shutil,numpy as np
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');R=T/'c02-north-repair';O=R/'candidate-v3';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receiptp=R/'wood02.receipt.json';receipt=json.loads(receiptp.read_text());src=Path(receipt['sourceOutputPath']);local=R/'wood-source02.png'
if not local.exists():shutil.copyfile(src,local)
pf=R/'wood02.prompt.txt';pf.write_text(receipt['prompt'],encoding='utf-8')
refs=[]
for ref in receipt['references']:
 q=Path(ref['path']);im=Image.open(q);refs.append(dict(ref,sha256=sha(q),width=im.width,height=im.height))
config=json.loads((T/'jobs/r01_c02.json').read_text(encoding='utf-8-sig'))['configSnapshot']
record={'file':str(local),'sha256':sha(local),'generatedAt':receipt['generatedAt'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'prompt':receipt['prompt'],'referenced_image_paths':[x['path'] for x in refs],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin exposes no model/quality selectors and result discloses neither.','prompt':str(pf),'promptSha256':sha(pf),'references':refs,'evidence':{'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'toolResultPath':str(receiptp),'toolResultSha256':sha(receiptp)},'status':'repair_native_source_pending_derived_join_review','formalAccepted':False}
(R/'wood02.generation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
basep=R/'original/native/r01_c02.png';eastp=T/'native/r01_c03.png';ctx=json.loads((T/'regional/context.json').read_text());northp=Path(ctx['northCore']['file'])
a=np.array(Image.open(basep).convert('RGB'));east=np.array(Image.open(eastp).convert('RGB'));wood=np.array(Image.open(local).convert('RGB'));north=Image.open(northp).convert('RGB')
y,x=np.mgrid[:1254,:1254].astype(np.float32)
knots=[(0,0),(110,0),(158,-3),(175,-2),(182,-2),(280,0),(294,2),(304,-2),(321,4),(326,3),(345,0),(417,-1),(450,0),(501,8),(512,5),(560,0),(720,0),(910,0),(930,0),(955,8),(960,11),(965,11),(976,6),(1001,1),(1024,0),(1253,0)]
dx0=np.interp(np.arange(1254),[k[0] for k in knots],[k[1] for k in knots]);depth=np.clip((y-115)/220,0,1);fade=1-depth*depth*(3-2*depth);fade[y>=400]=0
dx=dx0[None]*fade;warped=cv2.remap(a,(x+dx).astype(np.float32),y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
out=a.copy();out[115:400,:1139]=warped[115:400,:1139]
out[115:350,680:870]=wood[627:862,680:870]
out[115:300,1024:1254]=east[115:300,0:230]
out[:115]=np.array(north.crop((909,3981,2163,4096)));out[115:400,1139:]=east[115:400,115:230]
assert np.array_equal(out[400:],a[400:])
Image.fromarray(out).save(O/'candidate1254.png');np.savez_compressed(O/'geometry-fields.npz',dx=dx[:400].astype(np.float32));Image.fromarray(np.uint8(np.any(out!=a,axis=2)*255)).save(O/'edit-mask.png')
joined=Image.new('RGB',(1254,512));joined.paste(north.crop((909,3840,2163,4096)),(0,0));joined.paste(Image.fromarray(out).crop((0,115,1254,371)),(0,256));joined.save(O/'north1254x512.png')
for name,box in [('orange',[0,216,380,336]),('wood',[350,216,750,336]),('stone',[680,186,1010,386]),('leaves',[990,206,1254,346])]:joined.crop(box).save(O/(name+'.png'))
Image.fromarray(out).crop((0,300,1254,460)).save(O/'bottom1254x160.png');Image.fromarray(out).crop((620,115,930,400)).save(O/'wood-patch310x285.png')
meta={'status':'geometry_candidate_before_color_not_adopted','sources':{'base':{'file':str(basep),'sha256':sha(basep)},'wood02':record,'north':{'file':str(northp),'sha256':sha(northp)},'east':{'file':str(eastp),'sha256':sha(eastp)}},'geometry':{'manualSourceDxKnots':knots,'maximumAbsDx':float(np.abs(dx).max()),'dy':0,'fade':'smoothstep y115..335 tozero; no image blur','resampling':'Bilinear base-source registration only; copied AI wood and neighbor foliage remain native integer samples'},'woodPatch':{'sourceBox':[680,627,870,862],'destinationBox':[680,115,870,350]},'eastLeafReuse':{'sourceBox':[0,115,230,300],'destinationBox':[1024,115,1254,300],'operation':'Existing selected neighbor native overlap reused 1:1; no enlargement, no model call'},'northLock':'All real115 rows exact','eastLock':'Right115 exact only115..399','unchangedRows400To1253Verified':True,'outputs':[{'file':str(f),'sha256':sha(f)} for f in O.glob('*.png')],'field':{'file':str(O/'geometry-fields.npz'),'sha256':sha(O/'geometry-fields.npz')},'formalAccepted':False}
(O/'manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps({'candidate':str(O/'candidate1254.png'),'sha256':sha(O/'candidate1254.png')}))

