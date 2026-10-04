from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
from PIL import Image,ImageDraw
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy')
A=B/'audit/archer-reference'
sys.path.insert(0,str(B/'tools'))
from build_delivery import inspect
prev=json.loads((A/'ne-w-grounding-selection.json').read_text(encoding='utf-8'))
frames=[]
reasons={
6:'同一后支撑足保持、靴尖朝W。与已选W07脚底高差由33px降至8px；未达到提示词y1191，仍偏高23px。静态建议替换后动态复核。',
16:'同一前支撑足保持、靴底放平下移，脚底由1166至1183，接近目标1191，手臂扇及脸比例保留。静态建议替换。'
}
for n in [6,16]:
 key=f'run-W-{n:02d}-final-local-v1'
 f=B/'sources/new'/f'{key}.png'
 im,info=inspect(f)
 rec=json.loads((B/'provenance/generation'/f'{key}.json').read_text(encoding='utf-8'))
 old=next(x for x in prev['frames'] if x['slot']==f'run-W-{n:02d}')
 frames.append({'slot':f'run-W-{n:02d}','action':'run','direction':'W','frame':n,'durationMs':75,'decision':'replace','candidateKey':key,'source':f.relative_to(B).as_posix(),'sha256':rec['sha256'],'generationRecord':f'provenance/generation/{key}.json','supportFoot':'left','positionSegment':3 if n==6 else 0,'staticReview':'reviewed','animationApproval':'pending_root_dynamic_review','reason':reasons[n],'supersedes':{'source':old['source'],'sha256':old['sha256'],'generationRecord':old['generationRecord']},'technical':info,'alpha128BBox':list(im.getchannel('A').point(lambda a:255 if a>=128 else 0).getbbox())})
data={'schemaVersion':1,'character':'15_water_dragon_scholar_boy','generatedAt':datetime.now(timezone.utc).isoformat(),'status':'two_local_edits_static_review_complete_pending_root_dynamic','generationLimit':'Parent requested one round and exactly two local edits; no additional generation performed.','frames':frames,'technicalErrors':[],'actualModel':None,'actualQuality':None,'targetModel':'gpt-image-2.5-sunburst','targetQuality':'max','modelEvidence':'内置工具无型号/质量选择器，实际返回未披露，目标不可作为实测。','warnings':['W06新图脚底1168并未命中1191，W05 1197→W06 1168仍有29px差。W06→W07减至8px。必须完整16帧动态复核，不等同于全循环通过。','仅私有候选与审查；runtime/master由父线程导出。']}
(A/'ne-w-final-local-selection.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'ne-w-final-local-review.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(A/'ne-w-final-local-review.md').write_text('# NE/W 最后两张局部修正\n\n只修改 W06 与 W16 小腿/靴子，已实际查看原图及新图，并附15身份、确认风格参考。两张均1254×1254透明RGBA，边缘留白通过。足别、双手及扇子保持。\n\n- W06：原脚底1209，新1168，W07为1176；06→07高差33降至8。仍未命中目标1191，05→06差29。建议替换后完整动态复核。\n- W16：原脚底1166，新1183；前支撑靴底更平，降低悬空感。建议替换。\n\n坐标只作审计，不用于自动裁切/脚底吸附。两张逐图来源、提示词、引用SHA和原生回执已落盘；模型目标GPT Image 2.5 Sunburst/max，实际未确认。runtime与master未修改。\n',encoding='utf-8')
# Whole-canvas comparison only; no anatomy edits, no alpha crop, no per-frame scaling.
sheet=Image.new('RGB',(1024,580),'#e9edf0')
dr=ImageDraw.Draw(sheet)
for i,n in enumerate([6,16]):
 old=next(x for x in prev['frames'] if x['slot']==f'run-W-{n:02d}')
 oldPath=B/old['source']
 if not oldPath.exists():
  oldRecord=json.loads((B/old['generationRecord']).read_text(encoding='utf-8'))
  oldPath=Path(oldRecord['evidence']['hostOutput'])
 for j,path in enumerate([oldPath,B/'sources/new'/f'run-W-{n:02d}-final-local-v1.png']):
  im=Image.open(path).convert('RGBA')
  im=im.resize((512,512),Image.Resampling.LANCZOS)
  x=j*512;y=34
  if i==0:
   # one output per frame, easy to inspect
   pass
  pane=Image.new('RGB',(512,554),'#e9edf0')
  pane.paste(im,(0,34),im)
  d=ImageDraw.Draw(pane);d.text((8,8),f'W{n:02d} '+('BEFORE' if j==0 else 'AFTER'),fill='#17263b')
  # Reference root at native y1191, resized whole canvas.
  line=int(1191*512/1254)+34
  d.line((0,line,511,line),fill='#799e7c',width=1)
  sheet.paste(pane,(j*512,0))
 sheet.crop((0,0,1024,554)).save(A/f'ne-w-final-local-W{n:02d}-comparison.png')
print(str(A/'ne-w-final-local-selection.json'))
print('technicalErrors=0, replacement_count=2')

