#!/usr/bin/env python3
"""Publish accepted Qdao artwork into Unity without changing existing .meta files.

All image conversion happens in this image-project folder. --sync copies only
planned PNGs and creates metadata only for new files. --check never edits Unity.
Unknown runtime art is explicitly inventoried and preserved rather than guessed.
"""
from __future__ import annotations
import argparse, hashlib, json, re, shutil, sys, uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent
IMAGE = ROOT.parent
CLIENT_DEFAULT = IMAGE.parent / "mmorpg-client"
COMPONENTS = IMAGE / "qdao_ui_redesign_v5/components"
STAGE = ROOT / "prepared"
BASELINE = ROOT / "baseline.json"
REPORT = ROOT / "assets_manifest.json"
BORDER_NAMESPACE = uuid.UUID("f612da11-890e-4812-a21f-c1f762a50f4b")
LANCZOS = Image.Resampling.LANCZOS

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def json_read(path): return json.loads(path.read_text(encoding="utf-8-sig"))
def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
def inside(path, root):
    result = path.resolve()
    if not result.is_relative_to(root.resolve()): raise ValueError(f"Path escapes root: {result}")
    return result
def pngs(root):
    return sorted(p for p in root.rglob("*.png") if not any("backup" in q.lower() for q in p.relative_to(root).parts))
def image_info(path):
    with Image.open(path) as im:
        im.load()
        return {"size": list(im.size), "mode": im.mode,
                "alpha_range": list(im.getchannel("A").getextrema()) if "A" in im.getbands() else None}
def nine_slice(im, size, edges):
    w,h=size; sw,sh=im.size
    l,t,r,b=(edges.get(k,0) for k in ("left","top","right","bottom"))
    if w <= l+r or h <= t+b: raise ValueError(f"Target too small for borders: {size}")
    out=Image.new("RGBA",size)
    xs=[0,l,sw-r,sw]; ys=[0,t,sh-b,sh]
    dx=[0,l,w-r,w]; dy=[0,t,h-b,h]
    for row in range(3):
        for col in range(3):
            box=(xs[col],ys[row],xs[col+1],ys[row+1])
            tw,th=dx[col+1]-dx[col],dy[row+1]-dy[row]
            if tw and th and box[2]>box[0] and box[3]>box[1]:
                tile=im.crop(box).resize((tw,th),LANCZOS)
                out.alpha_composite(tile,(dx[col],dy[row]))
    return out

