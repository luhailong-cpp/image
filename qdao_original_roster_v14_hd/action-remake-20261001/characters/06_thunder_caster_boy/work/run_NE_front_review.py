"""Bind the reviewed NE front phase observations to the frozen current PNGs."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
notes={
1:('右腿承重压低','右杖肩肘向后腰回摆、左符牌向前；支撑白绑腿局部缩短，鞋跟靠左下、鞋尖向东北远离镜头。','支撑关系与脚轴已静态改善；根和滑步未验。'),
2:('右腿承重/低通过','右支撑、另一腿返回髋下；白绑腿和膝踝链连续，右杖后摆。','支持腿足轴已改善；不能仅与01最低像素接近就标承重通过。'),
3:('右腿脚尖蹬离候选','后跟抬起、鞋尖朝东北向下接近地面；绑腿覆盖踝部，无新增裸踝。','固定诊断窗口下轮廓中位约Y980，较01/02低约43–48像素，仍须全16共同根和蹬地滚动复核；鞋轴正确不等于接地通过。'),
4:('左腿前送/短腾空','左前靴近处为鞋跟，鞋尖朝东北；右后腿露底按后收踝角保留，左牌后摆右杖前摆。','当前相机/头部占幅保留原目标，脚轴局改；离地幅度及连续性未动态验。'),
5:('左腿前送下降','左前靴鞋轴修为向东北，前脚离地余量很小；右后腿折收。','实际为下降/临落地，不标为高腾空。'),
6:('左脚下降/落地准备','前靴鞋跟下降、鞋尖朝东北，后靴离地；头部与上肢保留。','05/06高度接近，应与07/08连看；根/承重动态未验。')}
rows=[]
for i,(phase,evidence,limitation) in notes.items():
 p=ROOT/'runtime/run/NE'/f'{i:02d}.png';rec=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
 rows.append({'index':i,'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':rec['derivedFrom'][0],'observedPhase':phase,'visualEvidence':evidence,'remainingLimitation':limitation,'currentFrameMs':75,'axisStaticReviewed':True,'groundingPassed':False,'dynamicPassed':False})
out={'date':'2026-10-04','scope':'NE01–06 frozen front phase handoff; other slots owned by collaborators','frames':rows,'currentTiming':{'frameMs':75,'frameCount':16,'loopMs':1200,'oldWeightsActive':False},'camera':'Whole native canvas 1254 to1024 Lanczos, no per-frame bbox/lowest-foot adjustment; E/W transform not applied.','comparison':'Actual viewed09 bamboo archer NE01/04/09; compare ankle/boot axis only, do not copy character or frame identity. See each native generation record for actual submitted references.','currentReviewImages':['review/run_NE_contact.png','review/run_NE_feet_contact_20261003.png'],'modelTarget':'GPT Image2.5 Sunburst/max','actualModel':None,'actualQuality':None,'clientDirectoryExists':True,'clientIntegrated':False,'dynamicObserved':False,'runtimeFrozen':True,'conclusion':'6 current frames statically reviewed and source-bound; handoff to whole-circle root review. Not an overall grounding or dynamics approval.'}
(ROOT/'review/run_NE_front_review_20261004.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('NE front frozen SHA records:',len(rows))
