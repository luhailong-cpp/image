"""Freeze c16 DAY v5 only after exact historical and final-chain replay.

All writes are in source-contract-v2; DAY and root's base/tone work are read-only.
Superseded baseline paths never count as current hash matches.
"""
from pathlib import Path
from datetime import datetime, timezone
import copy, hashlib, importlib.util, io, json, shutil, sys
import numpy as np
from PIL import Image
import replay_c16_repairs as r

T=Path(__file__).resolve().parent; D=T/'source-contract-v2'; DAY=T.parent.parent/'donghai_day'; DT=DAY/'r08_c16'
sha,ref,read,need,verify=r.sha,r.ref,r.read,r.need,r.verify

def write(p,v):
    p=Path(p); need(p.resolve().is_relative_to(D.resolve()),'Write escaped own source contract')
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')

def raw(a): return hashlib.sha256(a.tobytes()).hexdigest()
def pngsha(a):
    b=io.BytesIO(); Image.fromarray(a).save(b,format='PNG'); return hashlib.sha256(b.getvalue()).hexdigest()

def snap(e,category):
    verify(e); p=D/'snapshots'/category/(e['sha256'][:16]+'-'+Path(e['file']).name)
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): need(sha(p)==e['sha256'],'Snapshot changed '+str(p))
    else: shutil.copyfile(e['file'],p)
    return {'authority':e,'snapshot':ref(p)}

def allrefs(v):
    if isinstance(v,dict):
        if 'file' in v and 'sha256' in v: yield v
        for k,x in v.items():
            if k not in ('qa','insertionQA'): yield from allrefs(x)
    elif isinstance(v,list):
        for x in v: yield from allrefs(x)

def record_check(e):
    verify(e); verify(e['record']); rr=read(e['record']['file'])
    need(rr['sha256']==e['sha256'] and [rr['width'],rr['height']]==[1254,1254],'Native record differs')
    need(rr['route']=='builtin' and rr['actualModel'] is None and rr['actualQuality'] is None,'Wrong actual route metadata')
    need(rr['submittedParameters']['model'] is None and rr['submittedParameters']['quality'] is None,'Unproven selector')
    need(rr['resizedAfterGeneration'] is False and rr['finalArtUpscaled'] is False,'Resampled native')
    verify({'file':rr['prompt'],'sha256':rr['promptSha256']})
    for item in rr['references']: verify(item)
    need(rr['evidence']['toolResultSha256']==e['sha256'],'Recorded tool bytes differ')
    rawp=Path(rr['evidence']['toolResultSourcePath'])
    if rawp.exists(): need(sha(rawp)==e['sha256'],'Retained tool raw differs')
    return {'id':r.native_id(e),'nativeAndRecordVerified':True,'promptAndAllReferencesVerified':True,'toolResultByteSHA':e['sha256'],'toolRawStillAvailable':rawp.exists(),'actualModel':None,'actualQuality':None}

