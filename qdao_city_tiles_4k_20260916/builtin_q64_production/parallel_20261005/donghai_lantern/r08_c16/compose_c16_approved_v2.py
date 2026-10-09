"""Compose c16's exact pinned DAY repair geometry from 13 real festival natives.

--pin-inputs freezes completed tone + immutable west. --check writes no pixels.
--build writes only this tile's repairs/approved-sync. It recomputes festival
fields (max24) and bounds the complete chain against a pure exact-mask raw
chain. DAY fields are evidence, never applied to festival pixels.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, importlib.util, json, sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
import replay_c16_repairs as r

T=Path(__file__).resolve().parent; OWN=T.parent
D=T/'repairs/approved-sync'; CONTRACT=T/'source-contract-v2/source-contract.json'
CONTRACT_SHA='e60640e0b49db49ecd7f932c4c99b41146ed2b2fc3fcbbedaaccf7c4d2afb289'
LOCK=T/'repairs/approved-sync-input-lock.json'
TONE=T/'tone-assembly/output/tone-assembly-manifest.json'
WEST_INPUT=T/'repairs/consolidated-sync/west-input-lock.json'
LIMIT=24
sha,ref,read,need,verify,cut=r.sha,r.ref,r.read,r.need,r.verify,r.cut
IDS=[f'west-only-joint-s{i}' for i in range(1,5)]+['mast-1024','mast-2048','mast-3072','hull-upper','hull-lower','water-upper','water-lower','west-insertion-finish','west-rail-second']
JOIN_IDS=['west-joint-1-2','west-joint-2-3','west-joint-3-4','hull-pair-1-2','water-pair-1-2']

def now(): return datetime.now(timezone.utc).isoformat()
def js(p,v):
    p=Path(p); need(p.resolve().is_relative_to(T.resolve()),'Write outside c16')
    p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def save(p,a,meta):
    p=Path(p); need(p.resolve().is_relative_to(D.resolve()) and not p.exists(),'Immutable image path invalid '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True); im=a if isinstance(a,Image.Image) else Image.fromarray(a); im.save(p)
    with Image.open(p) as saved: need(np.array_equal(np.asarray(saved),np.asarray(im)),'Saved pixels differ')
    info={**ref(p),'pixels':list(im.size)}; record=Path(str(p)+'.generation.json')
    js(record,{**info,'createdAtUtc':now(),'generatedByAI':False,'actualModel':None,'actualQuality':None,'sourceResampled':False,'formalAccepted':False,**meta})
    return {**info,'generationRecord':ref(record)}

def load_contract():
    need(sha(CONTRACT)==CONTRACT_SHA,'Pinned DAY contract changed'); c=read(CONTRACT)
    need(c['nativeSourceCount']==13 and c['nativeReferenceCount']==14,'Unknown source count')
    need([e['id'] for e in c['nativeSources']]==IDS,'Source ID order changed')
    need([e['id'] for e in c['joinOperations']]==JOIN_IDS,'Join ID order changed')
    need([e['id'] for e in c['insertionOperations']]==list(r.SOURCE_OPS),'Insertion order changed')
    for k in ('historicalBasePNGByteIdentical','historicalExtendedPNGByteIdentical','finalCorePixelIdentical','finalExtendedPixelIdentical','currentOutputPixelIdentical','unionPixelIdentical'):
        need(c['dayReplay'][k] is True,'Missing exact DAY proof '+k)
    snapshots={}
    for e in c['maskAndColorFieldSnapshots']:
        a,s=e['authority'],e['snapshot']; verify(s)
        need(a['sha256']==s['sha256'] and Path(s['file']).resolve().is_relative_to((T/'source-contract-v2').resolve()),'Snapshot does not freeze authority')
        snapshots[(a['file'],a['sha256'])]=s
    m={'seams':copy.deepcopy(c['seamOperations']),'insertions':copy.deepcopy(c['insertionOperations'])}
    for group in m.values():
        for e in group:
            for key in ('maskPng','maskNpz','alpha','localColorMatch','localBoundaryColorMatch'):
                if e.get(key):
                    a=e[key]; e[key]={**a,**snapshots[(a['file'],a['sha256'])]}
    # All replay inputs now point exclusively to owned frozen masks.
    for e in m['seams']: r.seam_alpha(e)
    ss={e['id']:e for e in m['seams']}
    for e in m['insertions']: r.reconstruct_insertion_alpha(e,ss)
    return c,m,snapshots

def pin_inputs():
    load_contract(); bm=read(TONE); bi,ex=bm['candidate'],bm['extendedContext']
    for e in (bi,ex): verify(e)
    need(WEST_INPUT.exists(),'Final c15 requires explicit helper pin-west PATH SHA first')
    wl=read(WEST_INPUT)
    for e in (wl['immutableWest'],wl['immutableWestExtended']): verify(e)
    west,wex=r.rgb(wl['immutableWest']['file']),r.rgb(wl['immutableWestExtended']['file']); base,bex=r.rgb(bi['file']),r.rgb(ex['file'])
    need(base.shape==west.shape==(4096,4096,3) and bex.shape==wex.shape==(4326,4326,3),'Wrong base dimensions')
    need(np.array_equal(bex[115:4211,115:4211],base) and np.array_equal(wex[115:4211,115:4211],west),'Base/core crop mismatch')
    lock={'createdAtUtc':now(),'sourceContract':ref(CONTRACT),'toneManifest':ref(TONE),'baseline':bi,'extendedBaseline':ex,'westInputLock':ref(WEST_INPUT),'immutableWest':wl['immutableWest'],'immutableWestExtended':wl['immutableWestExtended'],'westCoreAndHaloNeverWritten':True}
    if LOCK.exists():
        prior=read(LOCK)
        for k in ('sourceContract','toneManifest','baseline','extendedBaseline','westInputLock','immutableWest','immutableWestExtended'): need(prior[k]==lock[k],'Refusing changed immutable input '+k)
    else: js(LOCK,lock)
    return ref(LOCK)

def raw_evidence(p,record):
    raw=Path(record['evidence']['toolResultSourcePath']); need(record['evidence']['toolResultSha256']==record['sha256'],'Tool digest differs')
    if raw.exists(): need(sha(raw)==record['sha256'],'Raw tool bytes differ'); return {'raw':ref(raw),'cacheAvailable':True}
    audit=OWN/'audit/duplicate-cache-cleanup.json'; need(audit.exists(),'Missing raw without audit')
    entries=[e for e in read(audit)['entries'] if Path(e['nativeFile']).resolve()==p.resolve() and Path(e['originalToolResultSourcePath']).resolve()==raw.resolve()]
    need(len(entries)==1,'Missing unique raw cleanup evidence'); e=entries[0]
    need(e['status']=='deleted' and e['verifiedCacheSha256']==e['retainedNativeSha256AfterDeletion']==record['sha256'],'Raw cleanup digest differs')
    return {'rawFile':str(raw),'sha256':record['sha256'],'cacheAvailable':False,'cleanupEvidence':ref(audit)}

def validate():
    c,m,snapshots=load_contract(); need(LOCK.exists(),'Pin immutable completed tone / west inputs first')
    lock=read(LOCK)
    for k in ('sourceContract','toneManifest','baseline','extendedBaseline','westInputLock','immutableWest','immutableWestExtended'): verify(lock[k])
    wl=read(lock['westInputLock']['file'])
    need(lock['sourceContract']['sha256']==CONTRACT_SHA and lock['immutableWest']==wl['immutableWest'] and lock['immutableWestExtended']==wl['immutableWestExtended'],'Input authority differs')
    base=r.rgb(lock['baseline']['file']); ext=r.rgb(lock['extendedBaseline']['file']); west=r.rgb(lock['immutableWest']['file'])
    need(base.shape==west.shape==(4096,4096,3) and ext.shape==(4326,4326,3),'Bad input dimensions')
    need(np.array_equal(ext[115:4211,115:4211],base),'Base/extended differ')
    arrays,sources,missing={},[],[]
    for en in c['nativeSources']:
        ident=en['id']
        for k in ('geometrySnapshot','generationRecordSnapshot'):
            e=en[k]; verify(e['snapshot']); need(e['authority']['sha256']==e['snapshot']['sha256'],'Changed DAY native snapshot')
        p=Path(en['festivalNativePath'])
        if not p.exists(): missing.append(ident); continue
        rp=Path(str(p)+'.generation.json'); record=read(rp)
        need(sha(p)==record['sha256'] and Path(record['file']).resolve()==p.resolve(),'Native identity differs '+ident)
        need(record['route']=='builtin' and record['tool']=='image_gen.imagegen','Wrong generation route')
        need(record['actualModel'] is None and record['actualQuality'] is None and record['submittedParameters']['model'] is None and record['submittedParameters']['quality'] is None,'Unsupported selector claim')
        need(record['resizedAfterGeneration'] is False and record['finalArtUpscaled'] is False,'Resampled native')
        need(record['dayNativeRepair']['sha256']==en['daySource']['sha256'],'DAY source differs')
        need(record['sourceRectXYXY']==en['sourceRectTileAndHaloXYXY'],'Festival source rectangle differs '+ident)
        verify({'file':record['prompt'],'sha256':record['promptSha256']}); verify({'file':record['requestFile'],'sha256':record['requestSha256']})
        request=read(record['requestFile']); submitted=record['submittedParameters']
        need(request['prompt']==submitted['prompt'] and request['referenced_image_paths']==submitted['referenced_image_paths'],'Request prompt/references differ')
        refs=record['references']; need(len(refs)==len(submitted['referenced_image_paths'])>=3,'Incomplete actual references')
        for rr,sp in zip(refs,submitted['referenced_image_paths']): verify(rr); need(Path(rr['file']).resolve()==Path(sp).resolve(),'Reference order differs')
        need(refs[0]['sha256']==en['daySource']['sha256'],'DAY first reference differs')
        need(any(x['sha256']=='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6' for x in refs),'Missing actual confirmed 04-guild reference')
        verify(record['toneInputLock']); tone_lock=read(record['toneInputLock']['file'])
        need(tone_lock['manifest']==lock['toneManifest'] and tone_lock['candidate']['sha256']==lock['baseline']['sha256'],'Native used a different tone authority')
        x,y,x1,y1=en['sourceRectTileAndHaloXYXY']
        if ident.startswith('west-only-joint-'):
            verify(record['westInputLock']); native_west=read(record['westInputLock']['file'])
            need(native_west['immutableWest']==lock['immutableWest'] and native_west['immutableWestExtended']==lock['immutableWestExtended'],'West reference differs from final authority')
            need(record['sourceRectInPairXYXY']==en['sourceRectInPairXYXY'],'Native pair coordinates differ')
            same_window=np.concatenate((west[y:y1,4096+x:],base[y:y1,:x1]),axis=1)
        else: same_window=base[y:y1,x:x1]
        need(same_window.shape==(1254,1254,3) and np.array_equal(same_window,r.rgb(refs[1]['file'])),'Festival reference is not the exact real same-window crop '+ident)
        previous=record.get('previousOverlap')
        if previous:
            need(len(refs)==4 and previous['fullPreviousImageAttached'] is False,'Whole preceding window unexpectedly attached')
            verify(previous['previousNative']); verify(previous['previousRecord'])
            prior=r.rgb(previous['previousNative']['file']); overlap=cut(prior,previous['sourceCropXYXY'])
            need(np.array_equal(overlap,r.rgb(refs[3]['file'])),'Prior context differs from true overlap crop')
            wx,wy,wx1,wy1=previous['overlapTileAndHaloXYXY']
            need(previous['positionInsideCurrentXYXY']==[wx-x,wy-y,wx1-x,wy1-y] and 0<=wx-x<wx1-x<=1254 and 0<=wy-y<wy1-y<=1254,'Prior context position escapes actual window')
        with Image.open(p) as im:
            need(im.size==(1254,1254) and im.mode in ('RGB','RGBA'),'Wrong native dimensions')
            if im.mode=='RGBA': need(im.getchannel('A').getextrema()==(255,255),'Transparent native')
        arrays[ident]=r.rgb(p); sources.append({'id':ident,'native':ref(p),'record':ref(rp),'daySource':en['daySource'],'sourceRectTileAndHaloXYXY':en['sourceRectTileAndHaloXYXY'],'toolResult':raw_evidence(p,record)})
    return c,m,lock,base,ext,west,arrays,sources,missing,snapshots

def make_qa(result,west,candidate,extended,contract):
    # Use the immutable whole western core when a source window extends farther
    # west than the true 115px c16 halo; no synthetic fill or image resize.
    pair=np.concatenate((west,result[115:4211,115:4211]),axis=1)
    pair_im=Image.fromarray(pair); ext_im=Image.fromarray(result); items=[]
    def crop(name,b,category,pair_space=False):
        if pair_space:
            requested=[b[0]+4096,b[1],b[2]+4096,b[3]]; box=[max(0,requested[0]),max(0,requested[1]),min(8192,requested[2]),min(4096,requested[3])]; image=pair_im
            actual=[box[0]-4096,box[1],box[2]-4096,box[3]]
        else:
            requested=[v+115 for v in b]; box=[max(0,requested[0]),max(0,requested[1]),min(4326,requested[2]),min(4326,requested[3])]; image=ext_im; actual=[v-115 for v in box]
        need(box[0]<box[2] and box[1]<box[3],'Empty QA crop')
        meta={'derivedFrom':[candidate,extended],'operation':'exact original-pixel crop','category':category,'requestedTileAndHaloRectXYXY':b,'actualTileAndHaloRectXYXY':actual,'sourceCanvas':'immutable-c15-plus-c16-core-pair' if pair_space else 'c16-extended','pixelScale':1,'resized':False,'clippedOnlyAtTrueImageCoverage':box!=requested,'visualReview':'pending'}
        items.append({**save(D/'qa'/(name+'.png'),image.crop(box),meta),**meta})
    for e in contract['nativeSources']:
        name=e['id']; b=e['sourceRectTileAndHaloXYXY']; pair_source=name.startswith('west-only-joint-')
        crop(name+'-full1254',b,'native-source-window',pair_source)
        # West input's retained left half belongs to c15, while only x0..627 is inserted.
        x,y,x1,y1=[0,b[1],627,b[3]] if pair_source else b
        for side,box in [('left',[x-224,y,x+224,y1]),('right',[x1-224,y,x1+224,y1]),('top',[x,y-224,x1,y+224]),('bottom',[x,y1-224,x1,y1+224])]: crop(name+'-return-'+side,box,'four-native-window-returns',pair_source or box[0]<-115)
    for axis in ('x','y'):
        for center in (1024,2048,3072):
            for part in range(4):
                b=[center-448,part*1024,center+448,(part+1)*1024] if axis=='x' else [part*1024,center-448,(part+1)*1024,center+448]
                crop(f'{axis}{center}-return-part{part+1:02}',b,'full-internal-seam-return')
    for name,b in [('nw',[0,0,512,512]),('ne',[3584,0,4096,512]),('sw',[0,3584,512,4096]),('se',[3584,3584,4096,4096])]: crop('corner-'+name,b,'tile-corner')
    for y in (1024,2048,3072):
        for x in (1024,2048,3072): crop(f'junction-x{x}-y{y}',[x-256,y-256,x+256,y+256],'internal-junction')
    for part in range(4): crop(f'west-shared-edge-part{part+1:02}',[-448,part*1024,448,(part+1)*1024],'full-4096-west-shared-edge-and-both-returns',True)
    for e in contract['joinOperations']: crop('repair-join-'+e['id'],e['pairOverlapRectXYXY'],'complete-repair-native-overlap')
    need(len(items)==111,'QA coverage changed')
    return items

def run(build=False):
    if not LOCK.exists():
        c,_,_=load_contract(); report={'ready':False,'blockingInputs':['immutable input lock; run --pin-inputs after completed tone'],'sourceContract':ref(CONTRACT),'pixelOutputWritten':False,'DAYWritten':False}
        js(T/'qa/approved-sync-v2-preflight.json',report); return report
    c,m,lock,base,extended,west,arrays,sources,missing,snapshots=validate()
    report={'checkedAtUtc':now(),'ready':not missing,'sourceContract':ref(CONTRACT),'inputLock':ref(LOCK),'verifiedFestivalNativeCount':len(arrays),'requiredFestivalNativeCount':13,'missingNativeIds':missing,'plannedJoinCount':5,'plannedInsertionCount':9,'plannedOriginalPixelQA':111,'maximumPerFieldAndCumulativeDelta':24,'DAYRgbFieldsApplied':False,'pixelOutputWritten':False,'DAYWritten':False,'formalAccepted':False}
    js(T/'qa/approved-sync-v2-preflight.json',report)
    if not build: return report
    need(not missing,'Missing actual festival natives '+','.join(missing)); need(not D.exists(),'Immutable approved-sync already exists')
    raw_core,raw_union=r.replay(m,base,arrays,'raw'); fields=[]
    def sink(label,field,weight,alpha,unused_day_field):
        need(float(np.abs(field).max())<=24+1e-5,'RGB field exceeds24'); p=D/'fields'/(label+'.npz'); p.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(p,delta_rgb=field.astype(np.float32),weight=weight.astype(np.float32),exact_day_alpha=alpha)
        fields.append({'id':label,**ref(p),'maximumAbsoluteDelta':float(np.abs(field).max()),'maximumPermittedDelta':24,'DAYRgbFieldApplied':False,'artBlurred':False,'sourceResampled':False})
    matched,union=r.replay(m,base,arrays,'festival',sink)
    need(np.array_equal(union,raw_union),'RGB changed alpha union'); difference=matched.astype(np.int16)-raw_core.astype(np.int16)
    delta=np.clip(difference,-24,24).astype(np.int8); core=(raw_core.astype(np.int16)+delta.astype(np.int16)).astype(np.uint8)
    need(np.array_equal(core[union==0],base[union==0]),'Final core escaped exact union')
    raw_ext=extended.copy(); raw_ext[115:4211,115:4211]=raw_core; raw_ext[115:4211,:115]=west[:,-115:]
    result=extended.copy(); result[115:4211,115:4211]=core; result[115:4211,:115]=west[:,-115:]
    full_union=np.zeros((4326,4326),np.uint8); full_union[115:4211,115:4211]=union
    scope=full_union.copy(); scope[115:4211,:115]=255
    need(np.array_equal(result[scope==0],extended[scope==0]),'Final extended escaped insertion plus immutable-west scope')
    need(np.array_equal(result[:115],extended[:115]) and np.array_equal(result[4211:],extended[4211:]) and np.array_equal(result[:,4211:],extended[:,4211:]),'Protected halo changed')
    need(np.array_equal(result[115:4211,:115],west[:,-115:]),'West halo not exact immutable neighbor')
    need(len(fields)==14,'Expected 5 join +9 insertion RGB fields')
    final_delta=result.astype(np.int16)-raw_ext.astype(np.int16); need(int(np.abs(final_delta).max())<=24,'Cumulative bound failed')
    dp=D/'fields/final-applied-delta-extended.npz'; np.savez_compressed(dp,delta_rgb=final_delta.astype(np.int8),exact_insertion_union=full_union)
    with np.load(dp,allow_pickle=False) as z: need(np.array_equal(raw_ext.astype(np.int16)+z['delta_rgb'],result.astype(np.int16)),'Saved final field replay differs')
    common={'sourceContract':ref(CONTRACT),'inputLock':ref(LOCK),'repairSources':sources,'exactMaskOperations':c['insertionOperations'],'perStepFields':fields,'finalAppliedDelta':ref(dp),'DAYRgbFieldsApplied':False,'maximumPerStepChannelDelta':24,'maximumCumulativeChannelDelta':int(np.abs(final_delta).max()),'cumulativeLimitReference':'same whole-chain exact-mask raw result including immutable west halo','outsideCoreInsertionUnionChangedPixels':0,'outsideExtendedAuthorizedScopeChangedPixels':0,'immutableWest':lock['immutableWest'],'immutableWestExtended':lock['immutableWestExtended'],'c15CoreAndHaloChangedPixels':0,'westHaloOperation':'copy exact last115 immutable c15 core columns into c16 extended x0..115,y115..4211','sourceResampled':False,'imageBlur':False,'maskBlur':False,'formalAccepted':False,'wholeCityComplete':False,'clientAcceptance':False,'visualReview':'pending original-pixel QA'}
    rawmeta={**common,'operation':'Pure exact DAY mask chain without RGB fields','perStepFields':[],'finalAppliedDelta':None,'maximumCumulativeChannelDelta':0}
    raw_info=save(D/'output/r08_c16-exact-mask-raw.png',raw_core,rawmeta); raw_ext_info=save(D/'output/extended-context-exact-mask-raw.png',raw_ext,rawmeta)
    candidate=save(D/'output/r08_c16.png',core,{**common,'rawBaseline':raw_info}); ex_info=save(D/'output/extended-context.png',result,{**common,'rawBaseline':raw_ext_info})
    union_info=save(D/'masks/union-extended.png',full_union,{'operation':'exact insertion alpha maximum; west copy excluded'}); scope_info=save(D/'masks/authorized-scope-extended.png',scope,{'operation':'insertion union plus exact immutable west halo copy'})
    qa=make_qa(result,west,candidate,ex_info,c)
    for en in (lock['baseline'],lock['extendedBaseline'],lock['immutableWest'],lock['immutableWestExtended']): verify(en)
    for en in sources: verify(en['native']); verify(en['record'])
    verify({'file':str(CONTRACT),'sha256':CONTRACT_SHA})
    manifest={**common,'createdAtUtc':now(),'candidate':candidate,'extendedContext':ex_info,'rawBaseline':raw_info,'rawExtendedBaseline':raw_ext_info,'union':union_info,'authorizedExtendedScope':scope_info,'qa':qa,'script':ref(__file__),'replayScript':ref(r.__file__),'colorMathScript':ref(r.math.__file__),'pixelProof':{'allSavedPngPixelsVerified':True,'finalFieldReplaysExtended':True,'finalCoreEqualsExtendedCrop':True,'outsideCoreUnionEqualsToneBase':True,'outsideExtendedScopeEqualsToneExtended':True,'immutableWestCoreAndHaloHashesUnchanged':True,'maximumFinalDeltaFromRaw':int(np.abs(final_delta).max()),'unclippedMaximumAccumulation':int(np.abs(difference).max()),'channelsLimitedByCumulativeBound':int(np.count_nonzero(np.abs(difference)>24))},'qaCoverage':{'nativeWindows':13,'nativeReturns':52,'seamReturnParts':24,'corners':4,'junctions':9,'westFull4096Parts':4,'completeRepairNativeJoins':5,'pixelScale':1,'c15ExternalCoreSupplied':True}}
    mp=D/'output/integration-manifest.json'; js(mp,manifest)
    return {'candidate':candidate,'extendedContext':ex_info,'manifest':ref(mp),'qaCount':len(qa),'fieldCount':len(fields),'maximumCumulativeChannelDelta':int(np.abs(final_delta).max()),'formalAccepted':False}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__); g=p.add_mutually_exclusive_group(); g.add_argument('--check',action='store_true'); g.add_argument('--pin-inputs',action='store_true'); g.add_argument('--build',action='store_true'); args=p.parse_args()
    try: print(json.dumps(pin_inputs() if args.pin_inputs else run(args.build),ensure_ascii=False,indent=2))
    except (ValueError,FileNotFoundError,KeyError) as e: raise SystemExit('c16 approved composition refused: '+str(e))
