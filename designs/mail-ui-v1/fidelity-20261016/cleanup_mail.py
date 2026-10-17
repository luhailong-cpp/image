from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parent
items=[]
for rel in ("art/mail-empty-base.png","qa/mail-fidelity-runtime-check.dll"):
 p=(ROOT/rel).resolve()
 if ROOT.resolve() not in p.parents:raise RuntimeError("Out of package path")
 if p.exists():
  if p.suffix==".png":
   record=p.with_name(p.name+".generation.json");data=json.loads(record.read_text(encoding="utf-8"))
   data["retained"]=False;data["removedAt"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
   data["removalReason"]="Superseded intermediate empty base; approved final mail-empty-frame and runtime sprites are saved, hashed and referenced."
   record.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
  p.unlink();items.append(rel)
(ROOT/"retention.json").write_text(json.dumps({"checkedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"removed":items,"retainedArtMasters":{"art/mail-clean-skin.png":"Current required extraction source for banner, buttons, envelopes, category/gift icons and approved reward icon art.","art/mail-empty-frame.png":"Final runtime empty shell and source for neutral tab; used by current runtime sprites.","art/mail-controls-clean.png":"Final precise empty row and reward-slot controls; current runtime source."},"generationRecordsPreserved":True,"nativeScreenshotAcceptancePending":True},ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"removed":items}))

