"""Publish the reviewed v10 asset set. Default: reviewable dry run; --apply copies exact approved bytes."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, os, subprocess
from PIL import Image
from validate_staged import PACK, REPO, read, sha, safe

STAGE=PACK/"staged"
ATTR="designs/attribute-panels/v2-painted/unity-slices"
V5="qdao_ui_redesign_v5"
ATOMIC="q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic"
MANIFESTS=[V5+"/components/manifest.json","exact_qdao_slices/manifest_native_q5.json",
    ATOMIC+"/manifest_native_q5.json",ATOMIC+"/manifest_redrawn.json",ATOMIC+"/manifest_ai_qstyle_badges.json",
    "q_daoist_login_ui_uncropped_highres_final_layers/manifest_native_q5.json",V5+"/hud/placement.json",
    ATTR+"/manifest.json",ATTR+"/file-validation.json",V5+"/manifest.json"]
EXTRA_SVGS=["q_daoist_login_ui_uncropped_highres_final_layers/native_q5/"+n+".svg" for n in ["base","controls","labels"]]+[V5+"/hud/"+n+".svg" for n in ["hud_skin","hud_overlay","hud_labels"]]
REVIEWS=[ATTR+"/"+n+".png" for n in ["sprite-overview","nine-slice-review","frame-fields-review","fixed-glyph-title-review","character-layout-review","pet-layout-review"]]
def stamp(): return datetime.now(timezone.utc).isoformat()
def write_json(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
def git(*args,check=True):
    return subprocess.run(["git",*args],cwd=REPO,capture_output=True,check=check)
def require(condition,message):
    if not condition: raise ValueError(message)
def verify(path,digest):
    require(path.is_file() and sha(path)==digest,"Evidence changed: "+str(path))
def prepare_exports():
    manifest=read(REPO/V5/"manifest.json")
    paths=[]
    for stem,source in [("04_main_city_hud",STAGE/V5/"source/04_main_city_hud.png"),
                        ("02_server_select",STAGE/"ugui_qdao_headband_2560x1080.png")]:
        raw=source.read_bytes()
        row=next(r for r in manifest["screens"] if r["id"]==stem)
        for kind,rel in [("source","source/"+stem+".png"),("export",stem+"_2560x1080.png")]:
            destination=safe(STAGE,V5+"/"+rel);destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(raw)
            with Image.open(destination) as im:
                row[kind]={"path":rel,"size":list(im.size),"mode":im.mode,"bytes":len(raw),"sha256":sha(destination)}
            paths.append(V5+"/"+rel)
        row.update(creation_method="v10_painted_components_native_label_composition",
            recipe="../qdao_ui_style_recut_v10/tools/build_composites.mjs",resampling="none; byte-for-byte copy",
            source_crop_box_xyxy=[0,0,2560,1080],relative_aspect_error=0,native_2560x1080_generation=False)
    manifest["ui_recut"]="../qdao_ui_style_recut_v10/publication.json";manifest["updated"]="2026-09-11"
    write_json(STAGE/V5/"manifest.json",manifest)
    return paths
def check_evidence():
    check=subprocess.run([os.sys.executable,str(PACK/"tools/validate_staged.py")],cwd=REPO,capture_output=True,text=True)
    require(check.returncode==0,check.stdout+check.stderr)
    validation=read(PACK/"validation.json")
    require(validation["asset_count"]==158 and validation["counts"]=={"changed_needs_visual_review":155,"allowed_unchanged":3},"Unexpected PNG coverage")
    common=read(STAGE/"common-legacy-visual-qa.json");other=read(STAGE/"attribute-composite-visual-qa.json")
    for report in [common,other]:require(report["status"]=="passed_for_staged_art_delivery","Visual review is not passed")
    expected={r["path"] for r in read(PACK/"contracts/current_files.json")["files"] if r["family"] in ["components","legacy"]}
    require({r["path"] for r in common["files"]}==expected,"Common QA coverage mismatch")
    for r in common["files"]:
        verify(safe(STAGE,r["path"]),r["sha256"]);verify(safe(STAGE,r["svg"]),r["svg_sha256"])
    for r in other["reviewImages"]:verify(safe(REPO,r["path"]),r["sha256"])
    verify(STAGE/ATTR/"file-validation.json",other["attributes"]["fileValidationSha256"])
    verify(PACK/"source-map.attributes.json",other["attributes"]["sourceMapSha256"])
    verify(STAGE/"composite_build_report.json",other["composites"]["buildReportSha256"])
    attrs=read(PACK/"source-map.attributes.json")
    for r in attrs["outputs"]:verify(safe(STAGE,r["path"]),r["outputSha256"])
    composites=read(STAGE/"composite_build_report.json")
    for r in composites["files"]:verify(safe(STAGE,r["path"]),r["sha256"])
    for r in composites["scene_sources"]:verify(safe(REPO,r["path"]),r["sha256"])
    for r in composites["component_sources"]:verify(safe(REPO,r["path"]),r["sha256"])
    verify(REPO/"docs/references/ui-style-20260910.png","913e301b1955a4dd78888bebcec82d1dbf504c0517ed606cc8eaab667675b825")
    for r in read(PACK/"generation-status.json")["successful_generations"]:verify(PACK/r["file"],r["sha256"])
    return validation,common

def payload(relative):
    raw=safe(STAGE,relative).read_bytes()
    if relative in MANIFESTS and relative!=ATTR+"/file-validation.json":
        value=json.loads(raw.decode("utf-8-sig"))
        for key in ("staged_only","stagedOnly"):
            if key in value:value[key]=False
        value["publication_record"]="qdao_ui_style_recut_v10/publication.json (repository relative)"
        raw=(json.dumps(value,ensure_ascii=False,indent=2)+"\n").encode("utf-8")
    return raw

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    validation,common=check_evidence()
    aliases=prepare_exports()
    baseline={r["path"]:r for r in read(PACK/"contracts/current_files.json")["files"]}
    relatives=set(baseline)|{r["svg"] for r in common["files"]}|set(EXTRA_SVGS+MANIFESTS+REVIEWS+aliases)
    revision=git("rev-parse","HEAD").stdout.decode().strip()
    existing=read(PACK/"publication.json") if (PACK/"publication.json").exists() else {}
    prior_rows={r["path"]:r for r in existing.get("files",[])}
    entries=[]; contents={}
    for rel in sorted(relatives):
        current=safe(REPO,rel);raw=payload(rel);digest=hashlib.sha256(raw).hexdigest()
        oldsha=sha(current) if current.is_file() else None
        if rel in baseline:
            require(oldsha in {baseline[rel]["sha256"],digest},"Production PNG changed since inventory: "+rel)
        prior=prior_rows.get(rel)
        if prior and oldsha==prior["published_sha256"]:
            before=prior["previous_sha256"];oid=prior.get("previous_git_oid");rev=prior.get("previous_revision")
        else:
            before=oldsha;rev=revision
            oid_result=git("rev-parse",revision+":"+rel,check=False)
            oid=oid_result.stdout.decode().strip() if oid_result.returncode==0 else None
            # Keep unrelated edits in all existing non-PNG paths.
            if current.exists() and oid:
                clean=git("diff","--quiet","HEAD","--",rel,check=False)
                require(clean.returncode==0,"Uncommitted production edit requires review: "+rel)
        entries.append({"path":rel,"kind":"contract_png" if rel in baseline else "supporting_asset",
            "staged_sha256":sha(safe(STAGE,rel)),"published_sha256":digest,"previous_sha256":before,
            "previous_git_oid":oid,"previous_revision":rev,"changed":before!=digest})
        contents[rel]=raw
    evidence={p.relative_to(PACK).as_posix():sha(p) for p in [PACK/"validation.json",STAGE/"common-legacy-visual-qa.json",STAGE/"attribute-composite-visual-qa.json"]}
    result={"schemaVersion":1,"status":"ready_to_publish","checked_at_utc":stamp(),"before_revision":revision,
        "contract_png_count":158,"changed_png_pixels":155,"retained_text_layers":3,
        "supporting_file_count":len(entries)-158,"total_files":len(entries),"visual_review":"passed",
        "evidence":evidence,"rollback":"For a previously existing file, restore its previous_revision:path from Git; previous_git_oid identifies the exact original blob. New review files have no previous blob. No directories were removed.",
        "limits":["Art repository publication only; no new Unity/FairyGUI import or gameplay integration.","Historical full-screen source paintings and older interactive demos remain archived; standard server/HUD exports are updated."],
        "files":entries}
    write_json(PACK/"publication-plan.json",result)
    if args.apply:
        # All inputs have passed; recheck every target before the first write.
        for r in entries:
            current=safe(REPO,r["path"])
            expected={r["previous_sha256"],r["published_sha256"]}
            require((sha(current) if current.exists() else None) in expected,"Target changed during planning: "+r["path"])
        for r in entries:
            target=safe(REPO,r["path"]);target.parent.mkdir(parents=True,exist_ok=True)
            temp=target.with_name(target.name+".v10-publish-tmp")
            require(not temp.exists(),"Existing interrupted temporary file: "+str(temp))
            temp.write_bytes(contents[r["path"]]);os.replace(temp,target)
        for r in entries:verify(safe(REPO,r["path"]),r["published_sha256"])
        result.update(status="published_and_verified",published_at_utc=stamp(),verified_file_count=len(entries))
        write_json(PACK/"publication.json",result)
        print(json.dumps({k:result[k] for k in ["status","contract_png_count","changed_png_pixels","retained_text_layers","total_files","verified_file_count"]}))
    else: print(json.dumps({k:result[k] for k in ["status","contract_png_count","total_files","supporting_file_count"]}))
if __name__=="__main__":main()
