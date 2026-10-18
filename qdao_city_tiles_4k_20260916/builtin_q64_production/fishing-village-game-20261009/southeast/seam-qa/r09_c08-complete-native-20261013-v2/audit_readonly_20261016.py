from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
import numpy as np
from PIL import Image,ImageChops
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southeast");sys.path.insert(0,str(Z));from review_external_seams import Sources
Q=Z/"seam-qa"/"r09_c08-complete-native-20261013-v2";O=Q/"readonly-review-20261016-v1";O.mkdir(exist_ok=False)
def read(p):return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
m=read(Q/"manifest.json");all_e=[e for side in m["edges"] for e in side["segments"]]+m["intersections"]
S=Sources();records=[]
for e in all_e:
 if not e["sourceComplete"]:continue
 name=e["id"];isNE=name.startswith(("north-","east-")) or ("intersection" in name and not name.endswith("y36864"))
 root6=name in ["south-segment-1","south-segment-2","south-segment-3","intersection-x29696-y36864","intersection-x30720-y36864","intersection-x31744-y36864"]
 impactOnly=name in ["south-segment-4","intersection-x32768-y36864"]
 if not (isNE or root6 or impactOnly):continue
 qa=read(e["report"]);old=Image.open(e["image"]["file"]).convert("RGB");assert sha(e["image"]["file"])==e["image"]["sha256"]
 assembly=Image.new("RGB",old.size)
 for s in qa["sources"]:
  assert sha(s["file"])==s["sha256"];im=Image.open(s["file"]).convert("RGB")
  assembly.paste(im.crop(s["sourceCrop"]),tuple(s["destination"]))
 assert ImageChops.difference(assembly,old).getbbox() is None
 cur,pieces,missing=S.extract(e["globalBox"]);assert cur is not None and not missing
 delta=np.any(np.array(cur)!=np.array(old),axis=2);n=int(delta.sum());bb=Image.fromarray(delta.astype("uint8")*255).getbbox()
 changedPath=None
 if isNE and n:
  changedPath=O/f"{name}-current-100pct.png";cur.save(changedPath)
 records.append(dict(id=name,globalBox=e["globalBox"],scope="own_native_view" if isNE else "root_view_received" if root6 else "impact_audit_only_no_visual_acceptance",oldImage=e["image"]["file"],oldImageSha256=e["image"]["sha256"],qaReport=e["report"],oldEvidenceReplaysExactly=True,currentPixelDifference=n,currentDifferenceBoxInEvidence=bb,currentImage=str(changedPath) if changedPath else None,currentImageSha256=sha(changedPath) if changedPath else None,currentSources=pieces,sourceHashChanged=[dict(tile=s["tile"],patch=s["patch"]) for s in pieces if not any(o["tile"]==s["tile"] and o["patch"]==s["patch"] and o["sha256"]==s["sha256"] for o in qa["sources"])],evidenceReusable=n==0))
for r in records:
 for s in r["currentSources"]:assert sha(s["file"])==s["sha256"]
out=dict(createdAt=datetime.now(timezone.utc).isoformat(),tile="r09_c08",sourceManifest=str(Q/"manifest.json"),sourceManifestSha256=sha(Q/"manifest.json"),records=records,currentSourcesStableAtEnd=True,originalFilesModified=False,formalAccepted=False)
(O/"source-and-pixel-audit.json").write_text(json.dumps(out,indent=2),encoding="utf8")
print(json.dumps([dict(id=r["id"],diff=r["currentPixelDifference"],sourceChanged=r["sourceHashChanged"],image=r["currentImage"]) for r in records],indent=2))

