import json,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[1]
src=json.loads((R/'review/run_archer_EW_reference_sources_20261003.json').read_text(encoding='utf-8'))
rows=[]
for d in ['E','W']:
 for i in range(16):
  p=R/'runtime/run'/d/f'{i:02d}.png';r=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf-8'))
  phase='承重/低位通过' if i in [0,1,2,8,9,10,15] else '蹬离' if i in [3,11] else '短暂腾空/前腿送出' if i in [4,5,12,13] else '落地准备'
  rows.append({'direction':d,'index':i,'file':p.relative_to(R).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source':r['derivedFrom'][0], 'decision':'保留当前鞋轴，不因参考更换而重复绘制','staticFootAxis':'鞋尖沿画面右侧行进，膝踝与鞋掌侧面连续；蹬离/前摆时露底属于踝屈伸，未见需重画的横向外撇。' if d=='E' else '鞋尖沿画面左侧行进，膝踝与鞋掌侧面连续；前摆翘尖露底不作为外八误报。','phaseObserved':phase,'handOwnership':'逐图追肩肘手：右手雷杖、左手方符牌，当前未见新换手。','dynamicPassed':False})
data={'reviewedAt':'2026-10-04','method':'实际查看09 manifest列出的E/W全16接触表，并与06当前E/W全16接触表及已查看脚部表对照；不沿用旧通过结论。','referenceSources':src,'scope':'脚轴/可见膝踝/肩肘持物静态比较；不是09或06的完整动态与客户端通过','currentTiming':{'frameMs':75,'loopMs':1200},'rows':rows,'remainingIssues':[{'scope':'E09','issue':'已知支撑鞋底6–9px残差保留，需客户端根/滑步验证；不为最低像素齐线继续盲改。'},{'scope':'E02→03、E10→11、W02→03、W10→11','issue':'肩肘摆幅变化较集中，静态可读但75ms逐帧播放的连续性尚未实际观测。'},{'scope':'W00/08','issue':'髋部部分被衣摆遮挡，已确认鞋轴与持物，支撑腿近远归属仍应结合全圈动态追链，不根据提示词宣称左右脚通过。'},{'scope':'E/W15→00','issue':'循环首尾及整体根/滑步未接客户端；不因文件齐全标为动态通过。'}], 'clientIntegrated':False,'dynamicObserved':False}
(R/'review/run_EW_archer_comparison_20261004.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
md='已实际读取09当前manifest的E/W各16张并制作同画布接触表，再与06当前E/W全组逐张比较。32帧的鞋尖均沿各自横向行进方向，可见膝踝连续；暂保留当前鞋轴。蹬地、腾空翘尖所露鞋底不等于脚掌外撇。手物仍为右杖左牌。逐帧SHA和来源见同名JSON。\n\n剩余：E09已知6–9px支撑残差；E/W的02→03、10→11摆臂转换；W00/08衣摆遮挡下的近远腿连续追踪；15→00循环首尾。以上需75ms/帧的真实动态和客户端根/滑步检查，不因静态保留而当作整组通过。未接客户端，本机浏览器动态未观察。\n'
(R/'review/run_EW_archer_comparison_20261004.md').write_text(md,encoding='utf-8')
print('E/W32 current SHA bound static comparison saved; no dynamic approval')
