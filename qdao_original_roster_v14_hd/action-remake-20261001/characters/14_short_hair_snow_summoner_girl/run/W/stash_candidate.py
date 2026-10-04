import argparse,json,hashlib,shutil
from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
BASE=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--key',required=True);p.add_argument('--source',required=True);p.add_argument('--reason',required=True);a=p.parse_args()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=Path(a.source);dest=BASE/'run/staging'/f'{a.key}.png';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
req=BASE/'provenance'/f'{a.key}.request.json';request=json.loads(req.read_text(encoding='utf-8'));im=Image.open(dest)
record={'file':dest.relative_to(BASE).as_posix(),'sha256':sha(dest),'generatedAt':datetime.now(timezone.utc).isoformat(),'generatedAtEvidence':'local output-copy observation; tool timestamp unavailable','width':im.width,'height':im.height,'nativeSize':list(im.size),'format':'PNG','mode':im.mode,'tool':'image_gen__imagegen','route':'builtin','configSnapshot':json.loads(Path('D:/work/image/config/image-generation.json').read_text(encoding='utf-8-sig')),'submittedParameters':{'model':None,'quality':None,**request['args']},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed; image_url/output_hint only, no model/quality selection or disclosed metadata','evidence':{'request':req.relative_to(BASE).as_posix(),'receipt':f'provenance/{a.key}.receipt.json'},'prompt':f'prompts/{a.key}.txt','references':[{'path':r,'sha256':sha(Path(r))} for r in request['args']['referenced_image_paths']],'review':{'status':'needs_pose_correction','reason':a.reason},'hostOutputPath':source.as_posix()}
Path(str(dest)+'.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');(BASE/'provenance'/f'{a.key}.generation.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8');print(dest.as_posix())
