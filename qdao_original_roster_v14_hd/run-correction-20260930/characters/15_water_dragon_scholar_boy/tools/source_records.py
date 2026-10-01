from pathlib import Path
from PIL import Image
import json, hashlib, datetime, subprocess
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT.parents[3]
CLIENT=WORK.parent/'mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV14/15_water_dragon_scholar_boy'
PYTHON='C:/Users/Administrator/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def details(p):
 im=Image.open(p)
 return dict(file=str(p),sha256=sha(p),width=im.width,height=im.height,format=im.format,mode=im.mode,alpha_gt_8_bbox=im.convert('RGBA').getchannel('A').point(lambda v:255 if v>8 else 0).getbbox())
if __name__=='__main__':
 import sys, shutil
 cmd=sys.argv[1]
 if cmd=='baseline':
  files=[CLIENT/'appearance.json', CLIENT/'walk/E/01.png.meta']+[CLIENT/f'walk/{d}/{f:02}.png' for d in ['E','SE'] for f in [1,5,9,13,16]]+[CLIENT/'idle/S.png',WORK/'designs/jubaozhai-ui/02-characters.png']
  write(ROOT/'baseline-source.json',dict(recordedAt=now(),character='15_water_dragon_scholar_boy',files=[{**dict(file=str(p),sha256=sha(p),lastModified=datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat()),**(details(p) if p.suffix=='.png' else {})} for p in files],clientAppearance=json.loads((CLIENT/'appearance.json').read_text(encoding='utf-8'))))
 elif cmd=='record':
  direction,frame,version,hostfile=sys.argv[2:]
  stem=ROOT/f'generation/{direction}/{int(frame):02}-v{version}'
  target=stem.with_suffix('.png')
  if not target.exists(): shutil.copy2(hostfile,target)
  request=json.loads(stem.with_suffix('.request.json').read_text(encoding='utf-8'))
  meta=details(target)
  write(Path(str(target)+'.generation.json'),dict(**meta,generatedAt=now(),tool='image_gen.imagegen',route='builtin',configSnapshot=json.loads((ROOT/'generation/config-snapshot.json').read_text(encoding='utf-8')),submittedParameters=dict(model=None,quality=None,**request),actualModel=None,actualQuality=None,unverifiedReason='Host managed; tool exposes no model/quality selectors or returned model metadata.',prompt=str(stem.with_suffix('.prompt.txt')),references=[dict(file=r,sha256=sha(Path(r)),purpose=('selected E cel identity and scale' if '/generation/' in r else 'approved primary style' if '/designs/' in r else 'original character identity and anatomical hand ownership')) for r in request['referenced_image_paths']],evidence=dict(hostOutput=hostfile,toolResult=str(stem.with_suffix('.tool-result.json'))),acceptance='pending_visual_and_dynamic_review'))
  print(json.dumps(meta))
