from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image

D=Path(__file__).resolve().parent
B=D.parent.parent
O=B.parent.parent/'fishing-village-game-20261009/southwest'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p): return {'path':Path(p).as_posix(),'sha256':sha(p)}
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def check(r):
    assert Path(r['path']).is_file(),r['path']
    assert sha(r['path'])==r['sha256'],r['path']
    return Path(r['path'])
def image(p): return np.asarray(Image.open(p).convert('RGB'))
def changed(a,b): return int(np.any(a!=b,axis=2).sum())

def main():
    ledger=O/'current-tile-ledger.json'
    ledger_before=rec(ledger)
    lj=load(ledger)
    t=next(x for x in lj['tiles'] if x['tile']=='r12_c05')
    validated={k:rec(check(t[k])) for k in ('current4096','nativeContext','sourceTrace','internalAudit','artAudit')}
    tr=load(t['sourceTrace']['path'])
    audit=load(t['artAudit']['path'])
    internal=load(t['internalAudit']['path'])
    assert audit['trace']['sha256']==t['sourceTrace']['sha256']
    current_trace_tile=next(x for x in tr['tiles'] if x['tile']=='r12_c05')
    assert current_trace_tile['context']['sha256']==t['nativeContext']['sha256']
    trace_candidate=check(current_trace_tile['candidate'])
    west=image(t['nativeContext']['path'])
    own=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
    own_before=rec(own)
    assert own_before['sha256']=='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef'
    east=image(own)
    assert west.shape==east.shape==(4326,4326,3)
    candidate=image(t['current4096']['path'])
    assert candidate.shape==(4096,4096,3)
    assert np.array_equal(candidate,west[115:4211,115:4211])
    assert np.array_equal(candidate,image(trace_candidate))
    inputs=[image(check(x['context'])) for x in tr['inputs']]
    sourceids=np.load(check(tr['sourceIds']))
    before_overlap=changed(west[:4096],inputs[0][:4096])
    overlap=west[4096:4326]
    same_top=np.all(overlap==inputs[0][4096:4326],axis=2)
    same_bottom=np.all(overlap==inputs[1][:230],axis=2)
    unmatched=int((~(same_top|same_bottom)).sum())
    assert before_overlap==unmatched==0
    crops=[]
    for i in range(4):
        y0=115+1024*i;y1=y0+1024
        wbox=[3981,y0,4211,y1]
        ebox=[115,y0,345,y1]
        patch=np.concatenate([west[y0:y1,3981:4211],east[y0:y1,115:345]],axis=1)
        assert patch.shape==(1024,460,3)
        p=D/f'W{i+1:02d}-actual-corejoin-native.png'
        assert not p.exists()
        Image.fromarray(patch).save(p)
        crops.append({'id':f'W{i+1:02d}','image':rec(p),'dimensions':[460,1024],
            'westContextBox':wbox,'eastContextBox':ebox,'joinLocalX':230,
            'globalBox':[20250,45056+1024*i,20710,45056+1024*(i+1)],
            'globalCoreBoundaryX':20480,'west':t['nativeContext'],'east':own_before,
            'westCropIdentityDifferentPixels':changed(patch[:,:230],west[y0:y1,3981:4211]),
            'eastCropIdentityDifferentPixels':changed(patch[:,230:],east[y0:y1,115:345]),
            'noResize':True,'noBlend':True,'noDrawing':True,'visualReview':'pending'})
    assert rec(ledger)==ledger_before
    assert rec(own)==own_before
    for k,v in validated.items(): assert sha(v['path'])==v['sha256']
    result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'Read-only latest ledger and directly referenced r12c05 records; native integer diagnostic crops only.',
        'formalAccepted':False,'ledger':ledger_before,'ledgerUpdatedAtUtc':lj['updatedAtUtc'],'ledgerEntry':t,
        'verifiedFiles':validated,'candidateFromTrace':rec(trace_candidate),
        'sourceClassification':{'currentCandidateNativeCoreIdentityDifferentPixels':0,'traceCandidateIdentityDifferentPixels':0,
            'recordedSourcePixelIdentity':tr.get('sourcePixelIdentity'),'recordedNativePixelsResampled':tr.get('nativePixelsResampled'),
            'currentContextUnmatchedPixelsToNativeInputs':unmatched,'beforeOverlapDifferentPixels':before_overlap,
            'sourceIdShape':list(sourceids.shape),'sourceIdValues':[int(x) for x in np.unique(sourceids)],
            'classification':'native integer source selection assembly; no resampling/blending observed in current trace'},
        'qaStatus':{'ledgerInternalQa':t['internalQa'],'ledgerSharedEdgesQa':t['knownSharedEdgesQa'],
            'internalAuditStatus':internal['status'],'internalAuditBoundContext':internal['context'],
            'latestArtAuditStatus':audit['status'],'latestArtAuditScope':audit['scope'],
            'assemblyTraceStatus':tr['status'],'assemblyTraceStatusExplained':'Later hash-bound art audit supersedes pending visual QA for the specifically reviewed pair only.',
            'eastEdgeToR12c06PreviouslyPassed':False,'otherOuterEdgesPending':t['outerEdgesPending'],
            'formalMapAcceptance':audit.get('formalMapAcceptance')},
        'stability':{'hashesMatchCurrentLedger':True,'unchangedDuringDiagnostic':True,'ledgerAdoptedArtExport':t['artExport'],
            'explicitFreezeEvidenceFound':False,'scope':'Only latest ledger and referenced records inspected; no live owner freeze or future immutability is claimed.',
            'diagnosticSnapshotFixed':True},'ownContext':own_before,'ownAssembly':rec(own.parent/'assembly.json'),
        'crops':crops,'artworkChanged':False,'newGenerationCount':0}
    p=D/'diagnostic-inputs-v1.json'
    assert not p.exists()
    p.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'manifest':rec(p),'ownerContext':t['nativeContext'],'qaStatus':result['qaStatus'],'stability':result['stability'],'crops':[x['image'] for x in crops]},ensure_ascii=False))

if __name__=='__main__':main()
