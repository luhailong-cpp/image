from pathlib import Path
from PIL import Image
import json
from datetime import datetime,timezone
b=Path(__file__).resolve().parents[2];out=Path(__file__).resolve().parent
s=json.loads((out/'ns-selection.json').read_text(encoding='utf-8'))
animations=[]
for di in ['N','S']:
 for suffix,wanted in [('1200ms',1200),('slow',4800)]:
  p=out/f'ns-{di}-{suffix}.apng';im=Image.open(p);total=0
  assert im.n_frames==16
  for i in range(im.n_frames):im.seek(i);total+=im.info.get('duration',0)
  assert total==wanted,(p,total)
  animations.append({'file':p.name,'frames':im.n_frames,'totalMs':total})
r={'reviewedAt':datetime.now(timezone.utc).isoformat(),'reviewer':'continue_cast','status':'10_static_candidates_ready_for_parent_review','formalRuntimeWritten':False,'userAcceptance':False,'visualEvidence':{'individuallyViewed':'所有新候选生成返回均实际完整查看；10个旧原生host目标均实际查看；09N/S正式连图及64张runtime构建对照全部查看','finalSequenceContactViewed':['ns-N-updated-contact.png','ns-S-updated-contact.png','ns-N-updated-feet.png','ns-S-updated-feet.png']},'passes':['N07→08→09：屏右脚从少量后底转成鞋跟朝后/脚掌朝地，旧08整底突然翻到09的问题已明显减小','N13→14→15→16：左脚下降预落地、右腿后摆关系清楚；不再15整块左底向后再16突然翻面','N10→11→12：11持扇臂已收回身体附近，扇的角度连接低后摆与肩侧回摆，未换手','S01→02→03→04和09→10→11→12：02/03/10/11支撑足不再大块露底，膝踝连接到朝S平底，后腿抬膝保留','S13→14→15：14屏左后足长轴从向左斜甩变成沿S纵向，仍有腾空间隙','角色身份、右手扇、左空手保留；未人为逐帧挪根或按bbox缩放'], 'selectedNativeFootBottoms':[{ 'slot':f"{f['direction']}{f['frame']:02d}",'alphaBBoxBottomExclusive':f['review']['nativeAlphaBBox'][3],'deltaFrom1191':f['review']['nativeAlphaBBox'][3]-1191} for f in s['frames']],'remainingObservations':['N07/N08底界为1154/1176，距参考地面37/15px；N14为1140距51px，N15已到1191，可视作提前接近/初接触而不是继续宣称全腾空。父线程应按实图复核相位停留。','S02/S03/S10/S11底界1192/1185/1196/1199，约-6到+8px小高差；S14底界1101仍有90px腾空间隙，不应自动贴地。','N02/N10的支撑屈膝/压低仍偏轻；N05—10左臂停留较长，N11左腕回收再接12的摆幅仍可在实际播放时观察。本轮未扩大改图范围。','S01/09保留初接触露底，S15/16保留后半空中过渡；如播放仍显前踢，优先审这些直接相邻槽，不可据单帧露底将全部空中帧判错。','局部生成带来少量发/脸/衣缘轮廓变化，未用程序平移或缩放掩盖；不宣称像素级完全不变。','实际动态播放本代理未执行。本次可证明静态连续结构与文件完整性，最终1200ms播放与用户验收由主窗口进行。'],'animations':animations,'model':{'configuredTarget':'GPT Image 2.5 Sunburst / max','actualModel':None,'actualQuality':None,'route':'builtin host-managed','evidence':'各张request/prompt/receipt/generation记录完整，未披露实际版本/质量'},'discardedCandidates':{'run-S-02-archer-v1':'支撑底界1176略高，v3更接近地面','run-S-02-archer-v2':'延伸过多到底界1212，v3改为1192','run-N-11-archer-v1':'输入参考超过5张，未生成图；v2使用5张成功'}}
(out/'ns-repair-review.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
s['sequenceStaticReview']='audit/archer-reference/ns-repair-review.json'
s['residualSummary']='N02/N10屈膝弱；N05-10左臂停留和N11左腕原相位需实播；新S承重底界偏差-6..+8px；无本次实际动态/用户验收结论。'
(out/'ns-selection.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':len(s['frames']),'animations':animations,'review':'ns-repair-review.json'},ensure_ascii=False))

