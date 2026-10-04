from pathlib import Path
import json,re,hashlib
root=Path(__file__).resolve().parents[2]
planpath=root/'review/grounding-fourframes/south-plan-middle4-side2-20261004.json'
plan=json.loads(planpath.read_text(encoding='utf-8'))
config=json.loads((root/'generation/run/S/04-v2.request.json').read_text(encoding='utf-8'))['configSnapshot']
# Visual audit: former SE12 has the left support leg behind the hip; use once in rear slot15.
for e in plan['frames']:
 if e['direction']=='SE' and e['frame']==12:e.update(source=None,sha256=None,status='native_edit_required')
 if e['direction']=='SE' and e['frame']==15:
  p=root/'generation/run/SE/12-v4.png';e.update(source=p.relative_to(root).as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),status='provisional_existing_source_to_review')
planpath.write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding='utf-8')
mothers={'S':{'right':'04-v2','left':'12-v3'},'SE':{'right':'03-v1','left':'11-v3'},'SW':{'right':'03-v4','left':'11-v2'}}
style='D:/work/image/designs/jubaozhai-ui/02-characters.png'
jobs=[]
for e in plan['frames']:
 if e['source']:continue
 d=e['direction'];f=e['frame'];side=e['supportFoot'];n=e['distinctPoseWithinPosition']
 folder=root/'generation/run'/d
 existing=[int(re.search(r'-v(\d+)',x.stem).group(1)) for x in folder.glob(f'{f:02d}-v*.png')]
 stem=f'{f:02d}-v{max(existing,default=0)+1}'
 mother=folder/(mothers[d][side]+'.png')
 direction={'S':'正面朝屏幕下方','SE':'三分之四正面朝屏幕右下','SW':'三分之四正面朝屏幕左下'}[d]
 sidecn={'right':'解剖右脚（画面左腿）','left':'解剖左脚（画面右腿）'}[side]
 other={'right':'左','left':'右'}[side]
 if e['positionAlongRunDirection']=='under_body_support':
  poses={2:'中段第2姿态：支撑膝比参考更自然弯曲缓冲，踝背屈，全掌压地；摆动腿由后侧屈膝向前收。',3:'中段第3姿态：髋经过支撑踝正上方，支撑膝轻微伸展但不锁死，全掌仍落地；摆动腿的膝向前通过，脚自然悬空。',4:'中段第4姿态：支撑脚仍在髋下中段，只略后移，支撑膝继续伸展、脚跟轻微提起但脚掌稳定接触；摆动腿向前抬膝，准备下一步。'}
  phase=poses[n]
 else:
  phase=('后侧推蹬第1姿态：支撑腿从髋向跑向的后方伸展，鞋移到身体后侧地面；脚跟略升、前脚掌压地，绝不悬空。对侧腿朝跑向前方抬膝。' if n==1 else '后侧推蹬第2姿态：支撑腿比前一后撑姿态稍伸展，脚位仍在身体后侧地面，鞋跟抬高、前掌与趾端持续接触；另一腿向前落地前伸，不许两脚腾空。')
 prompt=f'在第一张母版上局部编辑双腿，制作单张独立跑步帧 {d}{f:02d}。人物{direction}。固定1254×1254透明RGBA完整画布，头脸、头身大小、躯干、手臂和葫芦位置保持母版，不放大、不缩放、不移动整个人。左手握葫芦，右手空，发带结在解剖左。{sidecn}为唯一支撑脚，{phase}这是沿跑向的前后空间，不是向左右外八。鞋长轴和膝踝一致朝跑向，保持天然透视，不拧踝、不叉腿。每张为不同真实屈膝踝姿态，不照抄原姿势。只画一个角色，无地面、阴影、文字。第二张已确认风格，仅用于金翠白材质和精细Q版画法。'
 refs=[mother.as_posix(),style]
 rel=f'generation/run/{d}/{stem}'
 req={'startedAt':None,'status':'prepared_not_submitted','tool':'image_gen.imagegen','route':'builtin','configSnapshot':config,'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'referenced_image_paths':refs},'actualModel':None,'actualQuality':None,'prompt':rel+'.prompt.txt','references':refs,'referenceRoles':['fixed-canvas same-support mother','approved style'],'referenceSha256':[hashlib.sha256(Path(x).read_bytes()).hexdigest() for x in refs],'objective':'middle4-side2 spatial layout 16*75ms: front2 middle4 rear2 per foot','slot':e}
 (root/(rel+'.prompt.txt')).write_text(prompt+'\n',encoding='utf-8')
 (root/(rel+'.request.json')).write_text(json.dumps(req,ensure_ascii=False,indent=2),encoding='utf-8')
 jobs.append({'direction':d,'frame':f,'stem':stem,'rel':rel,'prompt':prompt,'refs':refs})
out=root/'review/grounding-fourframes/south-middle4-jobs.json'
out.write_text(json.dumps(jobs,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(jobs,ensure_ascii=False))

