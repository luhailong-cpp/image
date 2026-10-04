from pathlib import Path
import json
b=Path('D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
p=b/'run/W/09.png.generation.json'
r=json.loads(p.read_text(encoding='utf-8'));r['review']['status']='rejected-identity-drift-replaced-by-run-W-09-v2';r['review']['rejectionReason']='Short bob and robe length drift; corrected natively while preserving right contact phase.'
p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
(b/'provenance/run-W-09-v1.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')