def build_plans(resources):
    components=json_read(COMPONENTS/"manifest.json")["assets"]
    by_id={a["id"]:a for a in components}
    plans={}
    def add(source,target,reason,category,component=None,size=None,read_only=False):
        source=inside(IMAGE/source,IMAGE)
        target=Path(target).as_posix()
        inside(resources/target,resources)
        if not source.is_file(): raise FileNotFoundError(source)
        if size is None and (resources/target).exists(): size=image_info(resources/target)["size"]
        plans[target]={"source":source,"target":target,"reason":reason,"category":category,
                       "component":component,"size":size,"read_only":read_only}
    def comp(cid,target,reason="Accepted v7 image-generated control, dynamic labels remain native."):
        a=by_id[cid]
        add("qdao_ui_redesign_v5/components/"+a["png"],target,reason,"ui_control",a)
    prefix="UI/Ugui/RefreshV8/"
    for a in components: comp(a["id"],prefix+a["id"]+".png")
    extras={
        "hero":"qdao_chibi_game_pack_v4/hero-transparent_1024.png",
        "companion_fox":"qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png",
        "sanctuary_background":"qdao_chibi_game_pack_v4/main-city_2560x1080.png",
        "battle_background":"qdao_ui_redesign_v5/05_battle_scene_2560x1080.png",
        "battle_loading":"qdao_ui_redesign_v5/06_battle_entry_loading_2560x1080.png",
        "battle_clouds":"qdao_ui_redesign_v5/06_battle_entry_clouds_fg_2560x1080.png",
        "companion_hu_tuan_tuan":"qdao_chibi_pets_v1/01_hu_tuan_tuan-transparent_1254.png",
        "companion_fu_xiao_hu":"qdao_chibi_pets_v1/02_fu_xiao_hu-transparent_1254.png",
        "companion_yun_jiu_jiu":"qdao_chibi_pets_v1/03_yun_jiu_jiu-transparent_1254.png",
    }
    for name,source in extras.items():
        add(source,prefix+name+".png","Accepted independent artwork; scenes have no baked interactive labels, actors/pets are static RGBA assets.","scene_or_actor")
    # Optional new art can be prepared by the root task under this image directory.
    for name in ("title_logo","login_background"):
        source=ROOT/"additional"/(name+".png")
        if source.is_file(): add(source.relative_to(IMAGE),prefix+name+".png","Additional clean production asset authored in image project.","additional_art")
    icons=json_read(IMAGE/"qdao_asset_refresh_v6/icons/manifest.json")["assets"]
    if len(icons)!=124: raise ValueError("Expected 124 item icons")
    for asset in icons:
        add(asset["path"],"UI/qdao_v3/icons_weapon/"+Path(asset["path"]).name,
            "Retain existing icon resource ID and canvas; update paint from final image-project asset. Published library; no literal client loader for this root was found.","item_library")
    for source in sorted((IMAGE/"q_daoist_character_pack_4096").glob("*_transparent_4096.png")):
        if not re.match(r"^(0[1-9]|1[0-9]|2[0-2])_",source.name): continue
        name=source.name.replace("_transparent_4096.png","_v3.png")
        add(source.relative_to(IMAGE),"UI/qdao_v3/characters/"+name,
            "Existing BattleArtCatalog.PortraitsRoot consumes these portrait IDs; preserve runtime canvas and GUID.","profession_portrait")
    aliases={
        "tab_button_green_active_v3":"tab_selected","list_row_idle_v3":"list_row_normal",
        "list_row_active_v3":"list_row_selected","server_card_wide_idle_v3":"server_card_wide_normal",
        "server_card_wide_active_v3":"server_card_wide_selected","server_card_med_idle_v3":"server_card_medium_normal",
        "server_card_med_active_v3":"server_card_medium_selected","bottom_bar_v3":"summary_bar",
        "search_box_with_icon_v3":"search_normal","ornament_gold_flower_v3":"gold_flower"}
    for dst,cid in aliases.items(): comp(cid,"UI/qdao_v3/ui/"+dst+".png")
    atom="q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/"
    for name,dst in [("status_red_dot.png","status_red_dot_v3.png"),("ai_qstyle_badges_sheet_chroma.png","badges_chroma_sheet_v3.png")]:
        add(atom+name,"UI/qdao_v3/ui/"+dst,"Preserve existing alias/atlas canvas using its final v7 replacement.","legacy_ui")
    exact={"bottom_bar_exact":"fx_bottom_bar","category_active_exact":"fx_left_row_active",
           "search_box":"fx_search_box","top_tab_active_exact":"fx_top_tab_active",
           "top_tab_idle_mid_exact":"fx_top_tab_idle_mid","top_tab_idle_right_exact":"fx_top_tab_idle_right"}
    for i in range(8): exact[f"server_card_{i}_exact"]=f"fx_server_card_{i}"
    for dst,src in exact.items():
        add("exact_qdao_slices/"+src+".png","UI/Ugui/Native/"+dst+".png",
            "Exact existing filename/canvas contract maps to final v7 legacy slice.","legacy_ui")
    native_atoms={"bottom_bar":"bottom_bar_bg_green_white","list_idle":"list_bg_unselected",
                  "list_selected":"list_bg_selected_green","server_card_idle":"server_card_bg_wide",
                  "server_card_selected":"server_card_bg_wide_selected_green","status_dot":"status_red_dot",
                  "tab_selected":"top_button_green_selected"}
    for dst,src in native_atoms.items():
        add(atom+src+".png","UI/Ugui/Native/"+dst+".png","Exact existing canvas maps to final v7 atomic control.","legacy_ui")
    for dst,cid in {"credential_btn_cancel":"list_row_normal","credential_btn_submit":"primary_button_normal",
                    "credential_panel_v2":"content_panel","window_frame_headband_clean":"main_frame"}.items():
        comp(cid,"UI/Ugui/Native/"+dst+".png")
    scene_targets={
        "UI/Ugui/Native/scene_background.png":"qdao_chibi_game_pack_v4/main-city_2560x1080.png",
        "UI/Ugui/Native/screen_art_headband.png":"qdao_ui_redesign_v5/02_server_select_2560x1080.png",
        "World/Tianyong/Backgrounds/tianyong_city_main_64x27_v1.png":"qdao_chibi_game_pack_v4/main-city_2560x1080.png",
        "UI/Ugui/Battle/Backgrounds/qdao_battle_arena_cloud_terrace_2560x1080_v1.png":"qdao_ui_redesign_v5/05_battle_scene_2560x1080.png",
        "UI/Ugui/Battle/Backgrounds/qdao_battle_entry_loading_2560x1080_v1.png":"qdao_ui_redesign_v5/06_battle_entry_loading_2560x1080.png",
        "UI/Ugui/Battle/Overlays/qdao_battle_entry_clouds_fg_2560x1080_v1.png":"qdao_ui_redesign_v5/06_battle_entry_clouds_fg_2560x1080.png"}
    for target,source in scene_targets.items():
        add(source,target,"Existing scene/transition alias; latest accepted image-project source. screen_art remains a reference-only image with baked labels.","scene_alias")
    for tile in json_read(IMAGE/"tianyong_city_6x6/tile_manifest.json")["tiles"]:
        add("tianyong_city_6x6/"+tile["file"],tile["resourcesPath"]+".png",
            "2026-09-08 image archive was copied byte-for-byte from the active client map. Verify identical bytes; do not redraw or replace a newer client tile.","city_tile",read_only=True)
    return plans,by_id

