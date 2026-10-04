import json,shutil,hashlib,importlib.util
from pathlib import Path
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl")
rows=json.loads((R/'provenance/north-bamboo-native-sources.json').read_text(encoding='utf-8'))
for d,fs in {'N':{'03':2,'06':3,'07':3,'11':2,'14':3,'15':3},'NW':{'03':1,'11':1}}.items():
 reg=json.loads((R/'run'/d/'registration.json').read_text())
 for f,v in fs.items():
  gr=json.loads((R/'run/staging'/f'run-{d}-{f}-v{v}.png.generation.json').read_text())
  src=Path(gr['evidence']['toolReturnedPath']);dst=R/'run/staging'/f'north-bamboo-source-{d}-{f}.png';shutil.copy2(src,dst)
  old=json.loads((R/'run'/d/(f+'.png.generation.json')).read_text())
  rg=next(x for x in reg['frames'] if x['file']==f'run/{d}/{f}.png')
  rows.append({'direction':d,'frame':f,'path':str(dst),'cacheSource':str(src),'sourceSha256':hashlib.sha256(src.read_bytes()).hexdigest(),'oldFormalSha256':old['registrationTransform']['inputRegisteredReferenceSha256'],'oldRegistrationRow':rg,'originalNativeRecord':gr})
(R/'provenance/north-bamboo-native-sources.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print('Recovered '+str(len(rows))+' sources')

