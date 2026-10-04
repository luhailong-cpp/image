from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parents[2]
stamp=datetime.now(timezone.utc).isoformat()
records=[]
for action,dirs in [('cast',['E','W']),('run',['SE'])]:
 for direction in dirs:
  for n in range(1,17):
   p=ROOT/'frames'/action/direction/f'frame_{n:02}.png'
   sc=p.with_suffix('.generation.json')
   data=json.loads(sc.read_text(encoding='utf-8-sig'))
   sha=hashlib.sha256(p.read_bytes()).hexdigest()
   assert sha==data['sha256']
   with Image.open(p) as im:
    assert im.size==(1024,1024) and im.mode=='RGBA'
   notes=('逐帧连图与关键帧原尺寸复核：右手持杖、左臂盾，双脚/膝踝可读；W06/12/13缩杖已修，W13补收脚中间姿态。' if action=='cast' else '16帧已逐张AI修，01/09异侧落地、02/10平底承重、05/13蹬地、06-08/14-16短暂腾空；肩肘两次相反摆动保留解剖持手。逐帧来源和相位须结合整段再审，SHA差异未作独立姿态证据。')
   data['review']={'status':'visual_passed','automaticallyApproved':False,'reviewedAt':stamp,'scope':'single_frame_and_contact_sheet','note':notes,'dynamicSequenceStatus':'pending_root_browser_review','clientStatus':'not_integrated'}
   sc.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
   records.append({'action':action,'direction':direction,'frame':n,'path':p.relative_to(ROOT).as_posix(),'sha256':sha,'singleFrameStatus':'visual_passed','dynamicSequenceStatus':'pending_root_browser_review'})
 for direction in dirs:
  out=ROOT/'provenance'/action/f'{direction}_static_review_20261003.json'
  out.write_text(json.dumps({'reviewedAt':stamp,'timezone':'America/New_York','reviewer':'finish_se_cast','method':'actual view_image contact sheets and native targeted frames; not hash-based pose judgment','singleFramePassed':16,'dynamicSequenceStatus':'pending_root_browser_review','clientIntegration':'not_integrated','records':[x for x in records if x['action']==action and x['direction']==direction]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'staticReviewed':len(records),'dynamicPassed':0,'client':'not_integrated'}))
