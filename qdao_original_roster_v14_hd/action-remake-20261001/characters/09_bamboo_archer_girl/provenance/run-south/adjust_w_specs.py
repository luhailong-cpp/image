import json
from pathlib import Path
root=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/09_bamboo_archer_girl")
for f in [13,14]:
 p=root/"provenance/run-south"/f"stance8-W-{f:02}.spec.json"
 x=json.loads(p.read_text(encoding="utf-8-sig"))
 x["references"][1]=str(root/"runtime/run/W/12.png")
 x["prompt"] += " IMPORTANT: keep the rear supporting ankle directly below the rear edge of the shorts, only slightly screenRIGHT of pelvis. Do not stretch the rear leg out to the far-right frame edge; the planted boot should remain below the character around x550–585, with a soft natural knee. Keep image1's upper silhouette untouched."
 p.write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding="utf-8")

