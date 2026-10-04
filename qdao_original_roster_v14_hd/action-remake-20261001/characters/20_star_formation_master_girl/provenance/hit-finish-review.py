from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from PIL import Image
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
stamp=datetime.now(ZoneInfo('America/New_York')).isoformat()
versions={'E':['01-v2','02-v2','03-v3','04-v2','05-v3','06-v2'],'W':['01-v2','02-v3','03-v6','03-v4','05-v2','06-v2']}
notes={'E':['预备帧重绘对齐02双靴，近右盘远左三卡。','初受力：膝部压缩、神情变化，靴位可读。','峰值屈膝与左向后仰明确；03-v3已消除远侧多出的眼。','重新接03峰值，保持双靴地面位置，头身开始回弹。','继04恢复，右手盘不翻转，三卡可数。','独立绘制的恢复呼吸/末帧，靴位按01固定。'],'W':['预备重绘对齐02双靴，近左三卡远右盘。','初受力固定双脚，左向单眼。','03-v6修掉前跨与脚漂，头肩向右后缩/膝髋下降，发梢不触边。','采用实际更适合回弹相位的03-v4，单独占用04槽。','继04恢复，三卡与右手盘保持归属。','独立绘制恢复末帧，靴位按01固定。']}
records=[]
for d,names in versions.items():
 sp=ROOT/('hit-selection.json' if d=='E' else 'hit-W-selection.json');s=json.loads(sp.read_text(encoding='utf-8-sig'));frames=[]
 for i,name in enumerate(names,1):
  src=f'generation/hit/{d}/{name}.png';p=ROOT/src;rp=Path(str(p)+'.generation.json');r=json.loads(rp.read_text(encoding='utf-8-sig'));im=Image.open(p);im.load();digest=hashlib.sha256(p.read_bytes()).hexdigest();assert r['sha256']==digest and im.mode=='RGBA' and min(im.size)>=1024
  a=im.getchannel('A');assert a.getextrema()==(0,255)
  bounds=a.point(lambda x:255 if x>=128 else 0).getbbox()
  crops=[(0,1160,680,1230),(680,1160,1254,1230)] if d=='E' else [(0,1160,610,1230),(610,1160,1254,1230)]
  foot=[]
  for x0,y0,x1,y1 in crops:
   c=a.crop((x0,y0,x1,y1)).point(lambda x:255 if x>=200 else 0);bb=c.getbbox();foot.append([bb[0]+x0,bb[1]+y0,bb[2]+x0,bb[3]+y0] if bb else None)
  r['review']={'status':'candidate','staticFindings':notes[d][i-1],'sequenceReview':'static_phase_sequence_checked_candidate','dynamicAcceptance':False,'fullSpeedReview':'not_verified_in_browser_or_client'}
  rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
  f={'action':'hit','direction':d,'frame':i,'source':src,'generationRecord':src+'.generation.json','sourceSha256':digest,'status':'candidate','visualReview':'static_checked_candidate','dynamicReview':'not_verified','sequenceNote':notes[d][i-1]};frames.append(f)
  records.append({**f,'technical':{'nativeSize':list(im.size),'mode':im.mode,'alphaExtrema':[0,255],'alpha128BoundsForDiagnosisOnly':list(bounds),'bootSoleRegionBoundsForDiagnosisOnly':foot,'hashMatchesRecord':True,'actualModel':r.get('actualModel'),'actualQuality':r.get('actualQuality')},'staticAnatomy':notes[d][i-1]})
 s.update({'frames':frames,'expectedFrames':6,'availableFrames':6,'status':'repaired_candidates_pending_dynamic_review','dynamicAcceptance':False,'dynamicReview':'not_verified_after_repair','updatedAt':stamp,'strictReview':'provenance/hit-finish-review.json'});sp.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
review={'schema':1,'character':'20_star_formation_master_girl','reviewedAt':stamp,'scope':'hit E6/W6 repaired candidates','status':'static_candidates_complete_dynamic_pending','expectedFrames':12,'staticReviewedCandidates':12,'completeActionAccepted':False,'dynamicAcceptance':False,'clientIntegrated':False,'timing':{'frameMs':40,'segmentMs':240},'method':'实际查看原生PNG及整画布统一缩放接触表；模型逐帧重画，未镜像、复制、插值或按最低脚/BBox对齐。脚底区域alpha读数只诊断，不修改图。','frames':records,'pending':['40ms正常速度、160ms慢速与逐帧连播仍需动态验收；不能以帧数/哈希不同当完成。','E03到04回弹头部上升约几十原生像素，需要正常速度检查力度与反弹节奏。','首尾到外部idle的过渡未在客户端执行；本角色当前固定双脚约束仅用于本段素材。','个别星穗/衣纹存在生成型细节波动，需要连续播放时复查。'],'modelEvidence':'配置目标GPT Image2.5 Sunburst/max；内置提交model/quality null、实际返回值未确认，逐图保留。'}
(ROOT/'provenance/hit-finish-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'candidates':12,'staticOnly':True,'footBounds':[{k:x[k] for k in ['direction','frame']}|{'bounds':x['technical']['bootSoleRegionBoundsForDiagnosisOnly']} for x in records]}))
