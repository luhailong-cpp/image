from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
prod=Path(__file__).resolve().parent.parent;root=prod.parent;batch=Path(__file__).resolve().parent
base=prod/'donghai_lantern/r08_c08_c09_c10_joint';out=base/'output_v2';qa=out/'qa'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rel=lambda p:Path(p).relative_to(root).as_posix()
review_path=qa/'visual-review-20260920.json';ledger_path=batch/'lantern-v2-ledger-update-20260920.json'
assert not review_path.exists() and not ledger_path.exists(), 'Refusing overwrite of final review or ledger'
a=json.loads((out/'assembly.json').read_text(encoding='utf-8'))
assert sha(a['source']['path'])==a['source']['sha256']
for x in a['outputs']:assert sha(x['file'])==x['sha256'] and list(Image.open(x['file']).size)==x['pixels']
for x in a['qa']:assert sha(x['path'])==x['sha256']
assert sha(a['previousAssembly']['file'])==a['previousAssembly']['sha256']
for x in a['registeredRepairs']:
 assert sha(x['record'])==x['recordSha256']
 assert sha(x['maskPath'])==x['maskSha256']
 assert sha(x['registrationFieldPath'])==x['registrationFieldSha256']
record_paths=list(sorted((prod/'donghai_lantern/r08_c10/native').glob('*.record.json')))
assert len(record_paths)==16
repair=base/'repairs_v2/fish_basin/native.record.json';record_paths.append(repair);records=[]
for p in record_paths:
 r=json.loads(p.read_text(encoding='utf-8'))
 for k,h in [('outputPath','outputSha256'),('sourceOutputPath','sourceOutputSha256'),('promptPath','promptSha256'),('guidePath','guideSha256'),('submittedReferencePath','submittedReferenceSha256')]:assert sha(r[k])==r[h]
 assert sha(r['outputPath'])==sha(r['sourceOutputPath'])
 for ref in r['actualInputReferences']:assert sha(ref['path'])==ref['sha256']
 im=Image.open(r['outputPath']).convert('RGBA');assert im.size==(1254,1254) and im.getchannel('A').getextrema()==(255,255)
 records.append(dict(file=str(p),sha256=sha(p),sourceSha256=r['outputSha256'],pixels=[1254,1254],opaque=True))
