from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import sys,json,shutil,hashlib
import numpy as np
p=Path(r'E:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\tianyong_festival\quad_r10_c07_c10');r=p/'repairs/v2'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
sources=json.loads(r'''[{"id":"boundary_lower","source":"C:\\Users\\luyua\\.codex\\generated_images\\01a0ad4d-500d-7c83-87fa-a0a2b62155fe\\exec-58073419-34c4-4963-8759-c544255c2511.png"},{"id":"stairs_boundary","source":"C:\\Users\\luyua\\.codex\\generated_images\\01a0ad4d-500d-7c83-87fa-a0a2b62155fe\\exec-ced4df42-b2fe-4174-95f6-8c7356c0ca41.png"}]''')
for i,e in enumerate(sources,1):
 src=Path(e['source']);f=r/'native'/f"{e['id']}.png";assert not f.exists();im=Image.open(src);assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255);shutil.copyfile(src,f)
 refs=[r/'inputs'/f'{name}.jpg' for name in ('boundary_lower','stairs_boundary')]
 prompt=r/'prompts'/f"{e['id']}.prompt.txt"
 record={'schemaVersion':2,'id':e['id'],'route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':[1254,1254],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputPath':str(f),'outputSha256':sha(f),'promptPath':str(prompt),'promptSha256':sha(prompt),'submittedImages':[{'path':str(x),'sha256':sha(x)} for x in refs],'selectedTargetImageOneBased':i,'finalArtUpscaled':False,'resizedAfterGeneration':False,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':2,'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'visualQa':{'status':'native_geometry_reviewed_local_composite_pending'}}
 (r/'native'/f"{e['id']}.record.json").write_text(json.dumps(record,indent=2),encoding='utf-8')
print('Saved 2 native repairs with actual 2 reference provenance')
