import json,shutil,hashlib,sys
from pathlib import Path
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl")
for q in json.loads((R/'provenance/north-bamboo-native-selection.json').read_text(encoding='utf-8')):
 if len(sys.argv)>1 and q['direction']!=sys.argv[1]:continue
 src=R/'run/staging'/(q['id']+'-registered.png');dst=R/'run'/q['direction']/(q['frame']+'.png')
 rec=json.loads(Path(str(src)+'.generation.json').read_text(encoding='utf-8'))
 assert rec['sha256']==hashlib.sha256(src.read_bytes()).hexdigest()
 if dst.exists() and hashlib.sha256(dst.read_bytes()).hexdigest()==rec['sha256']:
  print('unchanged '+str(dst));continue
 shutil.copy2(src,dst);rec['file']=dst.relative_to(R).as_posix();rec['registrationTransform']['file']=rec['file'];rec['registrationTransform']['status']='applied';rec['review']={'status':'visual_pass','notes':q['review'],'independentFinalReview':'pending_parent_review'}
 Path(str(dst)+'.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf-8')
 gp=Path(rec['derivedFrom']['generationRecord']);g=json.loads(gp.read_text(encoding='utf-8'));g['review']={'status':'selected_final','finalDerivative':rec['file'],'notes':q['review']};gp.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
 print(rec['file']+' '+rec['sha256'])

