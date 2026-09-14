#!/usr/bin/env python3
"""Build an independent 28 candidate. No edits to the original 56 authored poses."""
from pathlib import Path
from PIL import Image
import json, hashlib, shutil

BASE=Path(r"E:\work\image\qdao_chibi_roster_v12")
ORIGINAL=BASE/"28_moon_rabbit_artificer"
FIXES=BASE/"review"/"28_nw_arm_fixes"
ROOT=BASE/"candidate-stable-body"/"28_moon_rabbit_artificer"
SOURCE=ROOT/"source"
DIRECTIONS=("N","NE","E","SE","S","SW","W","NW")
PAIRS={"s_e":("S","E"),"n_w":("N","W"),"ne_sw":("NE","SW"),"nw_se":("NW","SE")}
CELL=443
PHASE_SHIFT={"N":4,"NE":0,"E":0,"SE":0,"S":0,"SW":4,"W":4,"NW":4}
ANATOMICAL_EVIDENCE={
"N":"Direct back view: original 01 anatomical LEFT thigh descends to forward contact while RIGHT hip/shin trails toward viewer with outsole; 05 reverses both legs and arm swing. 02/06 support ownership and 04/08 forward knee poses confirm the cycle.",
"NE":"Back-right view: near visible-ear/empty-waist side is anatomical RIGHT. Original 01 near RIGHT advancing thigh overlaps far LEFT trailing thigh, near RIGHT hand back; 05 near RIGHT thigh trails in foreground, far LEFT advances and right arm forward. Repaired 02/07/08 preserve that ownership.",
"E":"Right profile: near empty-waist/visible-ear side is anatomical RIGHT. Original 01 foreground right thigh advances with right arm back; 05 near right thigh trails over the far advancing left thigh with right arm forward. Original E07 cleanup remains selected.",
"SE":"Front-right view: near empty-waist leg from picture-left hip is anatomical RIGHT. Original 01 right thigh advances in foreground; 05 near right thigh trails across far LEFT advancing thigh. Near right arm counter-swings; selected 04/07 preserve opposite supporting legs.",
"S":"Direct front view: anatomical RIGHT is picture-left/empty-waist. Original 01 that hip and knee advance to right-foot contact, tool-side LEFT thigh trails. Original 05 tool-side LEFT advances, arms reverse. Selected original 01/02/08 arm corrections retain these legs.",
"SW":"Front-left view: near rabbit-pin/ruler side at picture-right hip is anatomical LEFT. Original 01 near LEFT thigh advances across far RIGHT thigh with near left arm back; 05 near LEFT thigh trails over the far RIGHT advancing thigh, with selected left arm forward correction.",
"W":"Left profile: near rabbit-pin/tool side is anatomical LEFT. Original 01 near LEFT thigh advances, left arm back; selected 05 shows near LEFT thigh trailing in foreground across far RIGHT advancing thigh with left arm forward. Selected 07 near-left passing confirms far-right support half.",
"NW":"Back-left view: near rabbit-pin/ruler side is anatomical LEFT. Original 01 near LEFT hip and trouser lead to supporting forward foot; far RIGHT heel trails with outsole. Original 05 far RIGHT supports while near LEFT trails in foreground. Original full 8-frame root prompt and thigh/shin overlap agree. Only original 01/02/08 near-left arms were edited; source legs retained."
}
CANONICAL=["RIGHT contact, LEFT trails","RIGHT support, LEFT heel lifts behind","RIGHT support, LEFT passes low","RIGHT support, LEFT knee advances before contact","LEFT contact, RIGHT trails","LEFT support, RIGHT heel lifts behind","LEFT support, RIGHT passes low","LEFT support, RIGHT knee advances before contact"]
EXPECTED_FINAL={
"S":"4f34544c7f4082db450f19c95b0d12b6342911360f87bacf69ff814692227163",
"N":"7d14787c28860c8b1b9891fd4730a40a10126e0b204dd3c914ba7c7c9df709c8",
"E":"69177d4c9ae7d41d443da25a3107ce450c59ce0876b6a37fc300e1da4fd3ffe3",
"W":"4de81279f4be462a449e85bd09556dcc8ccd4ce5b8cae274349d0d48b37b8e9b",
"SE":"182c61d2ec0a0f4e88dd7e24fa45535d85fb5ac0607854790786c1c0dd0065c6",
"SW":"211a0e25b08a96c5c51d89d4e24f2ce07ebb55600bce93e0c65a30b90328a4c0",
"NE":"9d51f6499aba9a75531ccdc23b96ff55aef3dccd294c9f2292f90a86c1fa4161"}
EXPECTED_FIX={1:"489de92399b3d99046a460b7d6a6377fac0a35cc95862fc35b027a908c16d387",
2:"762358c6bc18e488cfad38dde5b4d4ce2bfefc63c92dc41d2abb089fd8942fdc",
8:"3c955bac26a2461073489f3cf9b3cf4d3f9d96b898d0dc83c080e78e81637fb8"}
EXPECTED_NW="dfccdba05b2469a5442c6f650ed025197ffacac4f7e711eb4b5306b0a4389e3e"

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pixelsha(im):return hashlib.sha256(im.convert("RGBA").tobytes()).hexdigest()
def write(p,obj):Path(p).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def check(p,expected):
    if sha(p)!=expected:raise ValueError(f"Changed approved source {p}")
