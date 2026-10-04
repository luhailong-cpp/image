from pathlib import Path
import json,hashlib,shutil,sys
from datetime import datetime,timezone
from PIL import Image
b=Path(__file__).resolve().parents[2];key=sys.argv[1];host=Path(sys.argv[2])
assert '/' not in key and '\\' not in key and '..' not in key
q=json.loads((b/'provenance/requests'/f'{key}.json').read_text(encoding='utf-8-sig'))
dst=b/'sources/new'/f'{key}.png';dst.parent.mkdir(exist_ok=True,parents=True)
assert not dst.exists()
shutil.copyfile(host,dst)
im=Image.open(dst);assert im.size==(1254,1254) and im.mode=='RGBA'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
r={'file':dst.relative_to(b).as_posix(),'sha256':sha(dst),'generatedAt':q['startedAt'],'recordedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'mode':im.mode,'format':im.format,'alphaExtrema':im.getchannel('A').getextrema(),'tool':'image_gen.imagegen','route':'builtin_host_managed','configuredTarget':q['configuredTarget'],'submittedParameters':q['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'内置无型号/质量选择器，返回未披露实际型号及质量','prompt':f'provenance/prompts/{key}.txt','references':[{'file':p,'sha256':sha(p),'purpose':'角色修正目标/09对应动作结构/身份/风格，详见实际提示词'}for p in q['submittedParameters']['referenced_image_paths']],'evidence':{'hostOutput':str(host),'toolResult':f'provenance/receipts/{key}.json'},'supersedes':q.get('supersedes'),'retainedTransform':q.get('retainedTransform'),'acceptance':'pending_visual_review'}
r['configSnapshot']=q.get('configSnapshot',json.loads((b.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig')))
r['submittedParameters']['model']=None
r['submittedParameters']['quality']=None
r['selectorAvailability']='model/quality selectors not exposed; null means not passed'
(b/'provenance/generation'/f'{key}.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'key':key,'sha256':r['sha256'],'size':im.size,'alpha':r['alphaExtrema']}))

