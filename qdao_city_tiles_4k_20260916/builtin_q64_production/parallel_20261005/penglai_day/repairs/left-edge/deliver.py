from repair import *
O=R/'both-side'
proposal=read(O/'proposal-v3.json')
checked=[]
for seg in range(1,5):
    for label in ['left-outer','shared','right-outer']:
        p=O/f'qa-v3-{label}-s{seg}.png'
        finding='Continuous reconstructed geometry across shared edge.' if label=='shared' else 'No large structural discontinuity; painted material/detail change may remain at native cut.'
        if seg in [3,4] and label=='left-outer':finding='Small painted bevel/highlight transition remains visible at cut; parent integration review required.'
        checked.append({'file':str(p),'sha256':sha(p),'viewedAtNativeScale':True,'scope':{'segment':seg,'edge':label,'globalYRange':[32768+(seg-1)*1024,32768+seg*1024]},'finding':finding})
for y in [1024,2048,3072]:
    p=O/f'qa-v3-junction-y{y}.png';checked.append({'file':str(p),'sha256':sha(p),'viewedAtNativeScale':True,'scope':{'tileLocalY':y,'fullStripWidth':1254,'viewHeight':320},'finding':'No cut post, rail, stair or paving course across segment junction; low-frequency color match applied, painted texture transitions remain.'})
p=O/'qa-v3-endpoints.png';checked.append({'file':str(p),'sha256':sha(p),'viewedAtNativeScale':True,'scope':{'topBottom':True},'finding':'Current strip endpoints reviewed; adjacent row tiles unavailable and not claimed verified.'})
qa={'reviewedAt':now(),'candidate':proposal,'checked':checked,'status':'ready_for_parent_integration_review','formalAccepted':False,'noWholeCityOrClientAcceptance':True,'style':'Maintains approved clean rounded painted wood, stone and golden roof; no new identity or place-name mapping.','keyOutcome':'One continuous native AI source crosses each1024-long part of c12-c13 edge; no strict center cut restoring conflicting old pixels.','remaining':'Parent must review small outer bevel/paint transitions and integrated c13 joins. Source c13 was raw candidate; merge only the repair mask into newer internally corrected c13.','sourceRecords':[str(R/'repair-v3.png.generation.json')]+[str(R/f's{i}-repair-v1.png.generation.json') for i in [2,3,4]],'integration':{'jointFile':proposal['jointStrip'],'jointGlobalOriginXY':[48525,32768],'jointSize':[1254,4096],'jointCenterX':627,'mask':proposal['mask'],'c12CopySourceBox':[0,0,627,4096],'c12DestinationXY':[3469,0],'c13CopySourceBox':[627,0,1254,4096],'c13DestinationXY':[0,0],'onlyReplaceMaskPositivePixels':True,'c11_c12SharedEdgeUnmodified':True}}
write(O/'qa-reviewed-v3.json',qa)
proposal['status']='ready_for_parent_integration_review';proposal['qaRecord']=str(O/'qa-reviewed-v3.json');write(O/'proposal-v3.json',proposal)
previous=R/'repair-status.json'
if previous.exists():write(R/'repair-status-right-only-history.json',read(previous))
write(previous,{'updatedAt':now(),'status':'both_side_candidate_ready_for_parent_review','latestProposal':str(O/'proposal-v3.json'),'latestQA':str(O/'qa-reviewed-v3.json'),'formalAccepted':False,'originalSourceC12Sha256':sha(BASE),'originalSourceUnchanged':sha(BASE)==H['baselineCandidates'][-1]['sha256'],'c12NewDerivative':proposal['newC12'],'c13NewDerivative':proposal['newC13'],'finishedNativeRepairSegments':4,'newAcceptedTiles':0,'next':'Root reviews and integrates the mask into latest internally repaired c13; native outer bevel transitions remain review items.'})
# Preserve the unique current candidate, source masks/contexts, selected AI outputs,
# and every text/hash record. Superseded derived previews/fulltile copies are not backups.
keep={'c12-right-revised-candidate-v3.png','c13-left-revised-candidate-v3.png','joint-quilt-native-v3.png','joint-quilt-mask-v2.png','joint-quilt-provenance-v2.png'}
removed=[]
for p in O.glob('*.png'):
    if p.name in keep or p.name.startswith('qa-v3-'):continue
    assert p.resolve().parent==O.resolve()
    removed.append({'file':str(p),'sha256':sha(p),'reason':'superseded derived preview/candidate; v3 candidate and complete text provenance retained'})
    p.unlink()
for name in ['joined-v3.png','joined-v4.png','qa-both-edges-v3.png','qa-both-edges-v4.png','candidate-right-native.png','s2-joined-v1.png','s2-qa-v1.png','s2-strip-v1.png','s2-joined-register6.png','s2-qa-register6.png','s2-strip-register6.png','s2-registered6.png','s3-joined-v1.png','s3-qa-v1.png','s3-strip-v1.png','s4-joined-v1.png','s4-qa-v1.png','s4-strip-v1.png']:
    p=R/name
    if not p.exists():continue
    assert p.resolve().parent==R.resolve()
    removed.append({'file':str(p),'sha256':sha(p),'reason':'rejected right-only integration derivative; selected underlying AI output retained for both-side repair'})
    p.unlink()
write(R/'cleanup-derived-20261005.json',{'createdAt':now(),'removed':removed,'currentCandidate':str(O/'proposal-v3.json'),'allGenerationTextRecordsRetained':True,'sharedOrHistoricalSourceFilesDeleted':False})
