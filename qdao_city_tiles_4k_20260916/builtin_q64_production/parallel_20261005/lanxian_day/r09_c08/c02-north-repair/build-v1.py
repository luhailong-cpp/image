from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json,shutil,numpy as np
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08');R=T/'c02-north-repair';O=R/'candidate-v1';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receiptp=R/'attempt01.receipt.json';receipt=json.loads(receiptp.read_text());src=Path(receipt['sourceOutputPath'])
assert not (R/'native-source01.png').exists();shutil.copyfile(src,R/'native-source01.png');pf=R/'attempt01.prompt.txt';pf.write_text(receipt['prompt'],encoding='utf-8')
refs=[]
for ref in receipt['references']:
 q=Path(ref['path']);im=Image.open(q);refs.append(dict(ref,sha256=sha(q),width=im.width,height=im.height))
config=json.loads((T/'jobs/r01_c02.json').read_text(encoding='utf-8-sig'))['configSnapshot']
record={'file':str(R/'native-source01.png'),'sha256':sha(src),'generatedAt':receipt['generatedAt'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'prompt':receipt['prompt'],'referenced_image_paths':[x['path'] for x in refs],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'Builtin exposes no model/quality selectors and result discloses neither.','prompt':str(pf),'promptSha256':sha(pf),'references':refs,'evidence':{'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'toolResultPath':str(receiptp),'toolResultSha256':sha(receiptp)},'status':'repair_native_source_pending_derived_join_review','formalAccepted':False}
(R/'attempt01.generation.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
basep=T/'native/r01_c02.png';eastp=T/'native/r01_c03.png';ctx=json.loads((T/'regional/context.json').read_text());northp=Path(ctx['northCore']['file'])
base=Image.open(basep).convert('RGB');repair=Image.open(src).convert('RGB');north=Image.open(northp).convert('RGB');east=Image.open(eastp).convert('RGB')
out=base.copy();out.paste(repair.crop((0,627,1139,892)),(0,115));out.paste(north.crop((909,3981,2163,4096)),(0,0));out.paste(east.crop((115,115,230,1254)),(1139,115))
out.save(O/'candidate1254.png')
joined=Image.new('RGB',(1254,512));joined.paste(north.crop((909,3840,2163,4096)),(0,0));joined.paste(out.crop((0,115,1254,371)),(0,256))
scopes=[('north1254x512',joined),('bottom1254x160',out.crop((0,300,1254,460))),('east256x512',out.crop((1011,0,1254,512)))]
for name,im in scopes:im.save(O/(name+'.png'))
for name,box in [('orange',[0,216,380,336]),('wood',[350,216,750,336]),('stone',[720,206,1010,346]),('leaves',[990,206,1254,346])]:joined.crop(box).save(O/(name+'.png'))
manifest={'operation':'Native integer patch only. AI bottom source rows627..891 to cell115..379 excluding exact east115; authoritative north115 and east115 copied at integer coordinates. No geometry/color correction yet.','base':{'file':str(basep),'sha256':sha(basep)},'repair':record,'north':{'file':str(northp),'sha256':sha(northp)},'east':{'file':str(eastp),'sha256':sha(eastp)},'outputs':[{ 'file':str(q),'sha256':sha(q)} for q in O.glob('*.png')],'formalAccepted':False,'reviewPending':True}
(O/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({'candidate':str(O/'candidate1254.png'),'sha256':sha(O/'candidate1254.png')}))

