from pathlib import Path
import json
r=Path(__file__).resolve().parents[2]
p=r/'provenance/run/EW-grounding-review-20261003.json'
j=json.loads(p.read_text(encoding='utf-8-sig'))
updates={
('E',3):('右近脚中支撑，左远腿穿过','v3重画后支持鞋底1188/1254，已消除旧1205异常下探；右近腿前景支撑、左远腿折收过髋。','静态改善，仍待正常尺寸动态与换腿连续性。'),
('E',9):('左远脚承重缓冲','v3将前掌滚落画为平掌，脚底1179/1254，膝屈曲和近右后腿遮挡保持。','已缓解旧1174浮脚，距1184诊断线仍约5px；待动态。'),
('E',12):('左远脚蹬离','v2后左远足跖屈，前掌末次触点1179/1254；前右近腿屈膝。','旧1197下探已消除，触点较诊断线高约5px；待动态。'),
('W',10):('左近脚较深缓冲，右远腿回收','v5近左支撑脚平掌1195/1254、支撑膝深屈，右远腿后收；发带完整。','较v1原1179改善16px，仍高于W09/W11约5–10px；不得宣告动态通过。')
}
for row in j['frames']:
 key=(row['direction'],row['frame'])
 if key in updates:
  row['actualPhase'],row['visibleEvidence'],row['concern']=updates[key]
j['unresolved']=['完整E/W静态相位已复核，候选均有支撑/缓冲/蹬离/腾空，但正常尺寸动态尚未审过。','E03/E09/E12与W10已原生重画改善地面跳变，仍有约5–10px原生接触带差，需试播确认。','E04相对E03上身下沉、E05/E06高点先后与首尾接触衔接需动态重点看。','W10以固定全局W01/W02尺寸重画，局部脸部/发丝幅度有差，需动态连续性复核。','E与W原生地面带差异不能以单帧最低像素校准；全局导出根点仍未实际确认。','客户端位移速度/滑步/运行效果未验。']
j['latestSelection']='provenance/run/selection-EW.json'
p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