def preserved_reason(rel):
    if rel.startswith("World/Characters/"):
        return "Active 8-direction x 8-frame 4096x512 animation strips; image v7 has a different 4-frame contract and must not replace these."
    if rel.startswith("Battle/Characters/") or rel.startswith("Battle/Monsters/"):
        return "Active action animation strip; no approved equivalent action/anchor/frame contract in image UI pack. Preserve complete animation."
    if rel.startswith("Battle/Fx/") or "/Battle/Fx/" in rel:
        return "Active animated/transparent combat effect with a runtime frame/anchor contract; keep existing art until a matching animated replacement is authored."
    if rel.startswith("Battle/UI/") or rel.startswith("Battle/Buff/"):
        return "Runtime combat atlas/control retained; refresh root task skins runtime controls separately. Numeric atlases and effect-specific geometry must preserve their semantic mapping."
    if rel.startswith("World/Tianyong/Textures/"):
        return "Existing world material texture; active 6x6 painted map verified separately, no semantically equivalent replacement supplied."
    if rel.startswith("UI/Ugui/RefreshV8/"):
        return "Additional root-task asset already published in agreed RefreshV8 folder; retained without assuming provenance."
    return "Legacy resource kept for scene/prefab compatibility; new pages use explicit RefreshV8 independent controls. No guessed source substitution."

def metadata(resources,target,component):
    template=(resources/"UI/Ugui/Native/search_box.png.meta").read_text(encoding="utf-8-sig")
    guid=uuid.uuid5(BORDER_NAMESPACE,target).hex
    template=re.sub(r"(?m)^guid: .*$","guid: "+guid,template)
    # Unity may normalize the template to contain sub-sprite records. Never
    # transplant the template asset's local IDs, names or source rectangles.
    template=re.sub(r"(?ms)^  internalIDToNameTable:.*?(?=^  externalObjects:)", "  internalIDToNameTable: []\n", template)
    template=re.sub(r"(?ms)^    sprites:.*?(?=^    outline:)", "    sprites: []\n", template)
    template=re.sub(r"(?m)^    spriteID:.*$", "    spriteID: " + uuid.uuid5(BORDER_NAMESPACE,target+":sprite").hex, template)
    template=re.sub(r"(?m)^    nameFileIdTable:.*$", "    nameFileIdTable: {}", template)
    edges=(component or {}).get("nine_slice") or {}
    b=[edges.get(k,0) for k in ("left","bottom","right","top")]
    replacements={"enableMipMap":"0","sRGBTexture":"1","filterMode":"1","maxTextureSize":"4096",
                  "spriteMode":"1","spriteMeshType":"0","textureType":"8","alphaIsTransparency":"1","textureCompression":"0"}
    for key,value in replacements.items():
        template=re.sub(r"(?m)^(\s*"+key+r":) .*$",lambda m:m[1]+" "+value,template)
    template=re.sub(r"(?m)^(\s*spriteBorder:) .*$",lambda m:m[1]+f" {{x: {b[0]}, y: {b[1]}, z: {b[2]}, w: {b[3]}}}",template)
    return template

