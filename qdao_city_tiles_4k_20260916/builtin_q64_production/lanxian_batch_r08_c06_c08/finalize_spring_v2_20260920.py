from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

ROOT=Path('E:/work/image/qdao_city_tiles_4k_20260916')
P=ROOT/'builtin_q64_production';D=P/'lanxian_spring/triple_r08_c06_c08';Q=D/'qa_v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def write(p,obj):
    assert not p.exists(),f'Preserve existing version: {p}'
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ap=D/'output_v2/assembly.json';a=j(ap)
assert sha(a['triple'])==a['tripleSha256']
assert sha(a['extendedContext'])==a['extendedContextSha256']
assert sha(a['previousAssembly'])==a['previousAssemblySha256']
assert sha(a['newTileAssembly'])==a['newTileAssemblySha256']
assert sha(a['priorPairV6'])==a['priorPairV6Sha256']
tilebase=P/'lanxian_spring/r08_c08'
sources=j(a['newTileAssembly'])['nativeSources'];assert len(sources)==16
for s in sources:
    for fk,hk in [('nativeFile','nativeSha256'),('recordFile','recordSha256'),('promptFile','promptSha256'),('guideFile','guideSha256')]:
        assert sha(tilebase/s[fk])==s[hk],s[fk]
    assert sha(s['sourceOutputPath'])==s['nativeSha256']==s['sourceOutputSha256']
    with Image.open(tilebase/s['nativeFile']) as im:
        assert im.size==(1254,1254)
        assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
select=j(tilebase/'source-selection.json')['r01_c03']
assert sha(tilebase/select['rejectedNative'])==select['rejectedSha256']
repairs=[]
current=np.array(Image.open(a['triple']).convert('RGB'))
previous=np.array(Image.open(j(a['previousAssembly'])['triple']).convert('RGB'))
touched=np.zeros(current.shape[:2],bool)
for r in a['repairs']:
    rp=Path(r['record']);rec=j(rp)
    assert sha(rp)==r['recordSha256']
    assert sha(rec['sourceOutputPath'])==sha(rec['outputPath'])==rec['outputSha256']
    assert sha(rec['prompt'])==rec['promptSha256']
    assert rec['actualInputCount']==len(rec['actualInputs'])==1
    for ref in rec['actualInputs']:assert sha(ref['path'])==ref['sha256']
    with Image.open(rec['outputPath']) as im:
        assert im.size==(1254,1254)
        assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
    assert sha(r['fields'])==r['fieldsSha256']
    fields=np.load(r['fields']);mask=fields['mask'];flow=fields['flow']
    assert float(np.abs(flow).max())<=8.00001
    l,t,rr,b=r['rectTripleXYXY'];assert mask.shape==(b-t,rr-l)
    touched[t:b,l:rr]|=mask>0
    repairs.append(rel(rp))
assert np.array_equal(current[~touched],previous[~touched])
assert np.array_equal(current[:,:4096],previous[:,:4096])
rejoined=[]
for c in a['candidates']:
    assert sha(c['file'])==c['sha256']
    im=np.array(Image.open(c['file']).convert('RGB'));assert im.shape==(4096,4096,3);rejoined.append(im)
    assert sha(c['extendedContext'])==c['extendedContextSha256']
    ex=np.array(Image.open(c['extendedContext']).convert('RGB'));assert np.array_equal(ex[115:4211,115:4211],im)
assert np.array_equal(np.concatenate(rejoined,axis=1),current)
edge_manifest=j(Q/'four-edge-crops.json')
for x in edge_manifest['actualRoiEdges']:assert sha(x['file'])==x['sha256']
inspected=[]
for f in sorted(Q.glob('*.png')):
    inspected.append({'file':str(f),'sha256':sha(f),'method':'view_image detail original in resumed 2026-09-20 session','resized':False})
