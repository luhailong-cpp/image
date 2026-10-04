import json
from pathlib import Path
B=Path(__file__).resolve().parents[2]
inv=json.loads((B/'inventory-run-ne-cast.json').read_text(encoding='utf-8'))
for e in inv['frames']:
    r=json.loads((B/e['source_record']).read_text(encoding='utf-8-sig'))
    side={'file':e['path'],'sha256':e['sha256'],'generationRecord':e['source_record'],'derivedFrom':{'file':r['file'],'sha256':r['sha256'],'width':e['native_size'][0],'height':e['native_size'][1],'mode':'RGBA','format':'PNG'},'operation':'uniform full-canvas LANCZOS downsample; no crop, bbox scaling, translation, mirror, pose interpolation or alpha replacement','actualModel':r.get('actualModel'),'actualQuality':r.get('actualQuality'),'unverifiedReason':r.get('unverifiedReason','宿主未披露实际版本和质量')}
    (B/(e['path']+'.generation.json')).write_text(json.dumps(side,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('NE 16 formal sidecars aligned')
