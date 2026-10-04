from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[2]
positions=['front_landing','under_hip','behind_hip','rear_push']
for direction in ['NE','SE']:
 p=B/'grounding4'/direction/'selection-new.json'
 if not p.exists():continue
 srcs=json.loads(p.read_text(encoding='utf-8'))
 out=[]
 for idx,src in enumerate(srcs):
  f=B/src; rec=json.loads(Path(str(f)+'.generation.json').read_text(encoding='utf-8-sig'))
  native=rec.get('derivativeOf',src)
  requested=Path(src).stem
  out.append({'frame':idx+1,'selectedSlot':idx+1,'requestedSlot':requested,'exportFile':src,'nativeFile':native,'generationRecord':src+'.generation.json','nativeGenerationRecord':rec.get('generationRecord',src+'.generation.json'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'supportFoot':('right' if idx<8 else 'left') if direction=='NE' else ('left' if idx<8 else 'right'),'position':positions[(idx%8)//2],'mode':'retain' if src.startswith('runtime/') and int(f.stem)==idx+1 else 'replace_or_rephase','visualStaticReviewed':True,'dynamicReviewed':False,'contact':'连续接地，按图片实际支撑腿选相位，非按请求标签验收'})
 (B/'grounding4'/direction/'selected.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(direction,len(out),len(set(x['sha256'] for x in out)))

