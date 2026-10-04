from pathlib import Path
from PIL import Image
import json,sys,hashlib,shutil
root=Path(__file__).parent
job=json.loads((root/sys.argv[1]).read_text(encoding='utf-8'))
src=Path(job['source']); dst=root/job['file']
if src.resolve()!=dst.resolve(): shutil.copy2(src,dst)
im=Image.open(dst)
config=json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig'))
record={**job,'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema() if im.mode=='RGBA' else None,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':job['references']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露实际型号及质量。配置目标不等于已提交或实测参数。','status':'native_generated_visual_review_pending'}
(dst.with_name(dst.name+'.generation.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(dst),'size':im.size,'mode':im.mode,'sha256':record['sha256']},ensure_ascii=False))

