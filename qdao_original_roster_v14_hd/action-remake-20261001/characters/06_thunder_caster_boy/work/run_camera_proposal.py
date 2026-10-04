import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[3]
S=901/1024;TX=61;TY=97
files=sorted((ROOT/'runtime/run/E').glob('*.png'))
sheet=Image.new('RGB',(1280,5*284),(32,48,53));d=ImageDraw.Draw(sheet)
idle=Image.open(REPO/'qdao_original_roster_v14_hd/recovery-20260921/06-final/runtime/idle/E.png').convert('RGBA')
canvases=[('IDLE E',idle)]
for p in files:
 im=Image.open(p).convert('RGBA');out=Image.new('RGBA',(1024,1024))
 out.alpha_composite(im.resize((901,901),Image.Resampling.LANCZOS),(TX,TY))
 canvases.append(('E '+p.stem+' / global .88',out))
for i,(name,im) in enumerate(canvases):
 x=(i%5)*256;y=(i//5)*284
 t=im.resize((256,256),Image.Resampling.LANCZOS)
 sheet.paste(t,(x,y),t);d.line((x,y+235,x+255,y+235),fill=(204,184,121));d.text((x+8,y+261),name,fill=(247,238,215))
out=ROOT/'review/run_E_global_camera_proposal.png';sheet.save(out)
(ROOT/'review/run_E_global_camera_proposal.json').write_text(json.dumps({'purpose':'uniform camera normalization only; not anatomy or ground-contact repair','matrixRuntimeSpace':[[S,0,TX],[0,S,TY],[0,0,1]],'sourceRootManual':[512,960],'destinationRoot':[S*512+TX,S*960+TY],'basis':'Manually compare approved E idle to full16 contact sheet. Choose single global 0.88 scale based on consistent head/camera occupancy; source support-ground trial y960 from visually flat support soles, never per-frame minima. E07/E10 deviations remain evidence for redraw.','appliedToRuntime':False,'runtimeFiles':[{'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

