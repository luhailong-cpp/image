from pathlib import Path
from PIL import Image
import hashlib,json,datetime
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/northeast")
R=Z/'records/west_sol'
Q=Z/'qa/r04_c13-central-v2'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p): return dict(path=str(p),sha256=sha(p))
m=read(Q/'manifest.json')
assert sha(m['candidate']['file'])==m['candidate']['sha256']=='d11bc5e1a5e2d849af9518c347365bf537fcdfb885c76af63880badb6e650027'
assert sha(m['selection']['path'])==m['selection']['sha256']
im=Image.open(m['candidate']['file']).convert('RGB')
assert im.size==(4096,4096)
sources=[]
for e in m['inputs']:
 s=Image.open(e['path']).convert('RGB'); assert s.size==(1254,1254)
 assert sha(e['path'])==e['sha256']
 a=s.crop(e['nativeCropBox']); b=im.crop(e['destinationBox'])
 assert a.tobytes()==b.tobytes()
 assert hashlib.sha256(a.tobytes()).hexdigest()==e['coreRgbPixelSha256']
 sources.append(dict(patch=e['patchId'],source=ref(e['path']),nativePixels=list(s.size),corePixelEquality=True))
checks=[]
for e in m['qa']:
 assert sha(e['file'])==e['sha256']
 q=Image.open(e['file']).convert('RGB')
 assert q.tobytes()==im.crop(e['candidateCropBox']).tobytes()
 name=Path(e['file']).name
 pending=name=='h_p23_p33.native-1to1.png'
 note='Direct 1:1 view: painted material, silhouettes and local contours are coherent; no blocking geometry or artificial seam observed.'
 if pending: note='At candidate x2618..2648, y2048 the fine vertical pillar face/grain highlight shifts approximately 15-20 px. Outer left/right silhouette and surrounding rocks/foliage remain continuous. Retain visual pending; do not mark passed.'
 checks.append(dict(file=e['file'],sha256=e['sha256'],kind=e['kind'],candidateCropBox=e['candidateCropBox'],candidateCropPixelEquality=True,method='Independent direct original-size view of this exact QA PNG',visualPassed=not pending,status='pending' if pending else 'pass',note=note))
ext=read(Q/'external-native-QA/manifest.json')
extnotes={
 'west-r1':'At seam x128 several paving grout segments end or change direction and stone microtexture changes abruptly; timber rail brush texture also changes at exact seam. Fixed snapshot pending.',
 'west-r2':'At seam x128 left vegetation/stone-cap detail terminates against right wall face and paint texture changes vertically. Fixed snapshot pending.',
 'west-r3':'At seam x128 upper paving-to-wall material/contours change abruptly; blue roof paint/contour continuity is not fully clean. Fixed snapshot pending.',
 'west-r4':'At seam x128 roof face texture and some tile contour/highlight positions change; exact vertical transition remains visible. Fixed snapshot pending.',
 'west-junction-r1':'At junction x256 the two timber rail faces change abruptly from smooth left stroke to coarse right grain; adjacent stone material also changes. Fixed snapshot pending.',
 'west-junction-r2':'At junction x256 a vertical paving/stone-wall material transition and contour truncation remains visible. Fixed snapshot pending.',
 'west-junction-r3':'At junction x256 blue tile paint/highlights and local curved tile seams change at the exact vertical source boundary. Fixed snapshot pending.'
}
ec=[]
own={e['patchId']:e for e in m['inputs']}
for e in ext['qa']:
 assert sha(e['path'])==e['sha256']
 actual=Image.open(e['path']).convert('RGB');rebuild=Image.new('RGB',tuple(e['size']))
 for s in e['sources']:
  assert sha(s['path'])==s['sha256']
  if s['patch'] in own:
   assert s['sha256']==own[s['patch']]['sha256']
  part=Image.open(s['path']).convert('RGB').crop(s['crop'])
  rebuild.paste(part,tuple(s['at']))
 assert rebuild.tobytes()==actual.tobytes()
 pending=e['name'] in extnotes
 ec.append(dict(name=e['name'],qa=ref(e['path']),sources=e['sources'],sourcePixelEquality=True,method='Independent direct original-size view of this exact pinned external QA PNG',visualPassed=not pending,status='pending' if pending else 'pass',note=extnotes.get(e['name'],'Native boundary contours and material continue; no discontinuity observed in this pinned segment/junction.')))
assert len(checks)==49 and len(ec)==17
out=dict(schemaVersion=1,reviewer='roof_resume independent of central production',reviewedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),tile='r04_c13',candidate=m['candidate'],selection=m['selection'],manifest=ref(Q/'manifest.json'),nativeSources=sources,mechanical=dict(candidateHashVerified=True,selectedNativeCount=16,all16CorePixelsExactlyEqualCandidate=True,all49QaCropPixelsExactlyEqualCandidate=True,all17ExternalQaExactlyRebuiltFromPinnedNativeCrops=True,allExternalOwnSourcesMatchCandidateSelection=True),internalChecks=checks,internalCheckedCount=49,internalPassCount=48,internalPendingCount=1,internalVisualPassed=False,externalManifest=ref(Q/'external-native-QA/manifest.json'),externalChecks=ec,externalCheckedCount=17,externalPassCount=10,externalPendingCount=7,allExternalEdgesVerified=False,independentAccepted=False,formalAccepted=False,complete4k=False,status='independent_review_complete_pending_one_internal_material_issue_and_west_boundary_snapshot_issues',limitations=['External assessment binds only the pinned source hashes in this snapshot; later neighbor changes require only affected views rechecked.','North/east rows3-4/southwest diagonal not included in provided snapshot; no pass claimed.','No navigation/client/capacity or whole-map acceptance claimed.'],sourceImagesModified=False,sharedProgressModified=False)
dest=R/'r04_c13.central-v2.roof-independent-review.json'
assert not dest.exists()
dest.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(review=ref(dest),internal='48/49 passed, 1 pending',external='10/17 passed, 7 west pending',mechanical=out['mechanical'])))

