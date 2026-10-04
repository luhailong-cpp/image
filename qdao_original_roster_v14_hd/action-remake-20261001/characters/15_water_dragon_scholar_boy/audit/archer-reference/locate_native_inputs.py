from pathlib import Path
import json,hashlib
B=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy"); out=[]
for d in ["NW","SW"]:
 for n in range(1,17):
  p=B/"provenance/derived"/f"run-{d}-{n:02}.json"
  data=json.loads(p.read_text(encoding="utf8"));g=data["originalGenerationRecord"];host=Path(g["evidence"]["hostOutput"])
  exists=host.exists();sha=hashlib.sha256(host.read_bytes()).hexdigest() if exists else None
  out.append({"slot":f"run/{d}/{n:02}","derivedRecord":p.relative_to(B).as_posix(),"originalGenerationRecord":data["derivedFrom"]["generationRecord"],"originalSource":g["file"],"expectedSha":g["sha256"],"hostOutput":str(host),"hostExists":exists,"hostShaMatches":sha==g["sha256"]})
(B/"audit/archer-reference/native-input-map.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps(out,ensure_ascii=False))