def cellbox(index,cols=4):
    x,y=index%cols*CELL,index//cols*CELL
    return (x,y,x+CELL,y+CELL)
def copy(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(src,dst)
    check(dst,sha(src))

def main():
    assert ROOT.resolve().is_relative_to((BASE/"candidate-stable-body").resolve())
    SOURCE.mkdir(parents=True,exist_ok=True)
    prov=SOURCE/"provenance";prov.mkdir(exist_ok=True)
    config=json.loads((ORIGINAL/"direction-sources.json").read_text(encoding="utf8"))
    if set(config)!=set(EXPECTED_FINAL):raise ValueError("Unexpected original direction configuration")
    copy(ORIGINAL/"direction-sources.json",prov/"direction-sources.original.json")
    preserved_originals={}
    for d,h in EXPECTED_FINAL.items():
        p=ORIGINAL/"source"/f"walk-{d}-final.png";check(p,h);preserved_originals[str(p)]=h
        copy(p.with_suffix(".assembly.json"),prov/f"walk-{d}-final.original.assembly.json")
        for record in config[d]:record["source"]=str(ORIGINAL/"source"/record["source"])
    nw=ORIGINAL/"source"/"walk-NW-root.png";check(nw,EXPECTED_NW);preserved_originals[str(nw)]=EXPECTED_NW
    config["NW"]=[]
    for i in range(8):
        phase=i+1
        if phase in EXPECTED_FIX:
            p=FIXES/f"{phase:02}"/"candidate-cell-443.png";check(p,EXPECTED_FIX[phase])
            config["NW"].append({"source":str(p),"rows":1,"cols":1,"index":0,"edit_scope":"near left sleeve/arm/hand only","original_phase":phase})
            for name in ("candidate-native.png","candidate-cell-443.png","input-cell-443.png","prompt.txt","prompt-refine.txt","generated-source.json","reference-source.json","qc.json"):
                f=p.parent/name
                if f.exists():copy(f,prov/"NW-arm-fixes"/f"{phase:02}"/name)
        else:
            config["NW"].append({"source":str(nw),"rows":2,"cols":4,"index":i,"original_phase":phase})
    write(SOURCE/"direction-sources.before-canonical.json",config)
    phase_plan={"character_id":ROOT.name,"display_name_zh":"月兔机关师","policy":"Anatomical RIGHT foot contact first in every direction; whole 8-frame cyclic shift only", "canonical_phases":CANONICAL,"directions":{}}
    for d in DIRECTIONS:
        original_cycle=config[d]
        for i,pose in enumerate(original_cycle):pose["original_phase"]=i+1
        shift=PHASE_SHIFT[d]
        config[d]=[original_cycle[(i+shift)%8] for i in range(8)]
        prompt=ORIGINAL/"prompts"/("walk-NW-root.txt" if d=="NW" else f"walk-{d}.txt")
        selected=ORIGINAL/"source"/("walk-NW-root.png" if d=="NW" else f"walk-{d}-final.png")
        phase_plan["directions"][d]={"original_first_contact":"LEFT" if shift else "RIGHT","cyclic_offset":shift,"new_phase_to_original_phase":[p["original_phase"] for p in config[d]],"evidence":ANATOMICAL_EVIDENCE[d],"assessment_basis":"visual thigh/hip ownership, foreground occlusion, arm counter-swing, supporting leg sequence; not shoe XY alone","selected_upstream_path":str(selected),"selected_upstream_sha256":sha(selected),"original_prompt_path":str(prompt),"original_prompt_sha256":sha(prompt)}
    write(ROOT/"direction-sources.json",config)
    write(SOURCE/"phase-plan.json",phase_plan)
    write(ROOT/"candidate-plan.json",{
        "character_id":"28_moon_rabbit_artificer","display_name_zh":"月兔机关师","stage":"independent candidate; pending parent visual review; do not seal/publish",
        "changes":{"NW_original_phases":[1,2,8]},"unchanged_other_direction_frames":56,"unchanged_other_NW_frames":[3,4,5,6,7],
        "direction_phase_policy":"RIGHT contact first; full 8-frame cyclic rotation by 4 of N/SW/W/NW only; no contact-only swaps",
        "phase_plan":str(SOURCE/"phase-plan.json"),"phase_shift":PHASE_SHIFT,
        "NW_fix_original_to_canonical_phase":{"01":5,"02":6,"08":4},
        "scale_policy":"whole raw-cell normalization only; one common profile for all 72 final poses; no per-frame/body bbox fit",
        "original_directories_read_only":True})
    directions={};inventory={};all_records=[]
    for direction in DIRECTIONS:
        sheet=Image.new("RGBA",(1772,886),(255,0,255,255));records=[]
        for index,pose in enumerate(config[direction]):
            path=Path(pose["source"]);h=sha(path);inventory[str(path)]=h
            image=Image.open(path).convert("RGBA");cw,ch=image.width//pose["cols"],image.height//pose["rows"]
            i=pose["index"];box=(i%pose["cols"]*cw,i//pose["cols"]*ch,(i%pose["cols"]+1)*cw,(i//pose["cols"]+1)*ch)
            frame=image.crop(box);factor=min(CELL/cw,CELL/ch);size=(round(cw*factor),round(ch*factor))
            frame=frame.resize(size,Image.Resampling.LANCZOS)
            normalized=Image.new("RGBA",(CELL,CELL),(255,0,255,255));normalized.paste(frame,((CELL-size[0])//2,(CELL-size[1])//2))
            original_phase=pose["original_phase"]
            if direction in EXPECTED_FINAL:
                original_cell=Image.open(ORIGINAL/"source"/f"walk-{direction}-final.png").convert("RGBA").crop(cellbox(original_phase-1))
                if normalized.tobytes()!=original_cell.tobytes():raise ValueError(f"Changed completed source pixel {direction} original {original_phase}")
            elif original_phase not in EXPECTED_FIX:
                original_cell=Image.open(nw).convert("RGBA").crop(cellbox(original_phase-1))
                if normalized.tobytes()!=original_cell.tobytes():raise ValueError(f"Changed untouched NW original {original_phase}")
            output_box=cellbox(index);sheet.paste(normalized,output_box[:2])
            rec={**pose,"direction":direction,"phase":index+1,"source_path":str(path),"source_sha256":h,
                 "source_native_size":list(image.size),"source_crop":list(box),"uniform_whole_cell_scale":factor,
                 "normalized_cell_size":[CELL,CELL],"output_cell_box":list(output_box),"output_cell_rgba_sha256":pixelsha(normalized),
                 "per_subject_fit":False,"mirrored":False,"phase_rotation":PHASE_SHIFT[direction],"canonical_anatomical_phase":CANONICAL[index]}
            records.append(rec);all_records.append(rec)
        path=SOURCE/f"walk-{direction}-final.png"
        if direction in EXPECTED_FINAL and PHASE_SHIFT[direction]==0:
            copy(ORIGINAL/"source"/path.name,path) # no phase shift: original PNG byte-identical
        else:
            sheet.save(path) # entire source-cell pixels verified above; only cyclic positions changed
        checkpixel=Image.open(path).convert("RGBA")
        if checkpixel.tobytes()!=sheet.tobytes():raise ValueError("Saved direction pixels changed")
        assembly={"version":12,"operation":"whole authored cells; NW original near-arm fixes 01/02/08 only; other 61 walk cells preserved; canonical RIGHT-first full-cycle shifts",
                  "output_path":str(path),"output_sha256":sha(path),"output_size":[1772,886],"output_grid":[4,2],
                  "direction":direction,"sources":records,"new_poses_generated_by_script":False,
                  "mirroring":False,"interpolation_or_duplicate_pose":False,"per_subject_fit":False}
        if direction in EXPECTED_FINAL:
            assembly["original_assembly_snapshot"]=str(prov/f"walk-{direction}-final.original.assembly.json")
            assembly["original_completed_direction_png_byte_identical"]=(PHASE_SHIFT[direction]==0)
            assembly["all_eight_source_cell_pixels_identical_before_reordering"]=True
        assembly["phase_rotation"]=PHASE_SHIFT[direction]
        assembly["original_phases_in_new_order"]=[p["original_phase"] for p in config[direction]]
        write(path.with_suffix(".assembly.json"),assembly)
        directions[direction]=(sheet,path,assembly)
    paired={}
    for kind,ds in PAIRS.items():
        canvas=Image.new("RGBA",(1772,1772),(255,0,255,255));records=[]
        for k,d in enumerate(ds):
            image,path,a=directions[d]
            for i in range(8):
                srcbox=cellbox(i);outbox=cellbox(k*8+i);cell=image.crop(srcbox);canvas.paste(cell,outbox[:2])
                records.append({"direction":d,"phase":i+1,"source_path":str(path),"source_sha256":sha(path),
                                "source_crop_box":list(srcbox),"output_cell_box":list(outbox),
                                "source_crop_rgba_sha256":pixelsha(cell),"whole_cell_scale":1.0})
        path=SOURCE/f"{kind}.png";canvas.save(path)
        write(path.with_suffix(".assembly.json"),{"version":12,"operation":"pair two independently authored direction sheets by exact whole cells",
              "output_path":str(path),"output_sha256":sha(path),"output_size":[1772,1772],"output_grid":[4,4],
              "direction_order":list(ds),"sources":[{"path":str(directions[d][1]),"sha256":sha(directions[d][1]),
              "upstream_assembly_path":str(directions[d][1].with_suffix(".assembly.json"))} for d in ds],
              "frames":records,"new_poses_generated_by_script":False,"per_frame_body_fit":False,"mirrored_frames":False,"interpolation":False})
        paired[kind]={"path":str(path),"sha256":sha(path),"grid":[4,4],"direction_order":list(ds)}
    for name in ("idle.png","portrait-daoist.png"):
        src=ORIGINAL/"source"/name;copy(src,SOURCE/name);inventory[str(src)]=sha(src)
    idle=SOURCE/"idle.png"
    write(idle.with_suffix(".assembly.json"),{"version":12,"operation":"unchanged original authored 8-direction idle copied byte-for-byte",
         "output_path":str(idle),"output_sha256":sha(idle),"output_size":list(Image.open(idle).size),"output_grid":[4,2],
         "direction_order":list(DIRECTIONS),"source_path":str(ORIGINAL/"source"/"idle.png"),"source_sha256":sha(ORIGINAL/"source"/"idle.png"),
         "new_poses_generated_by_script":False,"per_subject_fit":False})
    paired["idle"]={"path":str(idle),"sha256":sha(idle),"grid":[4,2],"direction_order":list(DIRECTIONS)}
    for p,h in preserved_originals.items():check(p,h)
    write(SOURCE/"source-inventory-sha256.json",[{"path":p,"sha256":h} for p,h in sorted(inventory.items())])
    write(SOURCE/"cell-source-map.json",all_records)
    write(SOURCE/"candidate-sources.json",{"character_id":ROOT.name,"sources":paired,
         "portrait_raw":{"path":str(SOURCE/"portrait-daoist.png"),"sha256":sha(SOURCE/"portrait-daoist.png")},
         "checks":{"unchanged_completed_frames":56,"unchanged_NW_frames":5,"new_arm_only_edits":3,
         "unique_authored_walk_frames":64,"independent_idle_frames":8,"original_files_verified_unchanged":True},
         "phase_policy":"RIGHT contact first; complete-cycle shift 4 for N/SW/W/NW, other directions unchanged", "phase_plan":str(SOURCE/"phase-plan.json")})
    print(json.dumps({"status":"assembled","root":str(ROOT),"unchanged_56_frames":True,"unchanged_5_NW_frames":True,"NW_original_arm_fixes":[1,2,8],"canonical_shifts":PHASE_SHIFT,"sources":paired},ensure_ascii=False))

if __name__=="__main__":main()

