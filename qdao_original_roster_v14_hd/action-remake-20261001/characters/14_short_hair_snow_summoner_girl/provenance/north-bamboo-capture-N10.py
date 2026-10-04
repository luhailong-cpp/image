import json,hashlib
from pathlib import Path
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl")
p=R/'provenance/north-bamboo-native-sources.json';rows=json.loads(p.read_text(encoding='utf-8'))
fp=R/'run/N/10.png';m=json.loads(Path(str(fp)+'.generation.json').read_text(encoding='utf-8'));g=json.loads(Path(m['derivedFrom']['generationRecord']).read_text(encoding='utf-8'))
rows.append({'direction':'N','frame':'10','sourceSha256':g['sha256'],'oldFormalSha256':hashlib.sha256(fp.read_bytes()).hexdigest(),'oldGenerationRecord':m,'originalNativeRecord':g})
p.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

