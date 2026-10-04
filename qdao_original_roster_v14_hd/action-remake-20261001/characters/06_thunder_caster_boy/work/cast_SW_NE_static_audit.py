import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
B=Path(__file__).resolve().parents[1]
A=B.parent/'09_bamboo_archer_girl'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=[('cast','E',list(range(16))),('cast','W',list(range(16))),('run','SW',list(range(16))),('run','NE',[0,7,8,9,10,11,12,13,14,15])]
frames=[]
for action,d,indices in spec:
 for i in indices:
  p=B/'runtime'/action/d/f'{i:02d}.png'; rp=p.with_name(p.name+'.generation.json')
  r=json.loads(rp.read_text(encoding='utf-8'));im=Image.open(p);im.load()
  assert im.size==(1024,1024) and im.mode=='RGBA' and im.getchannel('A').getextrema()==(0,255)
  assert sha(p)==r['sha256']
  nrp=B/r['derivedFrom'][0]['generationRecord'];n=json.loads(nrp.read_text(encoding='utf-8'))
  assert n['native']['width']>=1024 and n['native']['height']>=1024
  assert n['actualModel'] is None and n['actualQuality'] is None
  assert n['submittedParameters']['model'] is None and n['submittedParameters']['quality'] is None
  prompt=n['prompt']; prompt_inline=len(prompt)>300 or '\n' in prompt
  assert prompt_inline or (B/prompt).exists()
  note=('两靴鞋尖同向右；膝踝轴连贯，未新增外撇问题。' if d=='E' else '两靴鞋尖同向左；W07–12近靴本轮局修后复核，站距和膝踝保留。') if action=='cast' else ('鞋尖随膝踝向左下，未见NE式反向鞋头；03→04与07/15接触尚需动态判断。' if d=='SW' else '近靴后跟竖缝朝左下，前掌延伸右上；远靴抬起露底，反臂和右杖左符保持。')
  frames.append({'action':action,'direction':d,'index':i,'file':p.relative_to(B).as_posix(),'sha256':sha(p),'source':r['derivedFrom'][0], 'sourcePrompt':n['prompt'],'native':[n['native']['width'],n['native']['height']],'actualModel':None,'actualQuality':None,'staticFootAxisAccepted':True,'staticNote':note,'dynamicAccepted':False})
assert len(frames)==58 and len({r['sha256'] for r in frames})==58
refs=[]
for action,d,indices in [('cast','E',[1,10]),('cast','W',[1,10]),('run','SW',[1,4,9]),('run','NE',[1,4,9])]:
 for i in indices:
  p=A/'runtime'/action/d/f'{i:02d}.png';refs.append({'path':str(p),'sha256':sha(p),'purpose':'实际查看同方向膝踝/鞋尖脚跟关系；未复制人物或按帧号替换06动作'})
report={'reviewer':'cast_frames','reviewedAt':datetime.now(timezone.utc).isoformat(),'scope':'cast E/W32 + SW16 + NE00/07–15共10；共58张静态复核','technicalChecks':'58张1024 RGBA真透明/唯一SHA/来源记录与prompt有效，独立native>=1024；模型质量均未确认','timing':{'runFrameMs':75,'runCycleMs':1200,'runSlowFrameMs':300,'castFrameMs':45,'castCycleMs':720},'references':refs,'frames':frames,'dynamicObservedByThisAgent':False,'continuousVideoEvidenceByThisAgent':False,'clientIntegrated':False,'browserBlocker':'本代理CUA iab不可用/getState browsers[]；根代理另行真实播放，本报告不将联系表当动态证据。','remainingDynamicChecks':['NE10→11接地高度与蹬地转换，15→00闭环','SW03→04跨腿转换、07/15落地衔接、15→00闭环','cast W06→07和12→13局部修改后脚轴连续性；施法45ms保持'],'knownStaticAxisFailures':[]}
(B/'review/cast_SW_NE_static_audit_20261004.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 06施法／西南跑步／东北负责帧静态复核','',report['scope']+'。全部绑定下列当前成品 SHA；静态鞋轴通过不代表动态整体验收。','',report['technicalChecks']+'。跑步每帧75ms、一圈1200ms，施法每帧45ms、720ms。','', '实际看09同向参考：cast E/W01、10；run SW及NE01、04、09。06与09帧号不同，不按帧号照搬。','', '本轮实际修复：NE00v5、07v2、08v4、09v3、10v6、11v5、12v2；root提供NE13–15 rootaxis_v1已复核。cast W07v3、08v2、09v2、10v4与root的11/12 rootaxis_v1已复核；前轮E03/W04–06局部修复保留。','', 'SW16本轮保留，逐格看鞋尖随膝踝朝左下；没有NE的脚跟/鞋头倒置。保留动态观察点，不因静态正确而宣称跑步合格。','', '剩余动态观察：']+['- '+x for x in report['remainingDynamicChecks']]+['',report['browserBlocker']+' 当前无本地客户端接入。','', '所有native暂保留，供根代理最终来源扫描与统一清理；失败稿记录拒收原因。','', '| 当前帧 | 原生来源 | 成品SHA256 |','|---|---|---|']
for f in frames: lines.append('| '+f['file']+' | '+f['source']['file']+' | '+f['sha256']+' |')
(B/'review/cast_SW_NE_static_audit_20261004.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
for d in ['E','W']:
 p=B/'review'/f'cast_{d}_contact_20261003.jpg'
 p.with_name(p.name+'.generation.json').write_text(json.dumps({'file':p.relative_to(B).as_posix(),'sha256':sha(p),'operation':'static full-canvas 4x4 contact preview, not runtime sprites','derivedFrom':[f for f in frames if f['action']=='cast' and f['direction']==d],'actualModel':None,'actualQuality':None},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'reviewedFrames':len(frames),'staticAxisFailures':0,'dynamicAccepted':False,'report':'review/cast_SW_NE_static_audit_20261004.json'},ensure_ascii=False))
