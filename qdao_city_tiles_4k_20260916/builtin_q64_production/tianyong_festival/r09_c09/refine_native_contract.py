from pathlib import Path
import json,hashlib,shutil
P=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
backup=P/'plan.before-single-reference-20260920.json';assert not backup.exists();shutil.copyfile(P/'plan.json',backup)
plan=json.loads((P/'plan.json').read_text())
for i,p in enumerate(plan['patches']):
 if i<3:continue
 if i==3:
  p['selectedNativeStem']='r01_c04.v2';p['promptFile']='prompts/r01_c04.v2.prompt.txt'
 p['submittedImages']=[p['guide']]
 prompt=f'Repaint this exact square terrain crop into crisp native-resolution premium hand-painted Chinese fantasy Q/chibi game art. This is detail {p["id"]} of an ivory-stone platform. Preserve the exact crop, scale, camera, positions, every curve, slab joint, step count and ornamental relief outline shown. Develop sharp native rounded bevels, restrained warm cream mineral shading, sculpted edge highlights and tidy soft shadows. Keep every blank stone panel blank. Do not add any cloud motif, angular ornament, seam, block, carving or other feature that is not already visible in THIS crop. One fully opaque continuous terrain crop with precisely aligned edges, especially the 115-pixel outer overlap, no writing, grid, collage, frame, watermark, characters, blur or transparency.'
 if p['column']==0:prompt+=' The left 230-pixel reference strip is existing neighboring art; unite its tone into the main crop while retaining continuous exact geometry, removing any pasted-strip boundary.'
 if p['row']==3:prompt+=' The bottom 230-pixel reference strip is existing neighboring art; unite its tone into the main crop while retaining continuous exact geometry, removing any pasted-strip boundary.'
 (P/p['promptFile']).write_text(prompt,encoding='utf-8')
(P/'plan.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
(P/'qa/r01_c04-rejection.json').write_text(json.dumps({'status':'rejected_retained','native':'native/r01_c04.png','sha256':sha(P/'native/r01_c04.png'),'reason':'Model transferred cloud and angular ornaments from full layout into blank stone panels. Need single local reference; original and record preserved.','replacementStem':'r01_c04.v2'},indent=2),encoding='utf-8')
f=P/'assemble_builtin.py';code=f.read_text(encoding='utf-8');code=code.replace('native = ROOT / "native" / f"{tile_id}.png"','selected = next(p for p in read_json(ROOT / "plan.json")["patches"] if p["id"] == tile_id)\n            stem = selected.get("selectedNativeStem", tile_id)\n            native = ROOT / "native" / f"{stem}.png"').replace('record_path = ROOT / "native" / f"{tile_id}.record.json"','record_path = ROOT / "native" / f"{stem}.record.json"').replace('prompt = ROOT / "prompts" / f"{tile_id}.prompt.txt"','prompt = ROOT / selected["promptFile"]')
code=code.replace('if len(references) != 2 or record["toolCall"]["referenced_image_paths"] != [r["path"] for r in references]:','if not references or record["toolCall"]["referenced_image_paths"] != selected["submittedImages"] or [r["path"] for r in references] != selected["submittedImages"]:')
f.write_text(code,encoding='utf-8');print('Original first three reference contracts retained; rejected fourth preserved; remaining crops use one exact local reference.')
