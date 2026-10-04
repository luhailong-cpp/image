from pathlib import Path
from PIL import Image
import json
b=Path(__file__).resolve().parents[2]
cfg=json.loads((b.parents[3]/'config/image-generation.json').read_text(encoding='utf-8-sig'))
for key in ['run-N-07-archer-v1','run-S-02-archer-v1','run-S-02-archer-v2','run-S-03-archer-v1','run-N-08-archer-v1']:
 p=b/'sources/new'/f'{key}.png';im=Image.open(p).convert('RGBA');a=im.getchannel('A').point(lambda x:255 if x>=128 else 0)
 print(key,a.getbbox())
 rpath=b/'provenance/generation'/f'{key}.json';r=json.loads(rpath.read_text(encoding='utf-8'))
 if 'configSnapshot'not in r:
  r['configSnapshot']=cfg;r['submittedParameters']['model']=None;r['submittedParameters']['quality']=None;r['selectorAvailability']='model/quality selectors not exposed; null means not passed'
  rpath.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')

