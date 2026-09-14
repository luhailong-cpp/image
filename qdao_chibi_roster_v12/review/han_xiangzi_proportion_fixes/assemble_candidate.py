"""Assemble six authored native-cell replacements into a separate candidate."""
from pathlib import Path
from PIL import Image
import hashlib, json, shutil

REVIEW=Path(__file__).resolve().parent
ROOT=REVIEW.parents[1]
FORMAL=ROOT/"30_han_xiangzi"
OUT=ROOT/"candidate-stable-body/30_han_xiangzi"
SOURCE=OUT/"source"
REPLACEMENTS={"N":(1,),"NE":(1,),"SE":(1,3),"W":(1,),"NW":(1,)}
DIRECTIONS=["N","NE","E","SE","S","SW","W","NW"]


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rgba_sha(im):return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()
def save_json(p,j):p.write_text(json.dumps(j,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

assert OUT.resolve().is_relative_to((ROOT/"candidate-stable-body").resolve())
assert OUT.name=="30_han_xiangzi" and OUT.resolve()!=FORMAL.resolve()
SOURCE.mkdir(parents=True,exist_ok=True)
manifest_path=FORMAL/"manifest.json"
manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
summary={"character":"30_han_xiangzi","formal_manifest_path":str(manifest_path),"formal_manifest_sha256":sha(manifest_path),"operation":"exact whole-native443 cell replacement only; preserve phase and all other source pixels","replacements":[],"unchanged_cells":0,"sheets":{},"common_scale_cli_string":"1.024390243902439","additional_edge_despill":False,"portrait_source":str(FORMAL/"portrait.png"),"portrait_sha256":sha(FORMAL/"portrait.png"),"approved_for_publication":False}
for kind,source in manifest["sources"].items():
 src=Path(source["path"])
 assert sha(src)==source["sha256"],str(src)
 original=Image.open(src).convert("RGB");working=original.copy()
 cw,ch=source["native_cell_size"];assert(cw,ch)==(443,443)
 cols,rows=(4,2) if kind=="idle" else(4,4)
 order=DIRECTIONS if kind=="idle" else manifest["walk"]["raw_sheet_direction_order"][kind]
 dest=SOURCE/(kind+".png")
 assembly={"version":12,"operation":"replace six reviewed source-art cells; all unselected cells retained pixel-for-pixel","output_path":str(dest),"output_size":list(original.size),"output_grid":[cols,rows],"native_cell_size":[cw,ch],"upstream_formal_manifest":str(manifest_path),"upstream_formal_manifest_sha256":sha(manifest_path),"upstream_source_path":str(src),"upstream_source_sha256":sha(src),"direction_order":order,"sources":[],"phase_order_changed":False,"body_bbox_fit":False,"part_scaling":False,"mirrored_frames":False,"new_poses_generated_by_script":False}
 upstream_assembly=src.with_suffix(".assembly.json")
 if upstream_assembly.exists():
  assembly["upstream_assembly_path"]=str(upstream_assembly);assembly["upstream_assembly_sha256"]=sha(upstream_assembly)
 for index in range(cols*rows):
  direction=order[index] if kind=="idle" else order[index//8]
  phase=0 if kind=="idle" else index%8+1
  box=[index%cols*cw,index//cols*ch,(index%cols+1)*cw,(index//cols+1)*ch]
  previous=original.crop(box)
  record={"direction":direction,"action":"idle" if kind=="idle" else"walk","phase":phase,"target_grid_row_col":[index//cols,index%cols],"target_box_xyxy":box,"upstream_source_path":str(src),"upstream_source_sha256":sha(src),"upstream_source_box_xyxy":box,"upstream_cell_rgba_sha256":rgba_sha(previous),"phase_preserved":True}
  replaced=kind!="idle" and phase in REPLACEMENTS.get(direction,())
  if replaced:
   folder=REVIEW/f"{direction}-{phase:02d}";cell_path=folder/"final-cell.png";raw_path=folder/"final-raw.png";cell=Image.open(cell_path).convert("RGB")
   assert cell.size==(443,443)
   expected=Image.open(raw_path).convert("RGB").resize((443,443),Image.Resampling.LANCZOS)
   assert cell.tobytes()==expected.tobytes(),str(cell_path)
   working.paste(cell,(box[0],box[1]))
   record.update(replacement=True,source="built-in image_gen edit",source_path=str(cell_path),source_sha256=sha(cell_path),raw_source_path=str(raw_path),raw_source_sha256=sha(raw_path),raw_size=list(Image.open(raw_path).size),whole_raw_square_scale_to_cell=443/Image.open(raw_path).width,provenance_path=str(folder/"final-provenance.json"),provenance_sha256=sha(folder/"final-provenance.json"),visual_review_path=str(folder/"visual-qc.json"),visual_review_sha256=sha(folder/"visual-qc.json"),output_cell_rgba_sha256=rgba_sha(cell))
   summary["replacements"].append({"direction":direction,"phase":phase,"sheet":kind,"target_box_xyxy":box,"final_cell_path":str(cell_path),"final_cell_sha256":sha(cell_path)})
  else:
   record.update(replacement=False,source="unchanged formal source cell",output_cell_rgba_sha256=rgba_sha(previous));summary["unchanged_cells"]+=1
  assembly["sources"].append(record)
 if kind in ["idle","s_e"]:
  assert working.tobytes()==original.tobytes();shutil.copyfile(src,dest)
 else:working.save(dest)
 check=Image.open(dest).convert("RGB")
 for record in assembly["sources"]:
  cell=check.crop(record["target_box_xyxy"]);assert rgba_sha(cell)==record["output_cell_rgba_sha256"]
  if not record["replacement"]:assert cell.tobytes()==original.crop(record["target_box_xyxy"]).tobytes()
 # Any unused outer source pixels are also unchanged, including idle's1774x887 remainder.
 if check.width>cw*cols:assert check.crop((cw*cols,0,check.width,check.height)).tobytes()==original.crop((cw*cols,0,check.width,check.height)).tobytes()
 if check.height>ch*rows:assert check.crop((0,ch*rows,check.width,check.height)).tobytes()==original.crop((0,ch*rows,check.width,check.height)).tobytes()
 assembly["output_sha256"]=sha(dest)
 save_json(dest.with_suffix(".assembly.json"),assembly)
 summary["sheets"][kind]={"source":str(src),"source_sha256":sha(src),"output":str(dest),"output_sha256":sha(dest),"replacement_count":sum(r["replacement"] for r in assembly["sources"]),"unselected_cells_pixel_equal":True}
assert len(summary["replacements"])==6 and summary["unchanged_cells"]==66
save_json(SOURCE/"assembly-summary.json",summary)
print(json.dumps({"output":str(OUT),"replacements":summary["replacements"],"unchanged_cells":summary["unchanged_cells"]},ensure_ascii=False))