def run():
    cp=DT/'output/assembly-manifest.json'; cp_ref=ref(cp); current=read(cp)
    need(len(current['postprocessingChain'])==1,'Unknown current DAY chain')
    chain=current['postprocessingChain'][0]; verify(chain['integrationManifest']); m=read(chain['integrationManifest']['file'])
    hp=DT/'repairs/integrated-v5/previous-assembly-manifest.json'; historical=read(hp)
    need(sha(hp)==m['baseline']['assemblyManifest']['sha256']==chain['priorOutput']['assemblyManifest']['sha256'],'Historical manifest SHA differs')
    need(historical['output']['sha256']==m['baseline']['sha256']==chain['priorOutput']['sha256'],'Historical base SHA differs')
    need(chain['priorOutput']['availability']=='superseded','Missing explicit historical state')
    for e in (current['output'],current['extendedContext'],chain['review']): verify(e)
    checked={}
    for key,value in m.items():
        if key in ('baseline','qa','insertionQA'): continue
        for e in allrefs(value): verify(e); checked[e['file']]=e['sha256']
    # Import existing generic base-mask arithmetic, with only in-memory DAY mask path changed.
    p=T.parent/'r08_c15/assemble_c15_shared.py'; spec=importlib.util.spec_from_file_location('c16_day_base_replay',p); a=importlib.util.module_from_spec(spec)
    old=sys.dont_write_bytecode
    try:
        sys.dont_write_bytecode=True; spec.loader.exec_module(a)
    finally: sys.dont_write_bytecode=old
    a.DAY_MASKS=DT/'qa/assembly-masks'
    masks,base_mask_evidence=a.load_day_masks(historical); native_arrays={}; base_native_evidence=[]
    for e in historical['nativeSources']:
        verify(e); verify({'file':e['recordFile'],'sha256':e['recordSha256']}); verify({'file':e['promptFile'],'sha256':e['promptSha256']})
        reference_evidence=[]
        for x in e['references']:
            if x.get('availability')=='superseded':
                hr={'file':x['historicalRecord'],'sha256':x['historicalRecordSha256']}; verify(hr)
                need(read(hr['file'])['sha256']==x['sha256'],'Superseded reference record SHA differs')
                reference_evidence.append({'reference':x,'currentPixelsVerified':False,'historicalRecordVerified':True,'historicalRecord':hr})
            else:
                verify(x); reference_evidence.append({'reference':x,'currentPixelsVerified':True})
        rr=read(e['recordFile']); need(rr['sha256']==e['sha256'],'Base record native differs')
        native_arrays[e['row'],e['column']]=a.load_rgb(e['file'],e['sha256'],(1254,1254))
        base_native_evidence.append({'id':e['id'],'native':ref(e['file']),'record':ref(e['recordFile']),'prompt':ref(e['promptFile']),'references':reference_evidence,'supersededReferencesPixelAvailability':'historical-record-only; never current pixel hash matches'})
    need(len(native_arrays)==16,'Missing base native')
    ext,_=a.assemble(native_arrays,masks); base=ext[115:4211,115:4211].copy()
    need(pngsha(base)==historical['output']['sha256'],'Historical core PNG-byte replay failed')
    need(pngsha(ext)==historical['extendedContext']['sha256'],'Historical extended PNG-byte replay failed')
    entries={}; record_evidence=[]
    for e in m['nativeRepairs']:
        ident=r.native_id(e)
        if ident in entries:
            need(e['sha256']==entries[ident]['sha256'] and e['record']==entries[ident]['record'] and e.get('reusedSource') is True,'Repeated source changed')
        else: entries[ident]=e; record_evidence.append(record_check(e))
    need(len(m['nativeRepairs'])==14 and len(entries)==13 and len(m['seams'])==36 and len(m['insertions'])==9,'Unknown c16 integration scope')
    need(list(r.SOURCE_OPS)==[e['id'] for e in m['insertions']],'Insertion order changed')
    arrays={k:r.rgb(e['file']) for k,e in entries.items()}; need(all(v.shape==(1254,1254,3) for v in arrays.values()),'Wrong repair size')
    seams={e['id']:e for e in m['seams']}
    for e in m['seams']: r.seam_alpha(e)
    for e in m['insertions']: r.reconstruct_insertion_alpha(e,seams)
    # Check original native targets against reconstructed raw base / immutable west.
    west=r.rgb(m['immutableWest']['file']); pair=np.concatenate((west,base),axis=1); previous=None; starts=[0,1024,2048,2842]
    for i,y in enumerate(starts,1):
        e=entries[f'west-only-joint-s{i}']; rect=[3469,y,4723,y+1254]
        need(e['sourceRectInPairXYXY']==rect and e['appliedNativeColumns']==[627,1254] and e['c15PixelsApplied'] is False,'West source geometry differs')
        ip=Path(e['file']).with_name(f's{i}-input.png'); meta=read(str(ip)+'.generation.json'); expected=r.cut(pair,rect).copy()
        need(raw(expected)==meta['rawSourceRGBSha256']==e['rawSourceRGBSha256'],'West raw source differs')
        if previous is not None:
            ov=starts[i-2]+1254-y; expected[:ov,627:]=previous[-ov:,627:]
        need(np.array_equal(expected,r.rgb(ip)),'Sequential west native input differs')
        previous=arrays[f'west-only-joint-s{i}']
    for ident in ('mast-1024','mast-2048','mast-3072','hull-upper','hull-lower','water-upper','water-lower'):
        e=entries[ident]; ip=Path(e['file']).parent/'input.png'; meta=read(str(ip)+'.generation.json'); expected=r.cut(base,e['sourceRectXYXY'])
        need(meta['source']['sha256']==m['baseline']['sha256'] and raw(expected)==e['rawSourceRGBSha256']==meta['rawSourceRGBSha256'],'Internal raw source differs '+ident)
        need(np.array_equal(expected,r.rgb(ip)),'Internal input differs '+ident)
    fields=[]; stage_proof=[]
    def field_sink(label,field,weight,alpha,e):
        verify(e)
        with np.load(e['file'],allow_pickle=False) as z:
            need(np.array_equal(field.astype(np.float16),z['delta_rgb']),'RGB field differs '+label)
            need(np.array_equal(weight.astype(np.float16),z['weight']),'Field weight differs '+label)
        fields.append({'id':label,'field':e,'computedFloat16MatchesRecorded':True,'computedWithOriginalFloatPrecision':True})
    def stage_sink(i,e,image):
        if i not in (5,6): return
        ident='west-insertion-finish' if i==5 else 'west-rail-second'; en=entries[ident]; source=en['sourceCandidate']; verify(source)
        need(np.array_equal(image,r.rgb(source['file'])),'Intermediate stage replay differs '+ident)
        ip=Path(en['file']).parent/'input.png'; meta=read(str(ip)+'.generation.json'); expected=r.cut(image,en['sourceRectXYXY'])
        need(raw(expected)==meta['rawSourceRGBSha256'] and np.array_equal(expected,r.rgb(ip)),'Later native target differs '+ident)
        stage_proof.append({'sourceId':ident,'stage':source,'corePixelIdentical':True,'targetCropPixelIdentical':True})
    image,union=r.replay(m,base,arrays,'day',field_sink,stage_sink)
    need(np.array_equal(image,r.rgb(m['candidate']['file'])),'Final integrated core replay differs')
    need(np.array_equal(union,r.mask(m['unionMask'])),'Union reconstruction differs')
    ext[115:4211,115:4211]=image; ext[115:4211,:115]=west[:,-115:]
    need(np.array_equal(ext,r.rgb(m['extendedContext']['file'])),'Final extended replay differs')
    need(np.array_equal(image,r.rgb(current['output']['file'])) and np.array_equal(ext,r.rgb(current['extendedContext']['file'])),'Published output differs')
    need(len(fields)==14,'Expected 5 joins + 9 insertion RGB fields')
    # Freeze only after the complete source graph and pixel replay pass.
    catalog=[]
    for ident,e in entries.items():
        pair_source=ident.startswith('west-only-joint-'); rect=e.get('sourceRectXYXY',e.get('sourceRectInPairXYXY'))
        local=[rect[0]-4096,rect[1],rect[2]-4096,rect[3]] if pair_source else rect
        catalog.append({'id':ident,'daySource':e,'geometrySnapshot':snap(e,'native-geometry'),'generationRecordSnapshot':snap(e['record'],'native-records'),'coordinateSpace':'c15-c16-pair' if pair_source else 'c16-core','sourceRectXYXY':rect,'sourceRectTileAndHaloXYXY':local,'sourceRectInPairXYXY':rect if pair_source else None,'appliedNativeColumns':[627,1254] if pair_source else [0,1254],'c15PixelsApplied':False,'usedByOperations':[k for k,v in r.SOURCE_OPS.items() if ident in v],'festivalNativePath':str(T/'repairs/consolidated-sync/native'/(ident+'.png')),'generationTask':'Builtin 1254 same-geometry conversion; attach actual DAY native, current festival same-window, and confirmed 04-guild. West sources need immutable c15 + c16 tone pair context.','actualModel':None,'actualQuality':None})
    artifacts={}
    for container in (historical['seams'],m['seams'],m['insertions']):
        for item in container:
            for key in ('maskPng','maskNpz','alpha','localColorMatch','localBoundaryColorMatch'):
                if item.get(key):
                    e=item[key]; artifacts[(e['file'],e['sha256'])]=snap(e,'masks-and-fields')
    artifacts[(m['unionMask']['file'],m['unionMask']['sha256'])]=snap(m['unionMask'],'masks-and-fields')
    manifest_snaps=[snap(e,'manifests') for e in (cp_ref,ref(hp),chain['integrationManifest'],chain['review'],ref(DAY/'integrate_c16_repairs.py'),ref(DAY/'integrate_c15_repairs.py'),ref(DAY/'assembly_r08_c16.py'))]
    ops=[dict(e,sourceIds=r.SOURCE_OPS[e['id']],coordinateSpace='core') for e in m['insertions']]
    proof={'historicalBasePNGByteIdentical':True,'historicalExtendedPNGByteIdentical':True,'historicalCoreSHA':historical['output']['sha256'],'historicalExtendedSHA':historical['extendedContext']['sha256'],'baseNativeAndRecordCount':16,'baseMaskCount':15,'seamPngNpzOffsetChecks':36,'insertionMasksReconstructedFrom36Seams':True,'intermediateStages':stage_proof,'finalCorePixelIdentical':True,'finalExtendedPixelIdentical':True,'currentOutputPixelIdentical':True,'unionPixelIdentical':True,'outsideUnionChangedPixels':0,'computedFieldsMatchRecordedFloat16':fields,'coreRawRGBSha256':raw(image),'extendedRawRGBSha256':raw(ext),'westHaloPixelIdenticalToImmutableC15Last115':True,'dayWritten':False}
    need(ref(cp)==cp_ref,'DAY authority changed during verification')
    contract={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c16','revision':2,'status':'verified-current-DAY-integrated-v5-chain','currentDayAssembly':cp_ref,'approvedManifest':chain['integrationManifest'],'historicalAssembly':ref(hp),'authoritativeOutput':current['output'],'authoritativeExtended':current['extendedContext'],'dayGeometrySnapshot':snap(m['candidate'],'verified-day-output'),'dayExtendedSnapshot':snap(m['extendedContext'],'verified-day-output'),'immutableWest':snap(m['immutableWest'],'verified-west'),'immutableWestExtended':snap(m['immutableWestExtended'],'verified-west'),'nativeSourceCount':13,'nativeReferenceCount':14,'nativeSources':catalog,'baseNativeEvidence':base_native_evidence,'repairRecordEvidence':record_evidence,'baseMaskEvidence':base_mask_evidence,'joinOperations':[e for e in m['seams'] if e.get('localColorMatch')],'seamOperations':m['seams'],'insertionOperations':ops,'maskAndColorFieldSnapshots':list(artifacts.values()),'manifestSnapshots':manifest_snaps,'dayReplay':proof,'legacyBaselineResolution':'Published core and assembly paths superseded. Historical manifest matches declared old SHA; exact PNG-byte replay of 16 native sources and 15 masks resolves old core and extended. Never claimed as current hash matches.','westPolicy':{'c15PixelsApplied':False,'nativeAppliedColumns':[627,1254],'extendedWestHalo':'exact immutable c15 last115 columns; c15 unchanged'},'festivalColorPolicy':{'freshFieldsOnly':True,'perFieldMaximumChannelDelta':24,'wholeChainMaximumDeltaVsExactMaskRaw':24,'dayColorFieldsAppliedToFestival':False},'dayWritten':False,'festivalPixelsGenerated':False,'formalAccepted':False,'script':ref(__file__),'replayScript':ref(r.__file__),'sharedMathScript':ref(r.math.__file__)}
    write(D/'source-contract.json',contract); write(D/'day-replay-proof.json',proof); write(D/'conversion-tasks.json',{'sourceContract':ref(D/'source-contract.json'),'uniqueSources':13,'tasks':catalog,'reuse':'west-insertion-finish reused for final upper-diagonal-small-notch; generate once','dayOnlyRGBFieldMaximum':32,'festivalFieldAndCumulativeMaximum':24})
    print(json.dumps({'contract':ref(D/'source-contract.json'),'uniqueNative':13,'nativeReferences':14,'joinFields':5,'insertionFields':9,'dayExactReplay':True,'historicalBaseBytesExact':True,'geometrySnapshot':contract['dayGeometrySnapshot']['snapshot']},ensure_ascii=False,indent=2))

if __name__=='__main__': run()
