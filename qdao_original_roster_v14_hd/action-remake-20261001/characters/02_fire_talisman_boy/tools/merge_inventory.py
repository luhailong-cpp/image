from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
frames=[]
for p in sorted(ROOT.glob("inventory-*.json")):
    data=json.loads(p.read_text(encoding="utf-8-sig"))
    frames.extend(data.get("frames",[]))
slots=[(x["action"],x["direction"],x["frame"]) for x in frames]
if len(slots)!=len(set(slots)):raise ValueError("duplicate frame slots")
manifest={"character":"02_fire_talisman_boy","root_anchor":[512,920],"anchor_status":"target coordinates; full sequence visual verification pending","target_frames":196,"timing":{"run":{"frameMs":75,"cycleMs":1200,"uniform":True,"clientConfirmed":False},"hit":{"frameMs":40,"cycleMs":240},"attack":{"frameMs":30,"cycleMs":360},"cast":{"frameMs":45,"cycleMs":720}},"frames":sorted(frames,key=lambda x:(x["action"],x["direction"],x["frame"]))}
(ROOT/"inventory.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps({"exported_candidates":len(frames),"target":196,"complete":False}))

