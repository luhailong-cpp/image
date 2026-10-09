from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
B=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r05_c10");B6=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r06_c10")
read=lambda p:json.loads(p.read_text(encoding="utf-8-sig"))
ref=lambda p:{"file":str(p),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
v=read(B6/"root-source-pixel-verification.json")
assert v["rootVsReviewedLocalPixelIdentical"]
Image.new("RGBA",(4096,4096),(0,0,0,0)).save(B/"initial-empty-fragment.png")
cp={"createdAtUtc":datetime.now(timezone.utc).isoformat(),"tile":"r05_c10","fragment":ref(B/"initial-empty-fragment.png"),"nativeScale":1,"coveragePixels":0,"coupledBottom":v["source"],"bottomNativeHalo":ref(B/"r06-top-external-halo-native.png"),"manifest":None,"contextJoined":None,"rootSourceVerification":ref(B6/"root-source-pixel-verification.json"),"formalAccepted":False,"rootPublished":False}
assert not (B/"local-source-checkpoint.json").exists()
(B/"local-source-checkpoint.json").write_text(json.dumps(cp,indent=2),encoding="utf-8")
for name in ["grid-ingest.py","grid-assemble.py","grid-finish.py","grid-prepare.py"]:
 s=(B6/name).read_text(encoding="utf-8")
 s=s.replace("r06_c10","r05_c10").replace("r07_c10","r06_c10").replace("r07-top-native-halo","r06-top-external-halo-native").replace("origin=[36864,20480]","origin=[36864,16384]").replace("'tileGlobalOrigin':[36864,20480]","'tileGlobalOrigin':[36864,16384]")
 if name=="grid-prepare.py":
  start=s.index("if not (B/'local-source-checkpoint.json').exists():")
  end=s.index("cp=read(B/'local-source-checkpoint.json')",start)
  s=s[:start]+"assert (B/'local-source-checkpoint.json').exists(), 'Initialize from verified r06 source first'\n"+s[end:]
  s=s.replace("mapref=T/f'r06_c10/r01_c{col:02}-v1/final-v1/joined.png'","mapref=Path(read(sorted((T/f'r06_c10/r01_c{col:02}-v1').glob('final-*/manifest.json'),key=lambda z:z.stat().st_mtime)[-1])['joined']['file'])")
  s=s.replace("Actual native r07 external top halo","Actual native r06 external top halo")
 (B/name).write_text(s,encoding="utf-8")
print("Initialized local r05 from pixel-verified root r06 and native halo.")

