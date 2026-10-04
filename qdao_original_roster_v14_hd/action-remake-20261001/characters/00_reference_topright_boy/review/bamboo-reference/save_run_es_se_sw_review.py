from pathlib import Path
import json,hashlib,datetime
root=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/00_reference_topright_boy')
reference=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl')
out=root/'review/bamboo-reference';out.mkdir(parents=True,exist_ok=True)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
boy_manifest=read(root/'manifest.json');bamboo_manifest=read(reference/'manifest.json')
selected=read(root/'selected-new.json')
dirs=['E','S','SE','SW']
reasons={
'E':{'feet':'鞋尖沿画面右方，支撑鞋与小腿方向一致；后腿屈膝的足尖下垂不是横向外撇。未发现新增反向脚掌或扭踝。','hand':'右空手可见后摆与前摆两个阶段，左手葫芦保持；无借用竹弓持弓姿态。','grounding':'01–03及09–11可读到接触/承重到换腿阶段；静态未见新增必须补画的支撑侧错误，真实地面/滑步需播放与客户端验证。'},
'S':{'feet':'正前鞋面/鞋底有抬脚透视，未见高置信度横向外八；膝踝相接，不能把鞋底斜椭圆等同于外撇。','hand':'前后半圈右空臂有相反摆动，左手保持葫芦；不把竹弓较窄腿型直接套给道童。','grounding':'01–03与09–11可读到两侧轮换支撑，保留原有相位。接触停留与压低幅度未做实时动态验收。'},
'SE':{'feet':'当前01-v5、02-v3、11-v3、12-v4、13-v3、14-v2、15-v3、16-v2的前鞋已转向右下；其余鞋形未见新增反向或扭踝硬伤。','hand':'右空手反摆和左持葫芦身份保持；没有因鞋向修复替换上身姿态。','grounding':'接触、换腿、腾空轮廓仍沿自身原相位；未按竹弓同帧编号或根点搬移脚掌，真实承重时长和地面接触仍需播放复核。'},
'SW':{'feet':'近脚鞋尖向左下，抬脚/屈膝中的鞋底透视成立；08–12放大核查已有记录，未出现与身向相反的外撇，16-v3保留。','hand':'右空手能辨认前摆与后摆阶段，左手葫芦保持；竹弓的弓与持弓手不迁移。','grounding':'01–03及08–11可读到交替接触/承重段；不因与竹弓膝高或脚距不同而判错，不从静态截图推定滑步通过。'}}
boy_rows=[];ref_rows=[];contacts=[]
for d in dirs:
 for f in [x for x in boy_manifest['frames'] if x['file'].startswith('frames/run/'+d+'/')]:
  p=root/f['file'];actual=sha(p);assert actual==f['sha256'],f['file']
  n=int(p.stem)
  s=next(x for x in selected if x['action']=='run' and x['direction']==d and x['frame']==n)
  source=root/s['source']
  boy_rows.append({'direction':d,'frame':n,'file':f['file'],'sha256':actual,'nativeSource':s['source'],'nativeSourceSha256':sha(source),'frameDurationMsAtRead':f.get('frameDurationMs'),'verdict':'retain_no_new_clear_static_limb_failure','dynamicApproved':False})
 seq=next(s for s in bamboo_manifest['sequences'] if s['action']=='run' and s['direction']==d)
 for f in seq['frames']:
  p=reference/f['file'];actual=sha(p);assert actual==f['sha256'],f['file']
  ref_rows.append({'direction':d,'frame':f['frame'],'file':f['file'],'sha256':actual})
 for actor,base,path in [('00',root,'review/animations/run-'+d+'-contact.png'),('09',reference,'preview/qa/run-'+d+'-contact.png')]:
  contacts.append({'character':actor,'direction':d,'file':str(base/path),'sha256':sha(base/path),'actuallyViewed':True})
assert len(boy_rows)==64 and len(ref_rows)==64
report={'createdUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'finish_nw','scope':'Independent static comparison of current 00 E/S/SE/SW 64 run frames through actual complete contact sheets against user-designated 09 bamboo reference. No generation or formal asset/selection/timing mutation.','referenceAuthority':'用户最新明确以竹弓少女为已确认正确动作参照；不再用月影旧说法。帧号、支撑侧、人物比例、弓和根点不照搬。','referenceManifestSha256':sha(reference/'manifest.json'),'referenceTiming':read(reference/'animation-timing.json'),'boyManifestSha256AtRead':sha(root/'manifest.json'),'selectedNewSha256AtRead':sha(root/'selected-new.json'),'timingConclusion':{'historicalReviewContext':'审阅开始时双方离线跑步720ms，原道童E有承重权重；这一节奏结论已被用户最新要求覆写。','latestUserTarget':{'frameMs':75,'count':16,'cycleMs':1200,'allEightDirectionsUniform':True,'removeEWeights':True,'removeOldFastPresets':[480,640,720,800]},'owner':'root updates timing source, manifest, previews; this reviewer does not edit timing files.','dynamicTested':False,'clientConfirmed':False},'directionFindings':reasons,'mustRegenerate':[],'recommendation':'保留此次绑定的64帧；静态未发现新的高置信度脚掌朝向、膝踝、持手或反摆硬伤。速度由root统一1200ms，不通过重画已可用帧处理速度反馈。','limitations':'实际查看双方8张完整联系表及本轮此前鞋向原图核查；没有实时播放、客户端位移/滑步验收。不同静态头位或脚下缘不单独作为必须重画依据。','contacts':contacts,'boyFrames':sorted(boy_rows,key=lambda r:(dirs.index(r['direction']),r['frame'])),'referenceFrames':ref_rows}
(out/'run-es-se-sw-static-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# 竹弓参照：道童 E / S / SE / SW 静态复核','',
'已实际查看双方八张完整联系表，并核对竹弓当前 manifest/runtime。双方各64张当前PNG的实际SHA、道童64张原生源SHA和联系表SHA均绑定在 run-es-se-sw-static-review.json。','',
'结论：保留道童当前64帧，本次无新增必须重画帧。','']
for d in dirs:
 lines+=[f'- **{d}**：'+reasons[d]['feet']+' '+reasons[d]['hand']+' '+reasons[d]['grounding']]
lines+=['','速度要求已更新：**八方向统一75ms×16=1200ms**，取消E权重并移除正式预览480/640/720/800旧快档，由root更新。审阅开始时的720ms仅是历史上下文，不是当前建议。','',
'竹弓按用户最新指定用于动作参考；不跨方向套帧号、不照搬根点、弓或人物比例。道童保持左持葫芦、右手空。','',
'本结论限于静态实见，未宣称正常速度、接地停留、客户端位移或循环滑步动态通过。本代理未生图，未改选表、正式图或时长文件。']
(out/'RUN_ES_SE_SW_STATIC_REVIEW.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
print('Saved: run-es-se-sw-static-review.json and RUN_ES_SE_SW_STATIC_REVIEW.md; 64 boy + 64 bamboo hashes verified; no new must-redraw frames.')

