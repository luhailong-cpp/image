from pathlib import Path
from PIL import Image
import numpy as np
import hashlib, json, datetime

R=Path(__file__).resolve().parent
O=R/'handoff-scope-change'
O.mkdir(exist_ok=True)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):
 p=Path(p)
 with Image.open(p) as im: size=list(im.size)
 return {'file':str(p),'sha256':sha(p),'size':size}
def difference(base,proposal,name):
 a=np.asarray(Image.open(base).convert('RGB'));b=np.asarray(Image.open(proposal).convert('RGB'))
 assert a.shape==b.shape
 d=np.any(a!=b,axis=2); ys,xs=np.where(d)
 p=O/(name+'-actual-diff-mask.png');Image.fromarray(d.astype('uint8')*255).save(p)
 return {'base':info(base),'proposal':info(proposal),'actualDifferenceMask':info(p),
 'changedPixels':int(d.sum()),'changedBBoxLTRB':None if not d.any() else [int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
 'integration':'Copy proposal RGB exactly at mask==255; do not multiply alpha or replace the whole neighboring tile.'}

raw=R/'tiles/r08_c11-candidate.png'
internal=R/'repairs/internal/r08_c11-internal-candidate-v5.png'
jointn=R/'repairs/south/output/r08_c11-south-candidate-v1.png'
joints=R/'repairs/south/output/r09_c11-north-candidate-v1.png'
south=R.parent/'tiles/current/region-v6/r09_c11-candidate.png'
east=R.parent/'r08_c12/repairs/south/output/r08_c12-south-candidate-v4.png'
diffs={
 'internalVersusRaw':difference(raw,internal,'internal-versus-raw'),
 'southChangesToOwnTile':difference(internal,jointn,'south-versus-internal'),
 'southChangesToNeighbor':difference(south,joints,'r09_c11-versus-frozen-region-v6')}
assert diffs['southChangesToNeighbor']['changedBBoxLTRB'][3]<=627

records=[]; errors=[];cache={}
for p in sorted(R.rglob('*.generation.json')):
 j=json.loads(p.read_text(encoding='utf8'))
 if j.get('route')!='builtin':continue
 f=Path(j['file']); actual=sha(f) if f.exists() else None
 refs=[]
 for ref in j.get('references',[]):
  rf=Path(ref['file']);key=str(rf)
  if key not in cache:cache[key]=sha(rf) if rf.exists() else None
  valid=cache[key]==ref.get('sha256')
  refs.append({'file':key,'recordedSha256':ref.get('sha256'),'currentSha256':cache[key],'matches':valid})
  if not valid:errors.append({'record':str(p),'reference':key,'problem':'reference hash mismatch or missing'})
 evidence=j.get('evidence',{}).get('toolOutputHintFile')
 good=actual==j.get('sha256')
 if not good:errors.append({'record':str(p),'problem':'output hash mismatch or missing'})
 if not evidence or not Path(evidence).exists():errors.append({'record':str(p),'problem':'missing tool output hint evidence'})
 records.append({'record':str(p),'recordSha256':sha(p),'output':str(f),'sha256':actual,'outputHashMatches':good,
 'size':[j.get('width'),j.get('height')],'role':j.get('role'),'generatedAt':j.get('generatedAt'),
 'configTarget':{'model':j.get('configSnapshot',{}).get('model'),'quality':j.get('configSnapshot',{}).get('quality')},
 'submittedModel':j.get('submittedParameters',{}).get('model'),'submittedQuality':j.get('submittedParameters',{}).get('quality'),
 'actualModel':j.get('actualModel'),'actualQuality':j.get('actualQuality'),'toolResultPath':j.get('toolResultPath'),
 'prompt':j.get('prompt'),'toolOutputHintFile':evidence,'references':refs})
(O/'ai-return-inventory.json').write_text(json.dumps({'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'receivedAndSavedCount':len(records),'allOutputsNative1254':all(r['size']==[1254,1254] for r in records),
 'errors':errors,'records':records},ensure_ascii=False,indent=2),encoding='utf8')

qa={
 'internal':{'source':info(internal),'review':'All six internal lines and nine junctions viewed at 1:1 on 2026-10-09. Main floor conflict and lantern/post discontinuity corrected; not a clean final acceptance.',
 'evidence':[str(R/'repairs/internal'/('v5-'+n+'.png')) for n in ['x1024','x2048','x3072','y1024','y2048','y3072','junctions']],
 'remaining':['Very faint straight material bands remain on some cream paving regions.','Small bevel notches remain near the floor-joint binary return, especially around tile (2048,3072), and a few other 1-2 px paving edge steps.','External east seam has not been repaired.']},
 'south':{'source':info(jointn),'neighborProposal':info(joints),
 'review':'All native full shared line, north return, south return, three segment junctions and both endpoints viewed; proposal rejected for final integration pending geometric return repair.',
 'remaining':['Major broken jade circular ornament and white stone curb at the south return, roughly old joint x=1150..1500, y=1100..1218 (neighbor y=473..591).','Jade stem black elliptical rim notch near old joint x=1940,y=650..750.','Minor paving bevel notches at some ownership/return cuts.'],
 'evidence':[str(R/'repairs/south/qa'/n) for n in ['shared-full-v1.png','north-return-full-v1.png','south-return-full-v1.png','junction-s2-v1.png','junction-s3-v1.png','junction-s4-v1.png','endpoints-v1.png']]}}
(O/'qa-freeze.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf8')

handoff={
 'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scopeStatus':'STOPPED_OLD_16x16_GENERATION_USER_SWITCHED_TO_6x6',
 'oldTile':'r08_c11','oldGlobalRectXYWH':[40960,28672,4096,4096],'formalAccepted':False,
 'newImagegenCallsAfterScopeStop':0,'imagegenCallsInFlight':0,'currentDirectoryModified':False,'imagesDeleted':False,
 'preferredReusableOwnTile':info(internal),'latestJointOwnTileCandidate':info(jointn),
 'latestJointNeighborProposal':info(joints),'southJointNative':info(R/'repairs/south/output/joint-quilt-native-v1.png'),
 'frozenNeighbors':{'south':info(south),'east':info(east)},'preciseDifferences':diffs,
 'completed':{'structure':1,'originalNativeDetailPatches':16,'replacementNativeP32':1,'internalLocalAIRepairs':2,'southJointNativeSegments':4},
 'aiReturnInventory':str(O/'ai-return-inventory.json'),'sourceEvidenceErrors':errors,
 'qa':str(O/'qa-freeze.json'),
 'pendingAtScopeStop':['South jade base/stone curb return and stem notch repair.','Small internal paving edge/material cleanup.','East joint all four segments.','Final external/four-corner acceptance and current integration.'],
 'reuseGuidance':'Preserve original pixels for compact-map reuse. Internal-v5 is the reusable own-tile base. South-v1 improves the boundary but the r09_c11 proposal has a visibly broken lower return: do not merge automatically. Parent may re-layout and use native pieces for new 6x6 scope.',
 'records':'Prompts, reference hashes, tool-result hints, actual native returns, mechanical field/mask/registration records are all retained. Config model/quality are targets only; builtin did not expose actual version/quality.'}
(R/'handoff-scope-change.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2),encoding='utf8')
(R/'current-work.json').write_text(json.dumps({'status':handoff['scopeStatus'],'handoff':str(R/'handoff-scope-change.json'),
 'complete':False,'formalAccepted':False,'nativeDetailCount':16,'inFlight':0,'newGenerationAllowed':False},ensure_ascii=False,indent=2),encoding='utf8')
(R/'HANDOFF-SCOPE-CHANGE.md').write_text('''# r08_c11 — old 16×16 scope frozen

Stopped new image generation after the user changed the map to a compact 6×6 layout. No in-flight calls; no current files overwritten; no image deletion.

Reusable own-tile base: `repairs/internal/r08_c11-internal-candidate-v5.png` (4096×4096). Latest south proposal: `repairs/south/output/r08_c11-south-candidate-v1.png`, paired with `r09_c11-north-candidate-v1.png`. The neighbor proposal is **not accepted**: jade medallion and white curb have a conspicuous broken lower return. Do not auto-integrate it.

All 16 original native detail patches, one replacement p32, two internal AI repairs, one structure image, and four south joint native images are saved with generation evidence. The six internal lines and nine junctions were reviewed at actual pixels; small bevel notches and faint material bands remain. East shared-edge repair never started.

See `handoff-scope-change.json` for exact paths/SHA256/base/proposal/difference masks, `handoff-scope-change/ai-return-inventory.json` for call provenance, and `handoff-scope-change/qa-freeze.json` for actual review evidence. Preserve these assets for native-pixel reuse in the compact layout.
''',encoding='utf8')
print(json.dumps({'handoff':str(R/'handoff-scope-change.json'),'aiReturnCount':len(records),'sourceEvidenceErrors':errors,
 'diffs':{k:{'changedPixels':v['changedPixels'],'bbox':v['changedBBoxLTRB']} for k,v in diffs.items()}},ensure_ascii=False,indent=2))
