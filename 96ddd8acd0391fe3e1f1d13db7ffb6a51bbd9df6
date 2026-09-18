from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,shutil
p=Path(__file__).resolve().parent;r=p/'repairs/v3';src=Path(r'C:\Users\luyua\.codex\generated_images\01a0ad4d-500d-7c83-87fa-a0a2b62155fe\exec-8a508ba9-741e-414d-bce6-07013763602d.png');dst=r/'native/short_joint.png';assert not dst.exists()
im=Image.open(src);assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255);shutil.copyfile(src,dst)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
prompt=r/'prompts/short_joint.prompt.txt';ref=r/'inputs/short_joint.jpg'
record={'schemaVersion':2,'id':'short_joint','route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':[1254,1254],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputPath':str(dst),'outputSha256':sha(dst),'promptPath':str(prompt),'promptSha256':sha(prompt),'submittedImages':[{'path':str(ref),'sha256':sha(ref)}],'selectedTargetImageOneBased':1,'finalArtUpscaled':False,'resizedAfterGeneration':False,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':1,'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'visualQa':{'status':'native_complete_joints_observed_local_composite_pending'}}
(r/'native/short_joint.record.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
code=(p/'apply_repairs_v2.py').read_text(encoding='utf-8')
code=code.replace("out=p/'output_v2';qa=p/'qa_v2'","out=p/'output_v3';qa=p/'qa_v3'").replace("source=p/'output/vertical-extended-context.png'","source=p/'output_v2/vertical-extended-context.png'").replace("r=p/'repairs/v2'","r=p/'repairs/v3'").replace("quadsource=p/'output/row10-extended-context.png'","quadsource=p/'output_v2/row10-extended-context.png'").replace("'newNativeRepairs':3","'newNativeRepairs':1").replace("assembly_v2.json","assembly_v3.json")
start=code.index('placements=');end=code.index('\ntouched=',start)
code=code[:start]+"placements={'short_joint':{'box':(1421,0,2675,1254),'roi':(340,40,930,590),'edges':('left','right','top','bottom')}}"+code[end:]
(p/'apply_repairs_v3.py').write_text(code,encoding='utf-8')
print('Fourth repair saved and v3 composition prepared')
