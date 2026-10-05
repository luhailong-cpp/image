
# RETIRED_20261005: direct human timing correction supersedes historical writers.
raise SystemExit("Retired: use tools/build_preview.py, build_delivery.py, build_run_board.py and build_timing_grounding.py; run60ms/960ms.")
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
sheet=Image.new('RGB',(1600,736),(32,46,50));d=ImageDraw.Draw(sheet);sources=[]
for i in range(16):
 p=ROOT/'runtime/run/W'/f'{i:02d}.png';im=Image.open(p).convert('RGBA')
 crop=im.crop((100,700,900,1020)).resize((400,160),Image.Resampling.LANCZOS)
 x=(i%4)*400;y=(i//4)*184;sheet.paste(crop,(x,y),crop)
 d.line((x,y+(941.6875-700)*.5,x+399,y+(941.6875-700)*.5),fill=(171,153,77));d.text((x+8,y+164),f'W / {i:02d}',fill=(255,240,214))
 sources.append({'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out=ROOT/'review/run_W_feet_contact_20261003.png';sheet.save(out)
(ROOT/'review/run_W_feet_contact_20261003.json').write_text(json.dumps({'sources':sources,'commonCrop':[100,700,900,1020],'operation':'same fixed diagnostic crop and isotropic half-size preview only, runtime unchanged','sha256':hashlib.sha256(out.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
h=(ROOT/'review/run_E_preview.html').read_text(encoding='utf-8').replace('东向','西向').replace('run/E','run/W').replace('· E 跑步','· W 跑步').replace('"E / "','"W / "').replace('09/10脚向已局部修正，09支撑高度6–9像素残差与循环连续性待动态/客户端滑步复核。','16帧已导出；肩肘持物、足轴与实图相位已有静态记录，首尾/步频/根与滑步待动态和客户端复核。')
(ROOT/'review/run_W_preview.html').write_text(h,encoding='utf-8')
for p in (ROOT/'work').glob('run_W_*.png.generation.json'):
 r=json.loads(p.read_text(encoding='utf-8'));pp=ROOT/r['prompt']
 r['submittedParameters']['prompt']=pp.read_text(encoding='utf-8-sig')
 r['timeEvidence']={'generatedAtSource':'time string embedded in generated PNG C2PA; not an explicit model or quality report','hostReceiptModelDisclosed':False,'hostReceiptQualityDisclosed':False}
 p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
import run_timing_1200; run_timing_1200.update()

