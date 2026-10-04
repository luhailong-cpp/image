import json
from pathlib import Path
ROOT=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/06_thunder_caster_boy').resolve()
p=(ROOT/'work/run_E_00_v1.png').resolve()
assert p.is_relative_to(ROOT) and p.name=='run_E_00_v1.png'
rp=p.with_name(p.name+'.generation.json')
r=json.loads(rp.read_text(encoding='utf-8'))
r['retention']={'status':'rejected_image_removed_after_v2_export_verified','replacement':'runtime/run/E/00.png','reason':'触地姿态仍像腾空、靴跟过低；已由原生v2替代，保留本逐图文字来源记录。'}
assert (ROOT/'runtime/run/E/00.png').exists() and (ROOT/'work/run_E_00_v2.png.generation.json').exists()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if p.exists(): p.unlink()
print('Rejected v1 workspace PNG removed; generation record retained.')

