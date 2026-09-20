from pathlib import Path
from PIL import Image
import json, hashlib
P=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production')
D=P/'lanxian_spring/triple_r08_c06_c08'
R=D/'repairs_v2_20260920'
assert not R.exists(), 'Version already exists; never overwrite'
for sub in ('guides','native','prompts'):(R/sub).mkdir(parents=True,exist_ok=True)
source=D/'output_v1/triple.png'
art=Image.open(source).convert('RGB')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
jobs=[]
for name,y in [('upper_gray',0),('middle_gray',1000),('lower_ivory',2000),('bottom_ivory',2842)]:
    box=[7565,y,8819,y+1254]
    f=R/'guides'/f'{name}.png';art.crop(box).save(f)
    jobs.append({'id':name,'rectTripleXYXY':box,'guide':str(f),'guideSha256':sha(f),'guidePixels':[1254,1254],'guideResampling':False})
(R/'plan.json').write_text(json.dumps({'schemaVersion':1,'appearance':'lanxian_spring','purpose':'Repair short grout breaks and abrupt surface brushwork along c07/c08','previousSource':str(source),'previousSourceSha256':sha(source),'route':'builtin_image_gen','configuredProduct':'ChatGPT Images 2.5','configuredModelTarget':'gpt-image-2.5-sunburst','configuredQualityTarget':'max','actualBackendModel':'unverified_host_managed','actualQualityPreset':'unverified_host_managed','separateBilledApiAuthorized':False,'jobs':jobs},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(str(R))
