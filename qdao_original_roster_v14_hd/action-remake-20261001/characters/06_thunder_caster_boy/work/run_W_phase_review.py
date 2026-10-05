
# RETIRED_20261005: direct human timing correction supersedes historical writers.
raise SystemExit("Retired: use tools/build_preview.py, build_delivery.py, build_run_board.py and build_timing_grounding.py; run60ms/960ms.")
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
notes=[
('接触/支撑','前下靴接近平底，后腿折收离地；00v2已修近肩到牌的连接。','前下支撑腿；髋根被袍摆部分遮挡，解剖左右待连播追踪。'),
('承重压低','头胸下沉、支撑膝更屈；后靴更靠近髋下，靴底延续支撑。','延续00的前下支撑链，不能仅按提示词认定左右。'),
('低通过/承重','02v2修掉错误的第二支撑，后靴现藏于髋下并离地；两臂过中位。','前下唯一支撑腿；近远髋链需与前后帧持续追踪。'),
('脚尖蹬离','后腿伸展、后跟升高，前尖接近共同地面；前腿上送。','后腿蹬离，前腿腾空；可見两关节链。'),
('短腾空/收膝','两靴离地，前膝上抬、后膝折收。','近前腿在髋部压过远后腿候选。'),
('腾空展开','前腿向左展开、抬趾，后膝回收；两靴在地面上方。','近前/远后候选；前靴斜底需连续侧向观察。'),
('下降准备','06v2由已接触稿重画，前靴抬趾并明确离地。','前向左腿下降、后腿收回；不把旧06v1当现帧。'),
('脚跟接触准备','前脚跟比06降低，脚尖仍上翘，后靴离地。','前向腿将承重；足轴沿运动方向。'),
('平底支撑','前靴平底、前膝微屈，后腿折起；与07相接近。','前向支撑大腿遮挡后收腿，近侧支撑可读；仍按可见链而非提示词追踪。'),
('承重/缓冲','支撑膝压低、两臂收回，后靴折向髋下。头部压低幅度较小，待动态。','延续08支撑，后腿为恢复腿。'),
('低通过/承重','单支撑靴平底，后靴收至髋下；近牌前向过中位，远杖退至后肋。','近支撑腿遮挡后收靴，单支撑可读。'),
('脚尖蹬离','后腿伸展、后跟升高，脚尖接近地面；前腿向左上送。','后腿蹬离；原生要求左近腿，实图仍需整段髋链复核。'),
('短腾空','两靴离地，前膝屈、后膝收，近牌前摆远杖后摆。','前后两腿清楚；解剖归属须同11/13连看。'),
('腾空展开','前腿伸向左、后腿收回，伸腿跨度较大；离地可辨。','前腿不是站立腿；后腿折收。'),
('脚跟接触准备','前腿已收回身下，脚尖上翘，脚跟近地；不能称高腾空。','前向腿将承重，后靴离地。'),
('平底接触/首尾衔接','前靴由抬趾过渡至平底支撑，后腿仍收回；待核对15到00。','延续14前向承重链，首尾不应突然换腿。')]
holds=[75]*16
frames=[]
for i,(phase,evidence,leg) in enumerate(notes):
 p=ROOT/'runtime/run/W'/f'{i:02d}.png'
 if not p.exists():continue
 r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
 frames.append({'index':i,'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':r['derivedFrom'][0],'observedPhase':phase,'pixelEvidence':evidence,'visibleLegChain':leg,'handChain':'近左肩对应符牌，远右臂对应雷杖；从肩肘手追踪，非按道具在图左右判断。','footDirection':'根据本图侧向鞋尖/膝踝检查；蹬地与腾空踝角不一律视为外撇。','currentFrameMs':75})
data={'character':'06_thunder_caster_boy','action':'run','direction':'W','date':'2026-10-03','frames':frames,'exportedSlots':len(frames),'sourceUnique':len({f['source']['sha256'] for f in frames})==len(frames),'actualModel':None,'actualQuality':None,'target':'GPT Image2.5 Sunburst/max','camera':{'matrixNativeToRuntime':[[901/1254,0,61],[0,901/1254,97],[0,0,1]],'sameForAll':True,'rootTrial':[511.5,941.6875],'purpose':'同E的统一相机/比例配准，不是脚底逐帧贴线或解剖修复'},'currentTiming':{'frameMs':75,'frameCount':16,'loopMs':1200,'status':'用户最新明确参数，旧相位权重停用，动态与客户端未验。'},'staticReview':'已实际查看全16单帧、完整接触表与固定脚部表，并与09当前W全16对照；SHA绑定见review/run_EW_archer_comparison_20261004.json','dynamicObserved':False,'clientIntegrated':False,'limitations':['本机浏览器iab不可用，未观察浏览器播放；GIF文件生成不等于动态通过。','客户端目录存在但本批素材未接入，根/滑步/地面残差与运行未验证。','髋部部分遮挡，左右支撑切换需要结合全组可见链，不能仅继承生成提示词标签。','02到03、10到11的摆臂跨度与15到00接缝待动态观察。']}
(ROOT/'review/run_W_grounding_phase_20261003.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('W phase slots',len(frames),'current ms',sum(holds))


import run_timing_1200; run_timing_1200.update()


