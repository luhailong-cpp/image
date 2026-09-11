"""Refresh actual native source and verified publication status; no image/API calls."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
from PIL import Image
root=Path(__file__).resolve().parents[1]; repo=root.parent
p=root/"generation-status.json"
d=json.loads(p.read_text(encoding="utf-8-sig"));records=[]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for f in sorted((root/"source").glob("0[1-6]-*.png")):
    with Image.open(f) as im:size=list(im.size)
    prompt=f.with_suffix(".prompt.txt")
    records.append({"file":f.relative_to(root).as_posix(),"prompt":prompt.relative_to(root).as_posix(),"native_size":size,
        "tool":"image_gen","reference_original":"docs/references/ui-style-20260910.png",
        "reference_transport":"in-memory conversation JPEG; num_last_images_to_include=1",
        "model_basis":"official built-in documentation: gpt-image-2","model_parameter_exposed":False,
        "quality_parameter_exposed":False,"sha256":sha(f),"prompt_sha256":sha(prompt)})
d.update(active_route="builtin_image_gen",generated_images=len(records),successful_generations=records,
    quality_target="highest visual quality; current tool exposes no quality parameter",updated_at_utc=datetime.now(timezone.utc).isoformat())
publication=root/"publication.json"
published=False
if publication.exists():
    result=json.loads(publication.read_text(encoding="utf-8"))
    published=result["status"]=="published_and_verified" and all((repo/r["path"]).is_file() and sha(repo/r["path"])==r["published_sha256"] for r in result["files"])
if published:
    d.update(status="artwork_and_slices_published",published_production_pngs=158,replaced_production_assets=155,
        retained_text_layers=3,verified_delivery_files=result["total_files"],publication_record="publication.json",
        next_step="Art and recutting are complete. Git delivery is tracked separately; use publication.json for exact verified asset paths.",
        client_attribute_validation="designs/attribute-panels/v2-painted/unity-slices/unity-validation-v10.json")
else:
    d.update(status="in_progress_builtin" if len(records)<6 else "artwork_ready_publication_unverified",
        next_step="Review staging and current production hashes before publishing. No API key is required.")
p.write_bytes((json.dumps(d,ensure_ascii=False,indent=2)+"\n").encode("utf-8"))
print(json.dumps({"status":d["status"],"generated_images":len(records),"published_production_pngs":d.get("published_production_pngs",0)}))
