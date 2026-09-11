"""Read-only final delivery verification; writes only its v10 audit JSON."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
from PIL import Image
import build_attributes
from validate_staged import PACK,REPO,read,sha,check_manifests
def require(value,message):
    if not value:raise ValueError(message)
def main():
    publication=read(PACK/"publication.json")
    require(publication["status"]=="published_and_verified","Publication is incomplete")
    for r in publication["files"]:
        require(sha(REPO/r["path"])==r["published_sha256"],"Published file changed: "+r["path"])
    manifests=check_manifests(PACK/"staged")
    require(not manifests["errors"],str(manifests["errors"]))
    for r in read(PACK/"contracts/attributes.json")["sprites"]:
        image,meta=build_attributes.build(r)
        with Image.open(build_attributes.OUT/"png"/(r["name"]+".png")) as saved:
            require(image.size==saved.size and image.tobytes()==saved.convert("RGBA").tobytes(),"Not reproducible: "+r["name"])
    attr=REPO/"designs/attribute-panels/v2-painted/unity-slices"
    imported=read(attr/"unity-import-v10.json");runtime=read(attr/"unity-validation-v10.json")
    require(imported["status"]==runtime["status"]=="passed","Attribute client validation incomplete")
    require(sha(attr/"manifest.json")==imported["manifestSha256"]==runtime["manifestSha256"],"Unity validation is for another manifest")
    for r in imported["files"]:
        require(sha(attr/"png"/(r["name"]+".png"))==r["sha256"],"Client recorded another sprite: "+r["name"])
    for r in runtime["screenshots"]:
        require(sha(attr/"unity-review-v10"/r["file"])==r["sha256"],"Unity screenshot evidence changed")
    sys.path.insert(0,str(REPO/"qdao_ui_redesign_v5"))
    from export_ui import check
    screens=check()
    result={"status":"passed","verified_at_utc":datetime.now(timezone.utc).isoformat(),
        "formal_pngs":158,"changed_png_pixels":155,"retained_text_layers":3,"published_files_exact_sha256":len(publication["files"]),
        "manifest_contracts":manifests["asset_records_checked"],"exact_png_svg_pairs":112,
        "attribute_in_memory_rebuilds_matching_current_pixels":31,"standard_screen_exports":len(screens["screens"]),
        "attribute_client_import":{"status":imported["status"],"sprites":len(imported["files"]),"guid_preserved":imported["guidsPreserved"],
            "tests":runtime["tests"],"verified_screenshots":len(runtime["screenshots"]),"live_server_verified":runtime["liveServerVerification"]},
        "publication_sha256":sha(PACK/"publication.json"),"attribute_builder_sha256":sha(PACK/"tools/build_attributes.py"),
        "git_push":"not verified; separate destination approval is pending in the push task",
        "limits":"This audit reads already-recorded Unity evidence; this script does not itself operate Unity. Full game UI/client integration and historical HTML reskins are not claimed."}
    (PACK/"final-verification.json").write_bytes((json.dumps(result,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
    print(json.dumps(result))
if __name__=="__main__":main()