before=np.array(Image.open(a['source']['path']).convert('RGB'));after=np.array(Image.open(out/'extended-context-triple.png').convert('RGB'))
x0,y0,x1,y1=a['registeredRepairs'][0]['boxXYXY'];mask=np.array(Image.open(qa/'fish_roi_mask.png'))
assert np.array_equal(before[:y0],after[:y0]) and np.array_equal(before[y1:],after[y1:])
assert np.array_equal(before[y0:y1,:x0],after[y0:y1,:x0]) and np.array_equal(before[y0:y1,x1:],after[y0:y1,x1:])
assert np.array_equal(before[y0:y1,x0:x1][mask==0],after[y0:y1,x0:x1][mask==0])
core=np.array(Image.open(out/'core12288x4096.png').convert('RGB'))
assert np.array_equal(core,after[115:4211,115:12403])
assert np.array_equal(np.concatenate([np.array(Image.open(out/f'r08_c{c:02d}.png').convert('RGB')) for c in (8,9,10)],axis=1),core)
assert np.array_equal(np.array(Image.open(out/'r08_c08.png').convert('RGB')),np.array(Image.open(prod/'donghai_lantern/r08_c09/joined_pair_v3/r08_c08.png').convert('RGB')))
mechanical=dict(status='pass',createdAtUtc=datetime.now(timezone.utc).isoformat(),baseNativeRecordCount=16,newNativeRepairCount=1,records=records,zeroMaskPixelsUnchanged=True,rejoinPixelIdentical=True,c08PixelsUnchangedFromSelectedPairV3=True,noArtUpscaling=True,sourceAssemblySha256=sha(out/'assembly.json'),registration=a['registeredRepairs'][0]['mechanical'],accepted=False,runtimePublished=False)
mechpath=qa/'mechanical-audit-20260920.json';mechpath.write_text(json.dumps(mechanical,ensure_ascii=False,indent=2),encoding='utf-8')
review=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),status='passed_local_continuity_review_not_runtime_accepted',scope='Donghai lantern c08/c09/c10 triple, inherited c08/c09 plus new c10 and native fish repair',approvedForRootMerge=True,accepted=False,wholeCityComplete=False,runtimePublished=False,viewMethod='view_image detail=original; entire native seam montage panels read at original pixel scale; overview only used for composition',referenceRead=['20260919 handoff and exact snapshot','donghai checkpoint 20260919','selected day output_v3 exact fish crop','lantern output_v1 exact fish crop'],generation=dict(newCalls=1,newNativePixels=[1254,1254],record=str(repair),recordSha256=sha(repair),route='builtin_image_gen',configuredModelTarget='gpt-image-2.5-sunburst',configuredQualityTarget='max',actualBackendModel=None,actualQualityPreset=None,separateBilledApiUsed=False),fullSeamsViewed=[x for x in a['qa'] if '_full_native' in x['path']],junctionsViewed=[x for x in a['qa'] if 'junction_' in x['path']],repairReturnEdgesViewed=[x for x in a['qa'] if '_return.png' in x['path']],repairWholeSupportViewed=dict(file=str(qa/'fish_reconnected_native.png'),sha256=sha(qa/'fish_reconnected_native.png')),maskInspected=dict(file=str(qa/'fish_roi_mask.png'),sha256=sha(qa/'fish_roi_mask.png')),overviewViewed=dict(file=str(qa/'overview.jpg'),sha256=sha(qa/'overview.jpg')),findings=[dict(id='blue_fish_multiple_eyes_heads',status='resolved',detail='The native rewrite follows selected day blue-fish silhouettes: two exposed blue heads each show one visible eye; repeated body eyes and repeated head partitions removed. Lantern gold rim light, basin contour, ice and neighboring fish remain continuous.'),dict(id='fish_repair_return_edges',status='pass',detail='Viewed full1254 support, actual polygon mask, four top/left/right/bottom return regions. No new clipped rim, doubled contour, missing ice or visible repair boundary.'),dict(id='all_six_c10_internal_full_seams',status='pass',detail='Three vertical and three horizontal full4096 seams inspected. Rail, canopy, stone, foliage, lantern and fish contours remain connected.'),dict(id='both_full_cross_tile_seams',status='pass',detail='Both c08/c09 and c09/c10 full4096 boundaries inspected. Repaired fish-basin crossing at x8192/y3072 has clean anatomy and continuous wooden basin/ice borders.'),dict(id='c09_affected_horizontal_seam',status='pass',detail='The whole c09 y3072 seam was additionally inspected because repair extends left of x8192.'),dict(id='twelve_junctions',status='pass',detail='All12 native900 junction closeups inspected in output_v2, including the4 outstanding from9/19.'),dict(id='blue_canopy_tone_transition',status='local_candidate_pass_with_observation',detail='Complete x8192 seam plus x8192/y1024 and y2048 closeups inspected. Very mild brush-tone variation remains within broad lantern reflection shapes; no definite broken fold, rim discontinuity or narrow seam band. Nearest-camera rendering and cross-appearance whole-map tone acceptance remain pending.')],mechanicalEvidence=dict(file=str(mechpath),sha256=sha(mechpath)),remainingAcceptance=['whole256-tile appearance and64K reassembly','all other external neighboring seams','cross-appearance exact geometry and navigation','independent foreground','closest camera and movement','seasonal switch','Unity device performance'],sourceCounts='Only this1 additional native source is new. The16 lantern base sources, prior day repairs and all486 previous retained detail sources must not be counted as new.')
review_path.write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
reviewed=dict(a);reviewed['status']='candidate_local_continuity_reviewed_not_runtime_accepted';reviewed['visualReview']=dict(file=str(review_path),sha256=sha(review_path));reviewed['preReviewAssembly']=dict(file=str(out/'assembly.json'),sha256=sha(out/'assembly.json'))
ap=out/'assembly-reviewed-20260920.json';assert not ap.exists();ap.write_text(json.dumps(reviewed,ensure_ascii=False,indent=2),encoding='utf-8')
candidates=[]
for i,c in enumerate((8,9,10)):
 f=out/f'r08_c{c:02d}.png'
 candidates.append(dict(appearance='donghai_lantern',displayName='东海渔村·元宵',tile=f'r08_c{c:02d}',file=rel(f),sha256=sha(f),assembly=rel(ap),qa=rel(review_path),finalPixelRectXYWH=[(c-1)*4096,28672,4096,4096],worldRect=dict(x=181.25+i*18.75,z=150,width=18.75,height=18.75),pixels=[4096,4096],accepted=False,runtimePublished=False,status='candidate_local_continuity_reviewed_not_runtime_accepted'))
ledger=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),candidates=candidates,repairRecords=[rel(repair)],phase='Lantern triple c08/c09/c10 local continuity reviewed, fish anatomy repair complete',approvedForRootMerge=True,formallyAcceptedTiles=0,wholeCitiesCompleted=0,newUniqueCandidateCoordinates=1,replacementCandidateCoordinates=2,incrementalExtraNativeSources=1,reviewSha256=sha(review_path),mechanicalEvidenceSha256=sha(mechpath),runtimePublished=False,warning='Day output_v3 already merged. Do not remerge day ledger or486 historical sources. Only this ledger new fish repair is incremental.')
ledger_path.write_text(json.dumps(ledger,ensure_ascii=False,indent=2),encoding='utf-8')
cp=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),status='lantern_local_review_pass_ready_for_root_merge',latestCandidateDirectory=str(out),ledgerPath=str(ledger_path),ledgerSha256=sha(ledger_path),newNativeSources=[dict(record=str(repair),recordSha256=sha(repair),sourceSha256=records[-1]['sourceSha256'])],daySelectedDirectory='donghai_day/r08_c08_c09_c10_joint/output_v3',allBaseNativeAlready16of16=True,rootLedgerModified=False,runtimePublished=False,formalAccepted=False,reviewPath=str(review_path),reviewSha256=sha(review_path),note='9/19 checkpoint preserved as history; output_v1, output_v2 and all native bytes retained. No pending generations.')
(batch/'checkpoint-lantern-reviewed-20260920.json').write_text(json.dumps(cp,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(ledger=str(ledger_path),ledgerSha256=sha(ledger_path),candidates=3,newCoordinates=1,newNativeSources=1,review=str(review_path),status=review['status']),ensure_ascii=False))
