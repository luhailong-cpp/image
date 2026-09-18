from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,shutil,hashlib
p=Path(__file__).resolve().parent;r=p/'repairs/v2'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
sources=json.loads(r'''[{"id":"tree_boundary","source":"C:\\Users\\luyua\\.codex\\generated_images\\01a0ad4d-500d-7c83-87fa-a0a2b62155fe\\exec-b34a3614-5bcc-4873-a3e5-b2d8dd2028c4.png"},{"id":"floor_boundary","source":"C:\\Users\\luyua\\.codex\\generated_images\\01a0ad4d-500d-7c83-87fa-a0a2b62155fe\\exec-219d59bf-c4f9-4a8e-b24e-515f0f034678.png"},{"id":"upper_stone_joints","source":"C:\\Users\\luyua\\.codex\\generated_images\\01a0ad4d-500d-7c83-87fa-a0a2b62155fe\\exec-753fb1f2-cda2-482a-9fd2-c878e96e9ad9.png"}]''')
refs=[r/'inputs'/f'{e["id"]}.jpg' for e in sources]
for i,e in enumerate(sources,1):
 src=Path(e['source']);f=r/'native'/f"{e['id']}.png";assert not f.exists();im=Image.open(src);assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[3]==(255,255);shutil.copyfile(src,f)
 prompt=r/'prompts'/f"{e['id']}.prompt.txt"
 record={'schemaVersion':2,'id':e['id'],'route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':[1254,1254],'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputPath':str(f),'outputSha256':sha(f),'promptPath':str(prompt),'promptSha256':sha(prompt),'submittedImages':[{'path':str(x),'sha256':sha(x)} for x in refs],'selectedTargetImageOneBased':i,'finalArtUpscaled':False,'resizedAfterGeneration':False,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':3,'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'visualQa':{'status':'native_geometry_reviewed_local_composite_pending'}}
 (r/'native'/f"{e['id']}.record.json").write_text(json.dumps(record,indent=2),encoding='utf-8')
print('Saved 3 original native repairs and exact provenance')
