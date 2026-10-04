import json,subprocess,sys
from pathlib import Path
B=Path(__file__).resolve().parents[2]
sel=json.loads((B/'work/run-NE-cast/eight-support-selection.json').read_text(encoding='utf-8'))
for s in sel:
    if s['frame'] in (10,11,16):continue
    notes='整帧与固定下半身对照逐帧查看：右手五符、左手铜铃，支撑脚连续且鞋轴朝NE。每两帧独立姿态，已确认单帧；换脚连续性另记动态复核。'
    p=subprocess.run([sys.executable,str(B/'work/run-NE-cast/eight-support-finalize.py'),'--record',s['source_record'],'--frame',str(s['frame']),'--status','single_frame_pass_pending_dynamic','--notes',notes,'--import-formal'],capture_output=True,text=True,encoding='utf-8')
    if p.returncode:raise RuntimeError(p.stdout+p.stderr)
    print('Imported NE '+str(s['frame']).zfill(2))
