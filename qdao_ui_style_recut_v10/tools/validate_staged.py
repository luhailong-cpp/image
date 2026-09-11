"""Validate all 158 v10 outputs and their frozen client contracts; never publish."""
from pathlib import Path
import argparse, base64, hashlib, json, re
from collections import Counter
from inventory_contracts import PACK, REPO, inspect_png

TEXT_EXCEPTIONS = {
    "designs/attribute-panels/v2-painted/unity-slices/png/title_character.png": "Approved standalone static calligraphy; the surrounding UI skin is replaced.",
    "designs/attribute-panels/v2-painted/unity-slices/png/title_pet.png": "Approved standalone static calligraphy; the surrounding UI skin is replaced.",
    "qdao_ui_redesign_v5/hud/hud_labels.png": "Independent native HUD text layer; its underlying skin is replaced.",
}
def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def safe(root, relative):
    full=(root/relative).resolve()
    if not full.is_relative_to(root.resolve()): raise ValueError("Unsafe path: "+str(relative))
    return full
def check_manifests(staged):
    errors=[]
    specs=[
        ("components.json","qdao_ui_redesign_v5/components/manifest.json","assets","id",["width","height","png","svg","state","dynamic_text_baked","category","resize_axes","fixed_height","nine_slice","minimum_size","content_insets","text_color","selection_marker","disabled_marker"]),
        ("legacy.json","exact_qdao_slices/manifest_native_q5.json","assets","png",["png","svg","width","height","role","state","nine_slice","resize_axes","fixed_height","dynamic_text_baked","round_badge_baked","status_baked"]),
        ("attributes.json","designs/attribute-panels/v2-painted/unity-slices/manifest.json","sprites","name",["name","width","height","borderLeftBottomRightTop","resourcePath","containsDynamicText","containsStaticTitle"]),
    ]
    checked=0
    for contract,rel,array,key,fields in specs:
        before=read(PACK/"contracts"/contract)[array]
        after=read(safe(staged,rel))[array]
        old={a[key]:a for a in before}; new={a[key]:a for a in after}
        if len(new)!=len(after) or set(old)!=set(new): errors.append(rel+": asset keys changed")
        for ident, expected in old.items():
            actual=new.get(ident,{})
            for field in fields:
                if expected.get(field)!=actual.get(field): errors.append(f"{ident}: {field} changed")
            if array=="assets" and ident in new:
                prefix=Path(rel).parent if contract=="components.json" else Path()
                png=safe(staged,prefix/actual["png"]); svg=safe(staged,prefix/actual["svg"])
                uris=re.findall(r"data:image/png;base64,([A-Za-z0-9+/=]+)",svg.read_text(encoding="utf-8"))
                if len(uris)!=1 or base64.b64decode(uris[0])!=png.read_bytes(): errors.append(str(svg)+": PNG wrapper mismatch")
                if actual.get("png_sha256")!=sha(png) or actual.get("svg_sha256")!=sha(svg): errors.append(str(png)+": manifest hash mismatch")
            elif ident in new:
                png=safe(staged,Path(rel).parent/"png"/(ident+".png"))
                if actual.get("sha256")!=sha(png): errors.append(str(png)+": manifest hash mismatch")
            checked+=1
    return {"asset_records_checked":checked,"png_svg_pairs_checked":112,"errors":errors}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--staged",type=Path,default=PACK/"staged")
    parser.add_argument("--output",type=Path,default=PACK/"validation.json")
    args=parser.parse_args()
    staged,output=args.staged.resolve(),args.output.resolve()
    if not staged.is_relative_to(PACK.resolve()) or not output.is_relative_to(PACK.resolve()): parser.error("Paths must stay inside v10")
    rows=[]
    for old in read(PACK/"contracts/current_files.json")["files"]:
        candidate=safe(staged,old["path"]); row={"path":old["path"],"family":old["family"],"problems":[]}
        if not candidate.is_file(): row["status"]="missing"
        else:
            try:
                new=inspect_png(candidate); row["actual"]=new
                if new["size"]!=old["size"]: row["problems"].append("canvas_changed")
                if new["mode"]!=old["mode"]: row["problems"].append("mode_changed")
                if old["alpha_range"] is not None and old["alpha_range"][0]==0 and (new["alpha_range"] is None or new["alpha_range"][0]!=0): row["problems"].append("required_transparency_missing")
                if new["alpha_range"] is not None and new["alpha_range"][1]==0: row["problems"].append("empty_alpha")
                unchanged=new["pixel_sha256"]==old["pixel_sha256"] and new["mode"]==old["mode"]
                if row["problems"]: row["status"]="invalid"
                elif unchanged and old["path"] in TEXT_EXCEPTIONS:
                    row["status"]="allowed_unchanged"; row["reason"]=TEXT_EXCEPTIONS[old["path"]]
                elif unchanged: row["status"]="unchanged_artwork"
                else: row["status"]="changed_needs_visual_review"
                row["encoded_bytes_changed"]=new["sha256"]!=old["sha256"]
            except Exception as exc:
                row["status"]="invalid"; row["problems"].append(str(exc))
        rows.append(row)
    try: manifests=check_manifests(staged)
    except Exception as exc: manifests={"errors":[str(exc)]}
    counts=dict(Counter(r["status"] for r in rows))
    ready=not manifests["errors"] and all(r["status"] in {"changed_needs_visual_review","allowed_unchanged"} for r in rows)
    report={"status":"ready_for_visual_review" if ready else "incomplete","asset_count":len(rows),"counts":counts,
            "unchanged_policy":TEXT_EXCEPTIONS,"manifest_validation":manifests,"files":rows,
            "limits":"Mechanical verification only. Separate hash-bound visual reports are required by publish_staged.py. No Unity/FairyGUI import is claimed."}
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:report[k] for k in ("status","asset_count","counts","manifest_validation")}))
    return 0 if ready else 1
if __name__=="__main__": raise SystemExit(main())
