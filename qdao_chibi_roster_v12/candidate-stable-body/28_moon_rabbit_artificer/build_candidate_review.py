from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
root=Path(__file__).resolve().parent
outdir=root/"processing"/"candidate-review";outdir.mkdir(exist_ok=True)
DIRECTIONS=("N","NE","E","SE","S","SW","W","NW")
matte=(238,235,221,255)
def board(items,cols,name):
 rows=(len(items)+cols-1)//cols
 out=Image.new("RGBA",(cols*512,rows*532),matte);draw=ImageDraw.Draw(out)
 for i,(label,path) in enumerate(items):
  im=Image.open(path).convert("RGBA")
  if im.size!=(512,512):im=im.resize((512,512),Image.Resampling.LANCZOS)
  x=i%cols*512;y=i//cols*532;out.alpha_composite(im,(x,y+20));draw.text((x+10,y),label,fill="black")
 out.convert("RGB").save(outdir/name)
board([("NW IDLE",root/"idle"/"NW.png")]+[(f"NW CANONICAL {i:02}",root/"walk"/"NW"/f"{i:02}.png") for i in range(1,9)],3,"NW-canonical-eight-plus-idle.png")
for group,ds in enumerate((DIRECTIONS[:4],DIRECTIONS[4:])):
 items=[]
 for phase in ("idle","01","05"):
  for d in ds:items.append((f"{d} {phase.upper()}",root/"idle"/f"{d}.png" if phase=="idle" else root/"walk"/d/f"{phase}.png"))
 board(items,4,f"contacts-{group+1}.png")
board([("PORTRAIT",root/"portrait.png")]+[(f"IDLE {d}",root/"idle"/f"{d}.png") for d in DIRECTIONS],3,"portrait-and-idle-eight.png")
sequence=[root/"idle"/"NW.png"]*4+[root/"walk"/"NW"/f"{i:02}.png" for i in range(1,9)]*3+[root/"idle"/"NW.png"]*4
frames=[]
for p in sequence:
 frame=Image.new("RGBA",(512,512),matte);frame.alpha_composite(Image.open(p).convert("RGBA"));frames.append(frame.convert("RGB"))
frames[0].save(outdir/"NW-idle-transition.gif",save_all=True,append_images=frames[1:],duration=90,loop=0,disposal=2)
manifest=json.loads((root/"manifest.json").read_text(encoding="utf8"));qc=json.loads((root/"qc.json").read_text(encoding="utf8"))
before=json.loads((root/"processing"/"before-despill-invariants.json").read_text(encoding="utf8"))
for relative,data in before.items():
 im=Image.open(root/relative).convert("RGBA")
 assert hashlib.sha256(im.getchannel("A").tobytes()).hexdigest()==data["alpha_sha256"],relative
 assert hashlib.sha256(im.getchannel("G").tobytes()).hexdigest()==data["green_sha256"],relative
 assert list(im.getchannel("A").getbbox())==data["alpha_bbox"],relative
phase_plan=json.loads((root/"source"/"phase-plan.json").read_text(encoding="utf8"))
audit={"character_id":root.name,"display_name_zh":"月兔机关师","stage":"passed_numeric_qc_pending_visual_review","canonical_first_contact":"RIGHT","cyclic_shifts":{d:v["cyclic_offset"] for d,v in phase_plan["directions"].items()},"movement_frames":64,"idle_frames":8,"media_files":89,"common_scale":manifest["alignment"]["common_scale"],"alignment_version":3,"no_per_frame_scale":True,"source_completed_56_and_other_NW_5_exact_cell_pixels":True,"source_unique_frames_per_direction":8,"despill_alpha_and_green_sha_unchanged_frames":len(before),"despill_all_alpha_bounds_unchanged":True,"despill_policy":manifest["edge_despill"],"max_body_scale_cv":max(v["body_scale_cv"] for v in qc["directions"].values()),"cross_direction_mean_height_ratio":qc["cross_direction_mean_height_ratio"],"max_idle_walk_height_drift":max(v["idle_walk_height_drift"] for v in qc["directions"].values()),"max_head_axis_deviation":max(v["horizontal_body_axis_max_deviation_px"] for v in qc["directions"].values()),"visual_parent_approval_required":True,"sealed":False,"published":False}
(root/"processing"/"candidate-audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
print(json.dumps(audit,ensure_ascii=False))
