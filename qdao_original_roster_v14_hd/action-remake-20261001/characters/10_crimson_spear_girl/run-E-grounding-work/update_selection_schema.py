from pathlib import Path
import json
P=Path(r"D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/10_crimson_spear_girl")
b=P/"run-E-grounding-work"
old=json.loads((b/"selection.json").read_text())
(b/"selection-review.json").write_text(json.dumps(old,ensure_ascii=False,indent=2),encoding="utf-8")
slots={f"run/E/{n:02d}":f"generation/run-E-{n:02d}"+("-v2" if n==12 else "")+"/native.png" for n in range(1,17)}
for n,fn in {3:"run-E-03-v2.png",4:"run-E-04-v2.png",5:"run-E-05-v2.png",6:"run-E-06-v3.png",8:"run-E-08-v3.png",13:"run-E-13-v3.png",14:"run-E-06-v2.png",15:"run-E-15-v2.png",16:"run-E-16-v2.png"}.items():slots[f"run/E/{n:02d}"]="run-E-grounding-work/"+fn
(b/"selection.json").write_text(json.dumps({"slots":slots},indent=2),encoding="utf-8")
a=P/"attack-work";sel=json.loads((a/"selection.json").read_text())
if "slots" not in sel:
 out={"slots":{f"attack/{d}/{int(n):02d}":"attack-work/"+fn for d,frames in sel.items() for n,fn in frames.items()}}
 (a/"selection.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
 for fn in ["audit.py","audit-current.py"]:
  f=a/fn;s=f.read_text(encoding="utf-8").replace('selection=json.loads((B/"selection.json").read_text())','raw=json.loads((B/"selection.json").read_text())["slots"]; selection={d:{str(n):Path(raw[f"attack/{d}/{n:02d}"]).name for n in range(1,13)} for d in ["E","W"]}')
  f.write_text(s,encoding="utf-8")
 f=a/"make_contact.py";s=f.read_text(encoding="utf-8");lines=s.splitlines();lines=[('selected={d:{n:Path(json.loads((B/"selection.json").read_text())["slots"][f"attack/{d}/{n:02d}"]).name for n in range(1,13)} for d in ["E","W"]}' if line.startswith("selected=") else line) for line in lines];f.write_text("\n".join(lines),encoding="utf-8")
for f in [b/"selection.json",a/"selection.json"]:
 d=json.loads(f.read_text());missing=[x for x in d["slots"].values() if not (P/x).exists()];print(f.name,len(d["slots"]),missing)

