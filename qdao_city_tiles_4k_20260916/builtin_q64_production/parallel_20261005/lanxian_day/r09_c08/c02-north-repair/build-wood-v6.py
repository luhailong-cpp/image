from pathlib import Path
from PIL import Image
import sys,json,hashlib,shutil,numpy as np
sys.path.insert(0,r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');R=T/'c02-north-repair';O=R/'wood-v6';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receiptp=R/'wood03.receipt.json';receipt=json.loads(receiptp.read_text());src=Path(receipt['sourceOutputPath']);local=R/'wood-source03.png'
if not local.exists():shutil.copyfile(src,local)
pf=R/'wood03.prompt.txt';pf.write_text(receipt['prompt'],encoding='utf-8')
refs=[]
for ref in receipt['references']:
 q=Path(ref['path']);im=Image.open(q);refs.append(dict(ref,sha256=sha(q),width=im.width,height=im.height))
config=json.loads((T/'jobs/r01_c02.json').read_text(encoding='utf-8-sig'))['configSnapshot']
record={'file':str(local),'sha256':sha(local),'generatedAt':receipt['generatedAt'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'prompt':receipt['prompt'],'referenced_image_paths':[x['path'] for x in refs],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin exposes no model/quality selectors and result discloses neither.','prompt':str(pf),'promptSha256':sha(pf),'references':refs,'evidence':{'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'toolResultPath':str(receiptp),'toolResultSha256':sha(receiptp)},'status':'repair_native_source_pending_derived_join_review','formalAccepted':False}
(R/'wood03.generation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
prior=np.array(Image.open(R/'candidate-v4/candidate1254.png').convert('RGB'));base=np.array(Image.open(R/'original/native/r01_c02.png').convert('RGB'));wood=np.array(Image.open(local).convert('RGB'));northp=Path(json.loads((T/'regional/context.json').read_text())['northCore']['file']);north=Image.open(northp).convert('RGB')
f4=np.load(R/'candidate-v4/fields.npz');y,x=np.mgrid[:400,:1254].astype('float32');reg=cv2.remap(base,x+f4['geometry_dx'],y,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
restore=reg.copy();restore[115:400]=np.rint(np.clip(restore[115:400].astype(float)+f4['material_rgb'],0,255)).astype('uint8')
out=prior.copy();old=f4['wood_mask'];out[old]=np.concatenate([restore,base[400:]],axis=0)[old]
bm=np.array(Image.open(R/'wood03-edit-mask1254.png').convert('L'))>0;m=np.zeros((1254,1254),bool);m[115:400]=bm[627:912];out[:400][m[:400]]=wood[512:912][m[:400]]
out[:115]=np.array(north.crop((909,3981,2163,4096)));assert np.array_equal(out[400:],base[400:]);assert np.array_equal(out[:,873:],prior[:,873:])
Image.fromarray(out).save(O/'candidate1254.png');Image.fromarray(np.uint8(m)*255).save(O/'wood-mask.png');Image.fromarray(np.uint8(np.any(out!=prior,axis=2))*255).save(O/'changed-from-v4-mask.png')
joined=Image.new('RGB',(1254,512));joined.paste(north.crop((909,3840,2163,4096)),(0,0));joined.paste(Image.fromarray(out).crop((0,115,1254,371)),(0,256));joined.save(O/'north1254x512.png')
joined.crop((680,186,1010,386)).save(O/'stone-wood330x200.png');joined.crop((680,216,900,336)).save(O/'wood-top220x120.png');Image.fromarray(out).crop((620,90,930,450)).save(O/'wood-seat310x360.png')
Image.fromarray(wood).crop((620,602,930,962)).save(O/'wood-ai310x360.png');Image.fromarray(base).crop((620,90,930,450)).save(O/'wood-base310x360.png')
meta={'status':'candidate_pending_actual_review','sourceV4':{'file':str(R/'candidate-v4/candidate1254.png'),'sha256':sha(R/'candidate-v4/candidate1254.png')},'woodSource':record,'mask':{'file':str(O/'wood-mask.png'),'sha256':sha(O/'wood-mask.png'),'mapping':'source board (x,y+512), native nearest integer copy; only explicit selection mask used.'},'originalSeatAndSupportRetainedOutsideMask':True,'restoration':'Restore previous v4 wood02 region to base registration plus existing v4 material correction before copying wood03 selection.','allRows400To1253Exact':True,'north115Exact':True,'outputs':[{'file':str(q),'sha256':sha(q)} for q in O.glob('*.png')],'formalAccepted':False}
(O/'manifest.json').write_text(json.dumps(meta,indent=2),encoding='utf-8');print(json.dumps({'sha256':sha(O/'candidate1254.png'),'woodSourceSha256':sha(local)}))
