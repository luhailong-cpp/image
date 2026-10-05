
# RETIRED_20261005: direct human timing correction supersedes historical writers.
raise SystemExit("Retired: use tools/build_preview.py, build_delivery.py, build_run_board.py and build_timing_grounding.py; run60ms/960ms.")
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'review/run_E_grounding_phase_20261003.json'
data=json.loads(P.read_text(encoding='utf-8'))
updates={
0:('平底支撑/接触姿态','右下靴底近水平、支撑膝略弯；后靴折收离地。','A近侧右腿候选','鞋尖沿右；保留。尚未见连续的脚跟滚入证据。'),
1:('承重压低','对00头胸下沉、支撑膝更弯；支撑鞋底接近同线。','A近侧右腿候选','鞋尖沿右；保留。'),
2:('承重/收腿通过','v2近侧腿支撑、另一腿收至髋下；右杖/左牌过中位，头胸保持低位。','A近侧右腿候选','鞋尖沿右；保留。支撑底比00/01约高Y6像素，仍需动态观察。'),
3:('脚尖蹬离','后足后跟抬起仅前尖接近共同线，前腿抬起向右送膝。','A离地候选','两脚沿侧向矢状面，脚尖向下是蹬地踝角，不能误判外撇。02到03位移较大待动态。'),
4:('腾空','两靴均离共同线，前腿展开、后膝折回。','无','两靴朝右的侧轮廓可读，保留。'),
5:('腾空下降','前靴下落靠近参考线，后靴折收；非高腾空。','无','前脚抬趾，脚掌面与运动平面一致；保留。04到05下降跨度待动态。'),
6:('下降/落地准备','v3前靴脚跟仍高于共同线，脚尖抬起；后靴离地，近侧收腿遮挡远侧支撑腿。','B远侧左腿即将承重候选','已替换早期平底接触稿；按新图不再标初始平底接触。'),
7:('脚跟接触准备','v4前靴脚跟接近共同线，脚尖仍上翘；后靴折收。','B远侧左腿候选','已替换此前平底过低稿，后靴不作为地面标尺。'),
8:('远腿支撑/承重','v3远侧左靴放平承重，近侧回收大腿在前方遮挡，关节路径可辨。','B远侧左腿候选','支撑鞋尖侧向右，保留。实际鞋底窗口Y945–949。'),
9:('承重压低','v8两靴侧向外撇改善；前靴平底、后腿折收，头部占幅经独立重画回落，支撑踝局部延展。','B远侧左腿候选','仍有地面残差：鞋底窗口中位951，比08约低6像素、比10约低9像素。不能标接地通过。'),
10:('低通过/承重','v6近侧收腿靠髋下，两手随肩肘过中位；两靴侧向明确。','B远侧左腿候选','原后靴朝镜头外转已改善，头胸位置接近旧v5。窗口鞋底中位942。'),
11:('脚尖蹬离','后靴抬跟、前掌向下接近共同线，前膝送出。','B离地候选','向下踝角符合蹬离，鞋尖仍在跑动矢状面；10到11幅度待动态。'),
12:('短腾空/收膝','源run_E_13_v3：两靴明确离地，前膝屈起、后膝折收。','无','前靴倾斜向下是腾空踝角；未见必须改成垂直或水平的依据，先保留。'),
13:('腾空/前腿展开','源run_E_12_v2：前腿伸向右，足跟仍离地，后腿折收。','无','脚掌与前伸方向相符；保留。'),
14:('下降/接触准备','前靴脚跟近地，脚尖抬起；后膝收回。','A近侧右腿候选','脚尖侧向右，保留。'),
15:('平底接触/支撑','前靴已放平，后靴离地；与00相接延续同支撑。','A近侧右腿候选','鞋尖沿右；保留。循环接缝仍待动态。')
}
for f in data['frames']:
 i=f['index'];phase,evidence,leg,note=updates[i]
 p=ROOT/f['file'];r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
 f.update(sha256=hashlib.sha256(p.read_bytes()).hexdigest(),source=r['derivedFrom'][0],observedPhase=phase,pixelEvidence=evidence,supportLegIdentity=leg,note=note)
 f['footDirectionReview']='按本图踝关节与鞋尖方向独立检查；不把07方向作为已确认标准'
data['reviewMethod']='人工查看更新后的E全16接触表、固定窗口脚部表及09/10原生单帧，再与09弓足少女当前E全16对照；根据实图标相位。静态检查不等于浏览器/客户端动态通过。'
data['currentTiming']={'frameMs':75,'frameCount':16,'loopMs':1200,'status':'用户最新明确参数；旧相位权重不应用。动态与客户端未验。'}
data['grounding']={'sourceCanvasGroundTrialY':960,'fixedNominalRoot':[511.5,941.6875],'cameraRegistration':'全E16从各自1254原生全画布统一缩至901，固定置于1024画布(61,97)；无逐帧bbox参数或贴鞋底平移。','cameraEvidence':'records/run_E_global_camera_registration_20261003_r3.json','pixelLandmarks':'review/run_E_ground_landmarks_20261003.json','calibrationStatus':'已统一相机，根仍试值；相机配准不是解剖或接地通过。'}
data['currentBlockers']=['浏览器iab不可用，CUA库存apps/browsers为空；无浏览器动态观察证据。','E09承重底相对08/10仍偏低6–9像素，保留待客户端滑步验证，不为最低像素同一行继续重画。','客户端目录存在但此批素材未接入，客户端运行与根/滑步未验。']
data['laterUserSteering']='用户撤回07整套正确及垂直正确的说法；最新要求参考09弓足少女逐图检查脚轴、肩肘和承重，正确帧保留。统一每帧75ms、16帧1200ms，旧节奏与权重停用。'
data['archerComparison']='review/run_EW_archer_comparison_20261004.json'
data['dynamicObserved']=False;data['clientValidated']=False
data['conclusion']='E已导出16张独立原生来源，09/10脚向已局部改善；尚不能认定完整方向的承重/速度/动态通过。'
P.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Updated E16 actual SHA/phase,75ms x16=1200ms, no dynamic approval')


import run_timing_1200; run_timing_1200.update()

