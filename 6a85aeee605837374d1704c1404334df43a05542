from pathlib import Path
import json,hashlib
from PIL import Image
root=Path(__file__).resolve().parents[1]
p=root/"generation-status.json"
d=json.loads(p.read_text(encoding="utf-8-sig"))
records=[]
for f in sorted((root/"source").glob("0[1-6]-*.png")):
    with Image.open(f) as im: size=list(im.size)
    prompt=f.with_suffix(".prompt.txt")
    records.append({"file":f.relative_to(root).as_posix(),"prompt":prompt.relative_to(root).as_posix(),"native_size":size,"tool":"image_gen","reference_original":"docs/references/ui-style-20260910.png","reference_transport":"in-memory conversation JPEG; num_last_images_to_include=1","model_basis":"official built-in documentation: gpt-image-2","model_parameter_exposed":False,"quality_parameter_exposed":False,"sha256":hashlib.sha256(f.read_bytes()).hexdigest(),"prompt_sha256":hashlib.sha256(prompt.read_bytes()).hexdigest()})
d.update({"status":"in_progress_builtin","active_route":"builtin_image_gen","generated_images":len(records),"successful_generations":records,"quality_target":"highest visual quality; current tool exposes no quality parameter","next_step":"Continue remaining built-in artwork then recut, visually verify and publish the full UI contract set; no API key required."})
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"generated_images":len(records),"sources":[r["file"] for r in records]}))
