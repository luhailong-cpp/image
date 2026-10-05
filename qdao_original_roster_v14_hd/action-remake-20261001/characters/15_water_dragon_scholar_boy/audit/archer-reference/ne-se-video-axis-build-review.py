from pathlib import Path
from datetime import datetime,timezone
import json,sys,hashlib
from PIL import Image,ImageDraw
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy'); A=B/'audit/archer-reference'
sys.path.insert(0,str(B/'tools'))
from build_delivery import inspect
slots=['run-NE-08','run-NE-09','run-NE-12','run-NE-13','run-NE-15','run-SE-04','run-SE-05']
notes={
'run-NE-08':'右支撑靴前掌横向长度收短，鞋跟至鞋尖改回朝右上远离镜头的背3/4透视；另一足露底及手扇保留。',
'run-NE-09':'右支撑靴鞋尖向右上收进，跟部正后方轮廓更清楚；保留当前缓冲腿和对侧抬足。',
'run-NE-12':'支撑靴由明显E向长侧面改短的背3/4形，靴筒接续小腿更直；保留同足支撑和另一足姿态。',
'run-NE-13':'支撑前掌外伸减少，背3/4脚轴沿行进方向；未借用对照图动作或换腿。',
'run-NE-15':'后蹬支撑足靴筒外扭减轻，后跟到前掌轴收回右上，仍保留提跟及前掌支撑。',
'run-SE-04':'下方左支撑靴的横向长鞋面收短，鞋头转向右下斜前，靴筒自然接踝；原抬起右足不变。',
'run-SE-05':'左支撑靴改正面3/4短透视，鞋尖朝右下，去掉横向外撇；保留同足后移承重阶段。'
}
frames=[]
canvas=Image.new('RGB',(768,len(slots)*412),'#e7ecef')
draw=ImageDraw.Draw(canvas)
for row,slot in enumerate(slots):
 key=slot+'-video-axis-v1'
 q=json.loads((B/'provenance/requests'/f'{key}.json').read_text(encoding='utf-8'))
 rec=json.loads((B/'provenance/generation'/f'{key}.json').read_text(encoding='utf-8'))
 f=B/rec['file'];im,info=inspect(f);old=Image.open(q['sourceBeforeEdit']['path']).convert('RGBA')
 oldbbox=old.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
 newbbox=im.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox()
 frames.append({'slot':slot,'action':'run','direction':slot.split('-')[1],'frame':int(slot.split('-')[2]),'durationMs':75,'decision':'replace','candidateKey':key,'source':rec['file'],'sha256':rec['sha256'],'generationRecord':f'provenance/generation/{key}.json','supportFoot':'right' if '-NE-' in slot else 'left','staticReview':'reviewed_local_axis_improved','animationApproval':'pending_root_dynamic_review','notes':[notes[slot]],'supersedes':{'source':q['sourceBeforeEdit']['selectedSource'],'sha256':q['sourceBeforeEdit']['sha256'],'generationRecord':q['sourceBeforeEdit']['generationRecord']},'technical':info,'alpha128BottomBefore':oldbbox[3],'alpha128BottomAfter':newbbox[3],'alpha128BottomDelta':newbbox[3]-oldbbox[3],'heightMeasurementPurpose':'审计差异，不用于按帧吸附或调整导出。'})
 for col,pic in enumerate([old,im]):
  thumb=pic.resize((384,384),Image.Resampling.LANCZOS)
  x=col*384;y=row*412
  draw.text((x+8,y+6),slot+(' BEFORE' if col==0 else ' AFTER'),fill='#192d3a')
  canvas.paste(thumb,(x,y+28),thumb)
  yy=y+28+int(1191*384/1254)
  draw.line((x,yy,x+383,yy),fill='#b8c2c8',width=1)
canvas.save(A/'ne-se-video-axis-comparison.png')
data={'schemaVersion':1,'character':'15_water_dragon_scholar_boy','generatedAt':datetime.now(timezone.utc).isoformat(),'scope':'NE08/09/12/13/15 and SE04/05 supporting lower-leg/boot yaw correction','status':'seven_candidates_static_reviewed_pending_parent_sequence_review','frames':frames,'technicalErrors':[],'rejectedCandidates':[],'referenceAudit':'实际查看共享character-detail/video-contact、用户截图及64帧正式contact和20张1024单图；生成另实际查看与传入原生目标、1张同向正确对照、身份、确认风格、character-detail共5张。NE11/SE03原生对照从generation.evidence.hostOutput读取并核SHA，没有runtime放大。','comparison':'audit/archer-reference/ne-se-video-axis-comparison.png','warnings':['SE04/05最低脚底相较原图下移13/15原生像素，约10/11正式像素；需整圈核对接地高差，不声明逐像素不变。','NE五帧最低脚底变化为+4/+3/-8/+7/+3原生像素。','当前只审局部鞋轴和姿态保留，未替代正常与慢速动态完整验收。'],'actualModel':None,'actualQuality':None,'targetModel':'gpt-image-2.5-sunburst','targetQuality':'max','modelEvidence':'工具无型号/质量选择器，实际回执未披露。','formalFilesChanged':False}
(A/'ne-se-video-axis-selection.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'ne-se-video-axis-review.md').write_text('# NE/SE 视频脚轴局部修正\n\n7张原生1254透明稿已实际查看，均两腿两靴、支撑足别与手扇保持、边缘留白通过；建议父线程按selection替换后整圈复核。\n\n'+'\n'.join('- '+f['slot']+' = '+f['candidateKey']+'：'+f['notes'][0]+f" 脚底审计{f['alpha128BottomBefore']}→{f['alpha128BottomAfter']}。" for f in frames)+'\n\nSE04/05接地高度有13/15原生像素下移，约10/11正式像素；未按像素吸附或修改导出。NE五帧差异不超过8原生像素。无失败重试。实际model/quality均null，配置目标2.5 Sunburst/max。未修改manifest、derived、sources-index、runtime和正式preview。\n',encoding='utf-8')
print(json.dumps({'selection':str(A/'ne-se-video-axis-selection.json'),'accepted':len(frames),'technicalErrors':[]},ensure_ascii=False))