inspected.append({'file':str(Q/'overview.jpg'),'sha256':sha(Q/'overview.jpg'),'method':'overview only; downsampled preview, not acceptance source','resized':True})
assert len(inspected)==47,len(inspected)
v3=j(D/'output_v3/assembly.json')
qa={
 'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'status':'local_candidate_visual_QA_passed_not_formal_city_acceptance',
 'appearance':'lanxian_spring','selectedOutputVersion':'output_v2','approvedForRootMerge':True,
 'assembly':{'file':str(ap),'sha256':sha(ap)},'inspectedFiles':inspected,
 'inspectionCoverage':{'c08InternalFullSeams':6,'c07AffectedInternalFullSeams':3,'pixelsPerFullSeam':4096,'c07c08FullBoundary':1,'boundaryCrossings':3,'c08InternalCrossings':9,'repairSupportCrops':4,'actualRepairRoiEdges':16,'outerContextReturns':2,'shortBreakDetails':2,'overview':1},
 'findings':[
  'The two recorded short grout/bevel breaks are continuous in v2. Entire c07/c08 core border, six c08 internal seams, three affected c07 internal seams, twelve crossings and sixteen actual ROI edges inspected at original pixel scale; no clear core structural discontinuity observed.',
  'Gray and ivory surface brushwork now transitions gradually across the repaired shared core boundary. Existing more textured stone farther right remains visible and is not reclassified as an upscale.',
  'Top and bottom repair crops meet the current 4096px tile limits. Outer 115px context is inherited and has not been accepted against future north/south neighbors.',
  'A small upper trim kink in the outer-return crop is at extended y<115, outside the produced core and unchanged by both v2/v3. It remains a neighbor-boundary follow-up, not a passed outer-neighbor seam.',
  'v3 reused the same four native files with four-edge tapering as a mechanical comparison. It reintroduced the old material transition at the upper tile edge, so v2 remains selected; v3 and its registration fields are preserved unselected.'
 ],
 'mechanicalValidation':{'selectedNativeSources':16,'newRepairSources':4,'nativeBytesMatchHost':True,'nativeSources1254Opaque':True,'fourRepairInputsAndPromptHashesChecked':True,'allPixelsOutsideMasksUnchanged':True,'c06UnchangedFromPrevious':True,'splitReconstructionExact':True,'sourceUpscaledTo4K':False,'localRegistrationMaximumPixels':8},
 'preservedAlternative':{'assembly':str(D/'output_v3/assembly.json'),'sha256':sha(D/'output_v3/assembly.json'),'tripleSha256':v3['tripleSha256'],'selected':False},
 'pending':['north/south/east outer neighbors and all 256 tiles','exact cross-appearance geometry/navigation/foreground agreement','Unity nearest-camera and movement acceptance'],
 'formalAcceptance':False,'wholeCityAccepted':False,'runtimePublished':False
}
qa_path=D/'visual-review-v2-20260920.json';write(qa_path,qa)
rows=[]
for c in a['candidates']:
    rows.append({'appearance':'lanxian_spring','displayName':'揽仙镇春节','tile':c['tile'],'file':rel(c['file']),'sha256':c['sha256'],'assembly':rel(ap),'qa':rel(qa_path),'finalPixelRectXYWH':c['finalPixelRectXYWH'],'worldRect':c['worldRect'],'accepted':False,'runtimePublished':False})
ledger={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'candidates':rows,'repairRecords':repairs,'newNativeSources':4,'newCoordinates':1,'replacementCoordinates':2,'approvedForRootMerge':True,'qaSha256':sha(qa_path),'note':'Add spring c08 and update c06/c07 provenance to the verified triple. Four new repair sources only; 16 selected c08 base sources and its retained alternative already belong to prior 486 total. v3 uses the same four sources and must not add source count.','formalAcceptance':False,'runtimePublished':False}
lp=P/'lanxian_batch_r08_c06_c08/spring-ledger-root-20260920.json';write(lp,ledger)
print(json.dumps({'qa':str(qa_path),'ledger':str(lp),'inspectedFiles':len(inspected),'newNativeSources':4,'candidateCount':3}))
