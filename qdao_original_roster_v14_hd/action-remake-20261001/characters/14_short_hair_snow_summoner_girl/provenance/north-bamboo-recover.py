import json,shutil,hashlib
from pathlib import Path
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
rows=[]
for d,fs in {'NE':['01','02','03','04','05','09','10','11','12','13','15','16']}.items():
 for f in fs:
  formal=R/'run'/d/(f+'.png')
  rec=json.loads(Path(str(formal)+'.generation.json').read_text(encoding='utf-8'))
  gp=Path(rec['derivedFrom']['generationRecord'])
  gr=json.loads(gp.read_text(encoding='utf-8'))
  src=Path(gr['evidence']['toolReturnedPath'])
  dst=R/'run/staging'/('north-bamboo-source-'+d+'-'+f+'.png')
  shutil.copy2(src,dst)
  rows.append({'direction':d,'frame':f,'path':str(dst),'cacheSource':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'oldFormalSha256':hashlib.sha256(formal.read_bytes()).hexdigest(),'oldGenerationRecord':rec,'originalNativeRecord':gr})
(R/'provenance/north-bamboo-native-sources.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'direction':r['direction'],'frame':r['frame'],'path':r['path']} for r in rows]))

