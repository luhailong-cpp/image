from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,numpy as np
A=Path(__file__).resolve().parent;D=A.parent/'donghai_day';R=D/'r08_c14/repairs/west-common-edge'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def rgb(p):return np.array(Image.open(p).convert('RGB'))
def rawsha(a):return hashlib.sha256(a.tobytes()).hexdigest()
def blend(a,b,m):
    w=m.astype(np.uint32)[...,None]
    return ((a.astype(np.uint32)*(255-w)+b.astype(np.uint32)*w+127)//255).astype(np.uint8)
checks=[]
def check(p,s,role):
    actual=sha(p);assert actual==s,(role,str(p),actual,s)
    checks.append({'path':Path(p).as_posix(),'sha256':actual,'expectedMatches':True,'role':role})
mp=D/'tiles/west-integration-r08_c14-manifest.json';M=read(mp);mh=sha(mp)
qp=R/'integration-qa/review.json';Q=read(qp);qh=sha(qp)
native=[];ys=[0,1024,2048,2842]
baseline=[]
for s in M['immutableGuideSources']:
    check(s['file'],s['sha256'],'immutable guide baseline')
    check(s['recordFile'],s['recordSha256'],'immutable source manifest')
    baseline.append(rgb(s['file']))
guidepair=np.concatenate(baseline,axis=1)
for i,s in enumerate(M['nativeRepairSources']):
    check(s['file'],s['sha256'],'native repair');check(s['recordFile'],s['recordSha256'],'generation record')
    a=rgb(s['file']);assert a.shape==(1254,1254,3);native.append(a)
    g=read(s['recordFile']);assert g['route']=='builtin' and g['tool']=='image_gen.imagegen'
    assert g['actualModel'] is None and g['actualQuality'] is None
    assert g['submittedParameters']['model'] is None and g['submittedParameters']['quality'] is None
    assert g['generatedAt'] and g['resizedAfterGeneration'] is False and g['finalArtUpscaled'] is False
    check(g['prompt'],g['promptSha256'],'prompt')
    for rr in g['references']:check(rr['file'],rr['sha256'],'submitted reference')
    assert [str(Path(x).resolve()) for x in g['submittedParameters']['referenced_image_paths']]==[str(Path(x['file']).resolve()) for x in g['references']]
    raw=Path(g['evidence']['toolResultSourcePath']);assert g['evidence']['toolResultSha256']==s['sha256']
    if raw.exists():check(raw,s['sha256'],'original built-in tool result')
    check(s['guideRecord'],s['guideRecordSha256'],'native input provenance')
    expected=guidepair[ys[i]:ys[i]+1254,3469:4723].copy()
    if i:
        overlap=ys[i-1]+1254-ys[i];expected[:overlap]=native[i-1][-overlap:]
    assert np.array_equal(expected,rgb(g['references'][0]['file'])),'reference guide mismatch'
old=M['integrationBaselines'][0]
check(old['historicalRecord'],old['historicalRecordSha256'],'superseded prior current textual provenance')
oldrec=read(old['historicalRecord']);assert oldrec['sha256']==old['sha256']
prior=read(R/'current-c13-before-integration.json');assert prior['currentTileBeforeOverwrite']['sha256']==old['sha256']
assert rawsha(baseline[0][:,3469:])==prior['eastStripEquality']['currentRgbBytesSha256']
outputs=[]
for s in M['outputs']:
    check(s['file'],s['sha256'],'current output');out=rgb(s['file']);assert out.shape==(4096,4096,3);outputs.append(out)
    gp=Path(s['file']+'.generation.json');g=read(gp)
    assert g['sha256']==s['sha256'] and g['integrationManifest']['sha256']==mh
current=np.concatenate(outputs,axis=1)
for r in M['pixelVerification']['unchangedRegions']:
    l,t,rr,b=r['pairRectXYXY'];assert rawsha(current[t:b,l:rr])==r['baselineRGBBytesSha256']==r['candidateRGBBytesSha256']
seams={s['id']:s for s in M['seams']}
strip=native[0].copy()
for i in range(1,4):
    entry=seams[f'strip-s{i}-s{i+1}'];check(entry['maskPng']['file'],entry['maskPng']['sha256'],'longitudinal alpha mask')
    mask=np.array(Image.open(entry['maskPng']['file']).convert('L'));ov=strip.shape[0]-ys[i]
    assert mask.shape==(ov,1254)
    strip=np.concatenate((strip[:-ov],blend(strip[-ov:],native[i][:ov],mask),native[i][ov:]),axis=0)
expected=current.copy();expected[:,3469:4723]=strip
for key,left,right,lo,hi in [('insert-left',guidepair[:,3469:3619],strip[:,:150],3469,3619),('insert-right',strip[:,-150:],guidepair[:,4573:4723],4573,4723)]:
    entry=seams[key];check(entry['maskPng']['file'],entry['maskPng']['sha256'],'insertion alpha mask')
    mask=np.array(Image.open(entry['maskPng']['file']).convert('L'));expected[:,lo:hi]=blend(left,right,mask)
assert np.array_equal(expected,current),'native/mask reconstruction does not match current output'
qa=[]
for q in Q['reviewedImages']:
    check(q['file'],q['sha256'],'owner-viewed QA crop');l,t,r,b=q['pairSourceRectXYXY'];region=current[t:b,l:r]
    actual=rgb(q['file'])
    if 'pieces' in q:
        packed=np.zeros_like(actual)
        for piece in q['pieces']:
            pl,pt,pr,pb=piece['bandRectXYXY'];x,y=piece['sheetOriginXY'];packed[y:y+pb-pt,x:x+pr-pl]=region[pt:pb,pl:pr]
        assert np.array_equal(packed,actual)
    else:assert np.array_equal(region,actual)
    qa.append({'file':q['file'],'sha256':q['sha256'],'exactCurrentPixelBinding':True,'ownerVisualInspection':q.get('visualInspection')})
assert [o['sha256'] for o in Q['outputs']]==[o['sha256'] for o in M['outputs']]
assert not Q['findings'] and Q['coverage']['visualReview']=='complete'
assert sha(mp)==mh and sha(qp)==qh
O={'auditedAtUtc':datetime.now(timezone.utc).isoformat(),'kind':'same_coordinate_current_source_and_QA_binding_audit','integrationManifest':ref(mp),'ownerScopedVisualReview':ref(qp),'currentOutputs':M['outputs'],'priorC13Sha256':old['sha256'],'nativePatchCount':4,'nativeSourcesAll1254':True,'allGuidePixelsExactlyReconstructed':True,'nativeStripAndAllMasksExactlyReconstructCurrentOutputs':True,'unchangedOuterPixelsMatchRecordedBaselineRGBHashes':True,'historicalPriorC13TextProvenanceVerified':True,'retiredPriorC13PNGNotRequired':True,'qaImages':qa,'ownerReviewedScope':Q['scope'],'noNewVisualAcceptanceByThisAudit':True,'actualModel':None,'actualQuality':None,'formalAccepted':False,'newCoordinateCount':0,'checks':checks,'eligibleSameCoordinateC13Update':True,'c14Note':'Updated integrated tiles/r08_c14 exists with the same provenance and scoped QA; parent48 index still selects older output/r08_c14. Do not add a new coordinate.'}
op=A/'donghai-c13-current-update-audit.json';op.write_text(json.dumps(O,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'file':op.as_posix(),'sha256':sha(op),'checks':len(checks),'qaExact':len(qa),'currentOutputs':[{'tile':x['tile'],'sha256':x['sha256']} for x in M['outputs']],'eligibleC13Update':True},ensure_ascii=False))
