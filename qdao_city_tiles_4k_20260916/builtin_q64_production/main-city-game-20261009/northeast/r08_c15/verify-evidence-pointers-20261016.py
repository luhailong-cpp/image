from pathlib import Path
import json,hashlib
T=Path(__file__).resolve().parent
for f in (T/'native').glob('*v20261016*.png.generation.json'):
 j=json.loads(f.read_text(encoding='utf-8-sig'));v=f.name.removesuffix('.png.generation.json')
 for key,choices in [('prompt',[T/'prompts'/(v+'.prompt.txt'),T/'prompts'/(v+'.txt')]),('evidence',[T/'receipts'/(v+'.receipt.json'),T/'prompts'/(v+'.receipt.json')])]:
  p=next((p for p in choices if p.exists()),None);assert p,(key,v);j[key]=str(p)
 j.setdefault('configSnapshot',{'entry':'builtin image_gen','modelSelectorExposed':False,'qualitySelectorExposed':False,'actualModel':None,'actualQuality':None,'currentRule':'free/included2.5 preferred, builtin2.0 allowed; no additional paid API'})
 f.write_text(json.dumps(j,indent=2)+'\n',encoding='utf-8')
 print(v)

