from pathlib import Path
from PIL import Image
import hashlib,json,sys,shutil,datetime
R=Path('E:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/lanxian_spring/triple_r08_c06_c08/repairs_v2_20260920')
name=sys.argv[1];host=Path(sys.argv[2]);out=R/'native'/f'{name}.png';record=out.with_suffix('.record.json')
assert not out.exists() and not record.exists()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
shutil.copy2(host,out);im=Image.open(out);assert im.size==(1254,1254);alpha=im.convert('RGBA').getchannel('A').getextrema();assert alpha==(255,255)
prompt=R/'prompts'/f'{name}.prompt.txt';ref=R/'guides'/f'{name}.png'
rec={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'appearance':'lanxian_spring','id':name,'role':'native_boundary_repair','sourceOutputPath':str(host),'outputPath':str(out),'outputSha256':sha(out),'sourceSha256':sha(host),'nativePixels':list(im.size),'opaque':True,'prompt':str(prompt),'promptSha256':sha(prompt),'promptText':prompt.read_text(encoding='utf8'),'actualInputCount':1,'actualInputs':[{'order':1,'role':'edit_target_exact_native_scale_crop','path':str(ref),'sha256':sha(ref),'pixels':[1254,1254]}],'tool':'builtin_image_gen','toolArguments':{'prompt':prompt.read_text(encoding='utf8').strip(),'referenced_image_paths':[str(ref).replace('\\','/')]},'configuredProduct':'ChatGPT Images 2.5','configuredModelTarget':'gpt-image-2.5-sunburst','configuredQualityTarget':'max','actualBackendModel':'unverified_host_managed_no_selector','actualQualityPreset':'unverified_host_managed_no_selector','separateBilledApiAuthorized':False,'sourceResampling':False,'sourceUpscaledTo4K':False,'status':'native_retained_pending_join_and_QA'}
record.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'record':str(record),'sha256':sha(record),'outputSha256':sha(out)}))
