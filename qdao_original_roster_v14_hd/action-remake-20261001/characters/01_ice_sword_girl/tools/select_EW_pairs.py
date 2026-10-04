from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/01_ice_sword_girl")
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def build(direction,versions,notes,issues=[]):
 frames=[]
 names=['前落地','前落地压重','身体靠近支撑脚','身体靠近支撑脚第二姿态','身体经过支撑脚','身体经过后继续支撑','后方前掌支撑','后方前掌支撑后段']
 for i,v in enumerate(versions,1):
  p=R/f'drafts/run/{direction}/{i:02}-v{v}.png'
  rec=p.with_name(p.name+'.generation.json')
  if not p.exists() or not rec.exists():raise RuntimeError(p)
  info=json.loads(rec.read_text(encoding='utf-8-sig'));digest=hashlib.sha256(p.read_bytes()).hexdigest()
  if digest!=info['sha256']:raise RuntimeError('hash mismatch')
  support=('right' if direction=='E' else 'left') if i<=8 else ('left' if direction=='E' else 'right')
  phase=(i-1)%8
  contact='forefoot_support' if phase>=6 else 'full_sole_weight'
  observed={'left':'air','right':'air',support:contact,'confidence':'manual_visual_native_and_fullcanvas_sequence_inspection_not_client_collision','evidence':notes[i-1]}
  frames.append({'frame':i,'path':p.relative_to(R).as_posix(),'sourcePath':p.relative_to(R).as_posix(),'sha256':digest,'nativeSize':list(Image.open(p).size),'generationRecord':rec.relative_to(R).as_posix(),'durationMs':75,'actualContact':observed,'plannedPhase':names[phase],'positionPair':(i-1)//2+1,'notes':notes[i-1],'staticInspected':True,'actualModel':None,'actualQuality':None})
 data={'schemaVersion':2,'characterId':'01_ice_sword_girl','action':'run','direction':direction,'createdAt':datetime.now(timezone.utc).isoformat(),'canvasSize':[1024,1024],'nativeCanvasSize':[1254,1254],'timing':{'uniformCycleMs':1200,'frameDurationsMs':[75]*16,'phaseWeights':False,'offlineDefaultApplied':True,'clientVerified':False},'artStatus':'paired_support_static_reviewed_dynamic_review_pending','eightConsecutiveSupportVerified':False,'positionPairsVerified':False,'staticEightContinuousSupportObserved':True,'dynamicArtAccepted':False,'clientIntegrated':False,'clientRuntimeVerified':False,'remainingIssues':issues,'root':{'status':'no_registration_applied','registrationApplied':False,'definition':'Full original canvas retained. No lowest-alpha/foot alignment, no whole-sprite offset.'},'frames':frames}
 write(R/f'review/run-{direction}-selection.json',data)
 return data
E_notes=[
'近右前靴全掌落地，远左靴后折离地；保留原正确帧。',
'近右前靴全掌压重，膝缓冲，远左后靴离地；保留原正确帧。',
'近右全掌支撑，脚相对骨盆由前向中；远左后靴上收。原正确手臂保持。',
'04-v6把原后蹬改为近右脚全掌支撑，近右膝柔和弯曲，远左靴仍抬起；剑符手链保留。',
'05-v4近右全掌在骨盆下承重，远左膝开始前摆、靴抬起；未提前前掌蹬离。',
'06-v3后方近右靴保持平掌支撑，前方远左靴重新抬起；拒用双脚同时落地的06-v2。',
'07-v3后方近右腿向后伸展，后靴前掌最低、足跟抬起；远左靴屈膝向前通过但不着地。拒用提前前脚落地07-v2。',
'08-v4近右后靴仍低位前掌支撑，远左靴前伸但保留离地间隙；换脚推迟到09。',
'远左前靴全掌开始承重，近右腿后折回收；保留正确帧。',
'远左全掌压重，近右后靴回收；保留正确帧。',
'11-v5远左脚恢复前/中位置全掌承重，近右靴后收；保持低位剑手与剑角。',
'12-v8远左脚平掌支撑，近右屈膝从前景通过且脚抬起；左脚不提前后蹬。',
'13-v3远左全掌在骨盆下支撑，近右靴前摆抬起；身体经过支撑脚。',
'14-v2远左后靴平掌持续支撑，近右前靴保持离地，替换原双脚腾空。',
'15-v3远左后腿向后伸，后靴前掌低位支撑且跟抬，近右前靴抬起。',
'16-v2远左后靴继续低位支撑，近右前靴下落但尚未接地；下一帧01才换近右脚。']
if __name__=='__main__':
 build('E',[1,1,4,6,4,3,3,4,1,1,5,8,3,2,3,2],E_notes)
 print('E selection updated, 16x75ms; dynamic review pending')