def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap=argparse.ArgumentParser()
    ap.add_argument("--client",type=Path,default=CLIENT_DEFAULT)
    mode=ap.add_mutually_exclusive_group()
    mode.add_argument("--sync",action="store_true")
    mode.add_argument("--check",action="store_true")
    args=ap.parse_args()
    client=args.client.resolve(); resources=client/"Assets/Resources"
    if not resources.is_dir(): raise FileNotFoundError(resources)
    plans,components=build_plans(resources)
    current=pngs(resources)
    if not BASELINE.exists():
        if args.check: raise FileNotFoundError("Run --sync or default preflight to freeze baseline first")
        write_json(BASELINE,{"client":client.as_posix(),"created":datetime.now(timezone.utc).isoformat(),"files":{
            p.relative_to(resources).as_posix():dict(sha256=sha(p),meta_sha256=sha(p.with_suffix(".png.meta")) if p.with_suffix(".png.meta").exists() else None,**image_info(p))
            for p in current}})
    baseline=json_read(BASELINE)
    if baseline["client"]!=client.as_posix(): raise ValueError("Baseline belongs to different client")
    records=[]; failures=[]; changes=0
    for rel,plan in plans.items():
        src=plan["source"]; dst=inside(resources/rel,resources)
        staged=inside(STAGE/rel,STAGE)
        src_info=image_info(src)
        if plan["read_only"]:
            if not dst.exists() or sha(dst)!=sha(src): failures.append("Map archival hash differs: "+rel)
            records.append(dict(target=rel,source=src.relative_to(IMAGE).as_posix(),source_sha256=sha(src),client_sha256=sha(dst) if dst.exists() else None,
                                status="preserved_hash_verified" if dst.exists() and sha(dst)==sha(src) else "map_diff_requires_review",
                                reason=plan["reason"],category=plan["category"],**src_info))
            continue
        size=tuple(plan["size"] or src_info["size"])
        staged.parent.mkdir(parents=True,exist_ok=True)
        if tuple(src_info["size"])==size:
            if not staged.exists() or sha(staged)!=sha(src): shutil.copyfile(src,staged)
            method="byte_copy"
        else:
            with Image.open(src) as im:
                im=im.convert("RGBA")
                edge=(plan["component"] or {}).get("nine_slice")
                if edge:
                    if plan["component"].get("resize_axes") == "horizontal" and im.height != size[1]:
                        ratio = size[1] / im.height
                        im = im.resize((round(im.width * ratio), size[1]), LANCZOS)
                        edge = {k: round(edge[k] * ratio) for k in ("left", "top", "right", "bottom")}
                        method = "proportional_height_then_horizontal_nine_slice"
                    else:
                        method = "manifest_nine_slice"
                    im = nine_slice(im, size, edge)
                else: im=im.resize(size,LANCZOS); method="LANCZOS_resample"
                im.save(staged,optimize=True)
        before=sha(dst) if dst.exists() else None
        desired=sha(staged)
        if args.sync:
            dst.parent.mkdir(parents=True,exist_ok=True)
            if before!=desired: shutil.copyfile(staged,dst); changes+=1
            meta=dst.with_suffix(".png.meta")
            if not meta.exists(): meta.write_text(metadata(resources,rel,plan["component"]),encoding="utf-8")
        after=sha(dst) if dst.exists() else None
        if args.check and after!=desired: failures.append("Unsynchronized PNG: "+rel)
        old=baseline["files"].get(rel)
        if old and old["meta_sha256"]:
            meta=dst.with_suffix(".png.meta")
            if not meta.exists() or sha(meta)!=old["meta_sha256"]: failures.append("Existing meta changed: "+rel)
        record=dict(target=rel,source=src.relative_to(IMAGE).as_posix(),source_sha256=sha(src),source_size=src_info["size"],
                    staged=staged.relative_to(ROOT).as_posix(),staged_sha256=desired,client_sha256=after,category=plan["category"],
                    method=method,reason=plan["reason"],status="synchronized" if after==desired else "pending_sync",
                    baseline_sha256=old["sha256"] if old else None,**image_info(staged))
        if plan["component"]:
            record["component_contract"]={k:plan["component"].get(k) for k in ("id","nine_slice","minimum_size","content_insets","resize_axes","fixed_height","text_color","dynamic_text_baked")}
        records.append(record)
    for p in pngs(resources):
        rel=p.relative_to(resources).as_posix()
        if rel in plans: continue
        old=baseline["files"].get(rel)
        meta=p.with_suffix(".png.meta")
        # Other agents may be implementing approved resources concurrently; record
        # current bytes without overwriting or treating those changes as rollback candidates.
        records.append(dict(target=rel,source=None,client_sha256=sha(p),baseline_sha256=old["sha256"] if old else None,
                            changed_by_other_work=bool(old and sha(p)!=old["sha256"]),status="preserved",
                            category="existing_runtime_art",reason=preserved_reason(rel),**image_info(p)))
    if len({r["target"] for r in records})!=len(records): failures.append("Duplicate destination")
    actual={p.relative_to(resources).as_posix() for p in pngs(resources)}
    recorded={r["target"] for r in records}
    if actual-recorded: failures.append("Unclassified client PNGs")
    for rel,old in baseline["files"].items():
        dst=resources/rel
        if not dst.exists(): failures.append("Baseline resource deleted: "+rel)
        meta=dst.with_suffix(".png.meta")
        if old["meta_sha256"] and (not meta.exists() or sha(meta)!=old["meta_sha256"]):
            failures.append("Baseline metadata changed: "+rel)
    for a in components.values():
        p=resources/"UI/Ugui/RefreshV8"/(a["id"]+".png")
        if p.exists():
            info=image_info(p)
            if info["size"]!=[a["width"],a["height"]] or info["alpha_range"] is None: failures.append("Invalid component canvas/alpha: "+a["id"])
            meta=p.with_suffix(".png.meta").read_text("utf8")
            edges=a.get("nine_slice") or {}
            b=[edges.get(k,0) for k in ("left","bottom","right","top")]
            expected=f"spriteBorder: {{x: {b[0]}, y: {b[1]}, z: {b[2]}, w: {b[3]}}}"
            if expected not in meta: failures.append("Sprite border mismatch: "+a["id"])
            if "textureType: 8" not in meta or "spriteMode: 1" not in meta: failures.append("Sprite import mismatch: "+a["id"])
    report={"schema":"qdao.client-art-sync.v1","generated_at":datetime.now(timezone.utc).isoformat(),
            "client":client.as_posix(),"image_root":IMAGE.as_posix(),"mode":"sync" if args.sync else "check" if args.check else "preflight",
            "status":"passed" if not failures and (args.sync or args.check) else "ready_for_sync" if not failures else "failed",
            "client_png_count":len(actual),"baseline_png_count":len(baseline["files"]),
            "mapped_assets":len(plans),"pngs_written_this_run":changes,"preserved_existing_meta":True,
            "category_counts":dict(Counter(r["category"] for r in records)),
            "method_counts":dict(Counter(r.get("method",r["status"]) for r in records)),
            "failures":sorted(set(failures)),
            "scope_notes":["Every current Resources PNG has a source mapping or a preservation reason.",
                           "124 item PNGs are published assets without a literal loader for UI/qdao_v3/icons_weapon found during static audit; they are not claimed visible on every page.",
                           "22 portraits are selected by BattleArtCatalog.PortraitsRoot.",
                           "Original image-project v5/v6 manifests contain historical hashes; current files and v7 provenance are authoritative for this sync.",
                           "This script never generates visual art, invokes paid APIs, edits client C#, deletes resources, or rewrites an existing meta file."],
            "records":sorted(records,key=lambda r:r["target"])}
    write_json(REPORT,report)
    write_json(ROOT/"refresh_components.json",{"resource_root":"UI/Ugui/RefreshV8","assets":list(components.values())})
    print(json.dumps({k:report[k] for k in ("status","client_png_count","baseline_png_count","mapped_assets","pngs_written_this_run","category_counts","failures")},ensure_ascii=False))
    return 1 if failures else 0
if __name__=="__main__": raise SystemExit(main())
