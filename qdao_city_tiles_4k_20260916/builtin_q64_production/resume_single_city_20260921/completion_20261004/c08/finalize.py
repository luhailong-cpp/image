from pathlib import Path
from PIL import Image
import json,numpy as np,shutil,hashlib,datetime
R=Path(__file__).resolve().parent;O=R/"final-pair";Q=O/"qa";Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prior=R/"south-pair/candidate-v1";shutil.copy2(prior/"r09_c08.png",O/"r09_c08.png")
n2=np.array(Image.open(O/"r08_c08.png").convert("RGB"));s2=np.array(Image.open(O/"r09_c08.png").convert("RGB"));strip=np.concatenate([n2[-627:],s2[:627]],axis=0)
code=(R/"south-pair/export_pair.py").read_text();code=code[code.index('for axis in'):code.index('t=np.array(')];exec(code)
priorN=np.array(Image.open(prior/"r08_c08.png"));keep=np.ones(n2.shape[:2],bool);keep[:1254,2445:3699]=False
assert np.array_equal(n2[keep],priorN[keep])
manifest={"recordedAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"scope":"r08_c08 full internal 6 seams and 9 intersections; whole4096px paired r08_c08 south/r09_c08 north boundary; patch perimeter reinsertion checks.","outputs":[{"file":str(O/"r08_c08.png"),"sha256":sha(O/"r08_c08.png"),"pixels":[4096,4096]},{"file":str(O/"r09_c08.png"),"sha256":sha(O/"r09_c08.png"),"pixels":[4096,4096]}],"sources":{"northTipAssembly":str(O/"assembly.json"),"southPairAssembly":str(prior/"assembly.json")},"verifiedPixelInvariants":{"northOutsideLastTipCropEqualPreviousReviewedPair":True,"southFileByteIdenticalPreviouslyReviewedPair":sha(O/"r09_c08.png")==sha(prior/"r09_c08.png"),"northSouth627RowsEqualPreviousReviewedPair":bool(np.array_equal(n2[-627:],priorN[-627:]))},"actualModel":None,"actualQuality":None,"formalCityAccepted":False,"missingOrUnboundExternalJoins":["north","west","east"],"southNeighborScope":"r09_c08 top627px coupled join only; remainder unchanged, not independently reaccepted","sourceImageOperations":"All AI edits native1254; no AI output enlarged. 4K composition uses source native pixels. Color correction changes RGB only; structural pixels not geometrically warped or blurred."}
(O/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding="utf-8")
for it in manifest["outputs"]:
 p=Path(it["file"]);g={**it,"operation":"Native image composition derived asset","derivedFrom":manifest["sources"],"actualModel":None,"actualQuality":None,"modelEvidenceNote":"See individual native.png.generation.json records. Configuration target is not actual model proof."};(p.with_suffix(".png.generation.json")).write_text(json.dumps(g,indent=2),encoding="utf-8");Image.open(p).resize((1024,1024)).save(O/(p.stem+"-overview-only.png"))
print(json.dumps(manifest,indent=2))
