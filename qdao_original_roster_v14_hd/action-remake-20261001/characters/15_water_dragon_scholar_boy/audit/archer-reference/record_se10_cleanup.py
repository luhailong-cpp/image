from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[2]
key,host=sys.argv[1:3]
dst=b/'sources/new'/f'{key}.png'
assert not dst.exists(),str(dst)
shutil.copy2(host,dst)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q=json.loads((b/'provenance/requests'/f'{key}.json').read_text(encoding='utf-8'))
im=Image.open(dst);a=im.getchannel('A').point(lambda x:255 if x>=128 else 0)
old=b/'sources/new/run-SE-10-archer-v1.png';om=Image.open(old)
rec={'file':str(dst.relative_to(b)).replace('\\','/'),'sha256':sha(dst),'generatedAt':q['startedAt'],'recordedAt':datetime.now(timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'alphaExtrema':im.getchannel('A').getextrema(),'nativeAlphaBBox':a.getbbox(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8')),'submittedParameters':q['submittedParameters'],'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具没有型号/质量选择器，回执未披露实际型号/质量。','prompt':f'provenance/prompts/{key}.txt','references':[{'file':p,'sha256':sha(p),'purpose':['original edit target and framing authority','character identity only','confirmed material/style only','09 SE motion structure only'][i]}for i,p in enumerate(q['submittedParameters']['referenced_image_paths'])],'evidence':{'hostOutput':host,'toolResult':f'provenance/receipts/{key}.json','request':f'provenance/requests/{key}.json'},'editedFrom':{'file':str(old.relative_to(b)).replace('\\','/'),'sha256':sha(old),'generationRecord':'provenance/generation/run-SE-10-archer-v1.json'},'acceptance':'candidate_pending_parent_review','originalAlphaBBox':om.getchannel('A').point(lambda x:255 if x>=128 else 0).getbbox()}
(b/'provenance/generation'/f'{key}.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:rec[k]for k in ['file','sha256','width','height','nativeAlphaBBox','originalAlphaBBox']},ensure_ascii=False))
