from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
from PIL import Image
OUT = Path(__file__).resolve().parent
TILE = OUT.parents[1]
ROOT = TILE.parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p, d): Path(p).write_text(json.dumps(d, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def info(p): return {'file':str(p), 'sha256':sha(p)}
hard = TILE/'assembly_hardcut/extended4326.png'
south = ROOT/'r09_c11/selected/extended4326.png'
hm = json.loads((TILE/'assembly_hardcut/assembly.json').read_text(encoding='utf-8'))
sm = json.loads((ROOT/'r09_c11/selected/delivery.manifest.json').read_text(encoding='utf-8'))
assert sha(hard)==hm['outputs']['extended']['sha256']
assert sha(south)==sm['outputs']['extended']['sha256']
a,b = Image.open(hard).convert('RGB'),Image.open(south).convert('RGB')
assert a.size==b.size==(4326,4326)
# Context origin in target core coordinates = (2957,3469).
# The lower 627 rows are actual selected SOUTH core pixels, not new halo predictions.
context=Image.new('RGB',(1254,1254))
context.paste(a.crop((3072,3584,4326,4211)),(0,0))
context.paste(b.crop((3072,115,4326,742)),(0,627))
target=OUT/'target-context1254.png';context.save(target)
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'target':info(target),
 'size':[1254,1254],'newAIGeneration':False,'actualModel':None,'actualQuality':None,
 'operation':'Exact source pixel crops pasted 1:1; no resampling or artificial extension',
 'contextOriginInTargetCore':[2957,3469],'southCoreStartsAtContextY':627,
 'coreRightEdgeAtContextX':1139,'targetCoreWaterIssueLTRB':[4064,4000,4096,4096],
 'sources':[{'source':info(hard),'cropLTRB':[3072,3584,4326,4211],'targetXY':[0,0]},
            {'source':info(south),'cropLTRB':[3072,115,4326,742],'targetXY':[0,627]}],
 'fixedSouthContextLTRB':[0,627,1254,1254],
 'allowedRepairProposalInTargetCoreLTRB':[3990,3976,4180,4096],
 'sourceHardcutCore':info(TILE/'assembly_hardcut/core4096.png'),
 'sourceHardcutManifest':info(TILE/'assembly_hardcut/assembly.json'),
 'sourceSouthManifest':info(ROOT/'r09_c11/selected/delivery.manifest.json'),
 'formalAccepted':False}
write(str(target)+'.derivation.json',record)
write(OUT/'preparation.json',record)
print(json.dumps(record,ensure_ascii=False))
