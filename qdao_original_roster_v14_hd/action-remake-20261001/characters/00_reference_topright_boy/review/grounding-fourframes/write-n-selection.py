from PIL import Image
from pathlib import Path
import json,hashlib,datetime
r=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy")
names=['01-v4','16-v2','02-v2','03-v3','05-v4','06-v9','07-v3','08-v4','08-v2','09-v1','10-v2','05-v3','13-v4','03-v1','16-v3','15-v4']
obs=[
'右鞋后跟先接触，右小腿前伸，左腿后折；空右臂在后方。',
'右前侧接触加载，右鞋从跟部滚向平掌；左腿仍后折，空右臂后摆。',
'右膝缓冲回收到髋下，右鞋平掌，左小腿后折恢复。',
'右中段支撑膝略伸，右踝前移；左鞋后折幅度减小。',
'右髋下平掌承重，左膝向前经过，左鞋由整底转后跟视图；空右臂前摆遮挡。',
'右髋下持续承重，膝较伸，左膝更向远方抬起，左鞋升高且后跟朝观者；空右臂前藏。',
'右腿后伸，鞋跟抬起，支撑前掌仍朝地，左腿前摆；空右臂前藏。',
'右后侧伸展稍增，后跟更高，前掌端接触；左膝前抬，右空臂已单独修为前藏。',
'左前侧鞋后跟/平掌接触，左腿纵深前伸；右腿后折鞋底可见，空右臂前摆。',
'左前侧向加载过渡，左膝屈曲、接触鞋向身下回收；右腿后折。',
'左中段缓冲承重，鞋掌平稳，右膝开始恢复。',
'左髋下平掌支撑，右鞋后折回收程度减小；该原生候选原请求为右脚，按实际左支撑重排，不按提示词硬认。',
'左髋下支撑膝略伸，右膝进入经过，鞋仍可见背底；空右臂向身侧过渡。',
'左中段末段，左膝较伸、鞋跟轻减压，右膝已向前且鞋呈后跟视图；右空臂后摆。',
'左腿向后伸、前掌接触、鞋跟抬起；右膝前摆，空右臂后摆。',
'左后侧推蹬幅度增大，前掌端保持接触，右膝向前准备接地；空右臂后摆。'
]
frames=[]
for i,(n,o) in enumerate(zip(names,obs),1):
 p=r/'generation/run/N'/(n+'.png')
 with Image.open(p) as im: assert im.size==(1254,1254) and im.mode=='RGBA'
 record=p.with_suffix('.png.generation.json');assert record.exists()
 frames.append({'slot':f'run/N/{i:02}','frame':i,'durationMs':75,'source':p.relative_to(r).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'supportFoot':'right' if i<=8 else 'left','supportPositionAlongRun':['front','front','middle','middle','middle','middle','rear','rear'][(i-1)%8],'staticContact':'visible_contact','confidence':'medium' if i in [1,2,7,8,9,10,15,16] else 'medium-high','observation':o,'generationRecord':record.relative_to(r).as_posix()})
assert len({x['source'] for x in frames})==16
assert len({x['sha256'] for x in frames})==16
data={'schemaVersion':1,'direction':'N','status':'static_candidate_complete_dynamic_unverified','createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rule':'per foot front2 + spatial under-hip middle4 + rear2; sides mean fore/aft along run axis','frameDurationMs':75,'cycleDurationMs':1200,'nativeCanvas':[1254,1254],'rgba':True,'uniqueSources':16,'globalSelectionChanged':False,'formalExportsChanged':False,'dynamicVisualVerified':False,'staticMethod':'actual native images and derived full-canvas/lower-body contact sheets; heel/sole orientation, knee-ankle continuity and overlap; not alpha extrema alone','frames':frames,'limitations':['正北纯背视前后深度主要依靠膝踝遮挡、鞋跟/鞋底透视读取；透明背景无法直接测定世界地平面。','静态接触判断不代表浏览器或客户端播放验收。'],'reorderedGeneratedCandidates':['16-v2 to slot02','08-v2 to slot09','05-v3 actual left support to slot12','16-v3 to slot15','15-v4 to slot16'],'rejectedCandidates':{'05-v3':'不作原请求右05；按实图左支撑用于12','06-v8':'原请求右06但实图左支撑，不采用','14-v3':'恢复腿仍后折，不如03-v1适合中段末','08-v3':'空右臂反相，采用只改右臂的08-v4'}}
target=r/'generation/run/N/selection-middle4-side2-20261004.json';target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(r/'review/grounding-fourframes/N-static-evidence-middle4-side2.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='# N 空间前2／中4／后2静态候选\n\n16张唯一原生源，每帧75ms、整圈1200ms；未改全局选表与导出，动态未验收。\n\n|槽位|源|支撑/位置|静态观察|SHA256|\n|---|---|---|---|---|\n'
for f in frames:md+=f"|{f['frame']:02}|{f['source']}|{f['supportFoot']} / {f['supportPositionAlongRun']}|{f['observation']}|{f['sha256']}|\n"
md+='\n正北纵深位置依据膝踝遮挡和鞋跟/鞋底透视综合判断，不以alpha最低点宣称地面。原请求与实图不同的05-v3只按实际左支撑用于12，且每源仅用一次。\n'
(r/'review/grounding-fourframes/N-static-evidence-middle4-side2.md').write_text(md,encoding='utf-8')
print(json.dumps({'selection':str(target),'frames':len(frames),'uniqueSha':len({f['sha256'] for f in frames}),'cycleMs':1200}))

