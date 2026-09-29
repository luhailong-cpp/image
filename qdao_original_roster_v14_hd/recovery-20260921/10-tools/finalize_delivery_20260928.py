"""Freeze reviewed character-10 outputs; does not manufacture or alter image pixels."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, importlib.util

R=Path(__file__).resolve().parents[1]
O=R/'10-delivery-preview/current'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=read(O/'manifest.json'); validation=read(O/'validation.json')
assert m['walkCount']==128 and m['idleCount']==8 and not m['missing']
assert validation['manifestSHA256']==sha(O/'manifest.json')
assert all(validation[k] for k in ['png1024Transparent','nativeAtLeast1024','eightLoops16Frames30ms480ms','loopPixelsExactlySource','sourceRequestReceiptPromptHashBound'])
now=datetime.now(timezone.utc).isoformat()
prior=sha(O/'manifest.json')
files=[]
for slot,row in m['frames'].items():
    assert sha(O/row['file'])==row['sha256']
    row['finalVisualReview']='accepted'
    side=Path(str(O/row['file'])+'.generation.json');meta=read(side)
    meta['finalVisualReview']='accepted'
    meta['finalReviewRecord']='visual-acceptance.json'
    meta['sourceRetentionRecord']='source-retention.json'
    write(side,meta)
    files.append({k:row[k] for k in ['slot','file','sha256','rawSHA256','archive']})

observations={
 'N':'16帧两腿交替；N16-v5缓解尾首头肩变化，15→16→01→02保持步态顺序。',
 'NE':'修正靴子和接缝发束；06→09及15→02保持近远腿支撑关系，发束摆动属于次级运动。',
 'E':'修正04/05主体横移；完整枪尖与交替迈步可辨，尾首没有换腿倒序。',
 'SE':'07-v2保留两腿；10/11-v2修正连续只落脚跟；15-v2/16-v1低抬腿接回01。',
 'S':'正面左右脚交替；S16-v2改善头肩接缝；独立站立双脚着地。',
 'SW':'05→06及13→14步幅相位变化较快，但支撑腿不反转；全帧与播放采样未发现额外肢体或错误换腿。',
 'W':'06-v7/14-v5降低头髻与肩角突变；06近侧后支撑腿遮挡远侧前摆腿符合深度；07/08按真实独立稿脚部下降顺序重排。',
 'NW':'01-v4/16-v2改善接缝；04→05、13→14主要变化为马尾衣摆；远近脚透视深度保留。'
}
evidence=[
 '10-work/agent-E-SW/final-export-review-20260928.json',
 '10-work/agent-N-NE/final-NE-SE-QA/review-20260928.json',
 '10-work/agent-N-NE/final-NE-SE-QA/examined-outputs.json',
 '10-work/agent-N-NE/idle-QA/review-20260928.json',
 '10-work/agent-N-NE/idle-QA/examined-images.json',
 '10-work/agent-W-NW/QA-20260928.md',
 '10-work/agent-W-NW/selection-updates-20260928.json'
]
report={
 'character':m['character'],'status':'accepted','acceptedAt':now,'walkCount':128,'idleCount':8,
 'scope':'素材制作与本地离线验收；不含客户端导入或运行验收',
 'reviewedPixelManifestSHA256':prior,
 'reviewers':['root','complete_e_sw','complete_ne','finish_ns_wnw'],
 'checks':{
   'allFramesStatic':'128张行走与8张站立已看深浅底接触表、正常尺寸和放大细节。',
   'gait':'检查交替迈腿、支撑脚、足部深度、头身比例、完整装备与15→16→01→02。',
   'root':'整画布等比缩小后注册虚拟骨盆/地面点(512,942)；不以枪穗或腾空脚作根点，不逐脚拉齐透视。',
   'alpha':'深浅底复核无明显背景残块、彩边、悬浮碎片或截断轮廓；保留发丝细端抗锯齿。',
   'playback':'root在本地浏览器实际运行8方向30ms完整循环及15/16/01/02循环，切换深浅底、正常总览与1024放大，核对帧计数变化和播放采样截图；结合全帧静态审阅判定。',
   'timing':'APNG逐帧解码核验每帧30ms，共16帧480ms，像素逐一与最终PNG相同。浏览器显示采样受屏幕刷新约束，不把截图当每30ms录像证据。',
   'standing':'8张单独生成的双脚落地站姿；不是拿行走帧充当idle。',
   'realSources':'136个独立原生1254×1254生成来源；原图SHA及解码成品像素SHA均不重复。只做公共倍率缩小和根点注册，无镜像、插帧、局部扭曲或平移旧姿势凑槽。'
 },
 'directions':{d:{'status':'accepted','walkFrames':16,'idleFrames':1,'frameDurationMs':30,'loopDurationMs':480,'notes':observations[d]} for d in m['directions']},
 'nativeBoundaryException':{'slot':'E06','archive':'E03-v1','observed':'原生最右缘仅3个alpha>8像素，最大65；4倍实际查看为完整金属尖端抗锯齿，非缺尖，导出全alpha轮廓保留边距。'},
 'evidence':[{'file':p,'sha256':sha(R/p)} for p in evidence],
 'blockingSlots':[],'missingSlots':[],'clientIntegration':'not_performed','actualModel':None,'actualQuality':None,
 'modelDisclosure':'内置入口未披露实际型号及质量；配置目标不作为实际返回证明。',
 'files':files
}
write(O/'visual-acceptance.json',report)
m.update(visualReview='accepted_offline',acceptedAt=now,visualAcceptanceRecord='visual-acceptance.json',sourceRetentionRecord='source-retention.json',clientValidation='not_performed')
write(O/'manifest.json',m)
write(O/'source-retention.json',{'character':m['character'],'status':'cleanup_pending','policy':'用户2026-09-23授权只保留最终图片、设计、接入与文字来源；历史请求中的原图路径在删除后作为历史来源标识保留。','cleanupRecord':'../../10-work/cleanup-20260928/result.json'})
spec=importlib.util.spec_from_file_location('review_builder',R/'10-tools/build_review.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
html=mod.HTML.replace('__MANIFEST__',json.dumps(m,ensure_ascii=False))
html=html.replace('真实图片序列，每帧30毫秒，完整16帧一圈480毫秒。缺槽留空；文件齐全不代表美术通过。','128张行走和8张独立站立已通过本次素材与离线验收。每帧30毫秒，完整16帧一圈480毫秒。')
html=html.replace('${M.visualReview}',"${M.visualReview==='accepted_offline'?'离线验收通过':M.visualReview}")
html=html.replace('深底逐帧</a> · <a href="contact/${d}-light.jpg">浅底逐帧</a>','深底逐帧</a> · <a href="contact/${d}-light.jpg">浅底逐帧</a> · <a href="loops/${d}.png">循环APNG</a>')
(O/'index.html').write_text(html,encoding='utf-8')
print(json.dumps({'status':'accepted_offline','walk':128,'idle':8,'manifestSHA256':sha(O/'manifest.json')},ensure_ascii=False))
