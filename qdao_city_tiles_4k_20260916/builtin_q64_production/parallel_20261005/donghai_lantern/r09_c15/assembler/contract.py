"""Frozen r09_c15 DAY pixels/masks and exact raw+color replay, read-only DAY."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, io, shutil
import numpy as np
from PIL import Image
import shared_math as math

T=Path(__file__).resolve().parent.parent
C=T/'assembly-contract-v1'
LOCK=C/'contract.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def ref(p): return {'file':str(p),'sha256':sha(p)}
def dump(p,v):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf-8')
def key(p): return str(Path(p).resolve()).lower()
def pngsha(a):
    s=io.BytesIO();Image.fromarray(a).save(s,format='PNG');return hashlib.sha256(s.getvalue()).hexdigest()
def freeze():
    if LOCK.exists(): return read(LOCK)
    source=read(T/'source-contract.json'); a=read(T/'source-lock/day-output-assembly-manifest.json'); color=read(T/'source-lock/day-color-match-manifest.json')
    assert source['tile']=='r09_c15' and source['globalCoreXYWH']==[57344,32768,4096,4096]
    assert source['nativeWindowOriginXY']==[57229,32653] and source['dayGeometryRepairNativeCount']==0
    files={}
    def take(p,h=None):
        p=Path(p);h=h or sha(p);assert sha(p)==h,f'Current source SHA mismatch: {p}'
        if key(p) in files:assert files[key(p)]['sha256']==h;return files[key(p)]
        dest=C/'snapshots'/f'{h[:16]}-{p.name}';dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert sha(dest)==h
        else:shutil.copyfile(p,dest)
        r={'authorityFile':str(p),'file':str(dest),'sha256':h};files[key(p)]=r;return r
    take(T/'source-contract.json')
    for s in source['manifestSnapshots']:take(s['file'],s['sha256']);take(s['authorityFile'],s['authoritySha256'])
    for n in source['dayNativeSources']:
        assert n['extendedRectXYWH']==[(n['column']-1)*1024,(n['row']-1)*1024,1254,1254]
        take(n['file'],n['sha256']);take(n['recordFile'],n['recordSha256']);take(n['promptFile'],n['promptSha256'])
        for r in n['references']:take(r['file'],r['sha256'])
        assert sha(n['toolResultSourcePath'])==n['sha256']==n['toolResultSha256']
    assert len(a['seams'])==len(color['fields'])==15
    for s in a['seams']:
        for k in ('maskPng','maskNpz'):take(s[k]['file'],s[k]['sha256'])
    take(a['coverage']['countMask']['file'],a['coverage']['countMask']['sha256'])
    for f in color['fields']:
        take(f['originalAlphaFile'],f['originalAlphaSha256']);take(f['differenceField'],f['differenceFieldSha256'])
    take(color['finalCorrection']['file'],color['finalCorrection']['sha256'])
    for q in ('dayFinal','dayExtended'):take(source[q]['file'],source[q]['sha256'])
    for p in (a['script'],a['seamHelper'],color['script']):take(p['file'],p['sha256'])
    north=T.parent/'r08_c15/west-common-edge-v3/output/r08_c15.png'
    take(north,'7c18bf09e962b458ee285c04067655d6198c426d2bb53cccbe13bc58f24c8a4f')
    result={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r09_c15','sourceContract':ref(T/'source-contract.json'),
      'dayAssemblyManifest':ref(T/'source-lock/day-output-assembly-manifest.json'),'dayColorManifest':ref(T/'source-lock/day-color-match-manifest.json'),
      'files':files,'nativeCount':16,'maskCount':15,'dayColorFieldCount':16,
      'northAuthority':{'file':str(north),'sha256':sha(north),'role':'current true north tile for QA only; no source-pixel pasting'},
      'generationPalette':source['palette'],'historicalPaletteAuthority':source['paletteAuthority'],
      'westAuthority':None,'westUnknown':True,'globalCoreXYWH':[57344,32768,4096,4096],'globalExtendedXYWH':[57229,32653,4326,4326],
      'DAYColorFieldsUsedOnlyForReplay':True,'DAYWritten':False,'formalAccepted':False}
    dump(LOCK,result);return result
def frozen(p,lock):
    r=lock['files'][key(p)];assert sha(r['file'])==r['sha256'];return Path(r['file'])
def load_contract():
    lock=freeze()
    for q in lock['files'].values():assert sha(q['file'])==q['sha256']
    s=read(frozen(lock['sourceContract']['file'],lock));a=read(frozen(lock['dayAssemblyManifest']['file'],lock));c=read(frozen(lock['dayColorManifest']['file'],lock))
    assert {(n['row'],n['column']) for n in s['dayNativeSources']}=={(r,col) for r in range(1,5) for col in range(1,5)}
    for n in s['dayNativeSources']:
        x,y=(n['column']-1)*1024,(n['row']-1)*1024
        assert n['extendedRectXYWH']==[x,y,1254,1254]
        assert n['globalRectXYWH']==[57229+x,32653+y,1254,1254]
    return lock,s,a,c
def load_masks(lock,a):
    masks={}
    for e in a['seams']:
        z=np.load(frozen(e['maskNpz']['file'],lock));m=z['alpha_u8'];rect=e['overlapRectExtendedXYWH'];horizontal=e['orientation']=='horizontal'
        label=e['id'].split('_')
        expected_rect=[0,(int(label[2][1:])-1)*1024,4326,230] if horizontal else [(int(label[3][1:])-1)*1024,(int(label[1][1:])-1)*1024,230,1254]
        assert rect==expected_rect,f'Mask not at its exact grid coordinate: {e["id"]}'
        assert np.array_equal(m,np.asarray(Image.open(frozen(e['maskPng']['file'],lock))))
        assert z['overlap_rect_extended_xywh'].tolist()==rect and int(z['transition_width_pixels'])==2
        assert m.dtype==np.uint8 and m.shape==((230,4326) if horizontal else (1254,230))
        distance=np.arange(230)[None,:]-z['seam_offsets'][:,None]
        again=np.where(distance<=-2,0,np.where(distance==-1,64,np.where(distance==0,191,255))).astype(np.uint8)
        if horizontal:again=again.T
        assert np.array_equal(m,again)
        masks[e['id']]=m.copy()
    expected={f'vertical_r{r:02}_c{c-1:02}_c{c:02}' for r in range(1,5) for c in range(2,5)}|{f'horizontal_r{r-1:02}_r{r:02}' for r in range(2,5)}
    assert set(masks)==expected
    count=np.zeros((4326,4326),np.uint8)
    for r in range(4):
        for c in range(4):count[r*1024:r*1024+1254,c*1024:c*1024+1254]+=1
    assert np.array_equal(count,np.asarray(Image.open(frozen(a['coverage']['countMask']['file'],lock))))
    return masks
def verify_day(lock,s,a,c,masks):
    arrays={(n['row'],n['column']):math.load_rgb(frozen(n['file'],lock),n['sha256'],(1254,1254)) for n in s['dayNativeSources']}
    raw,_=math.assemble(arrays,masks)
    assert pngsha(raw)==c['baseline']['extendedSha256'] and pngsha(raw[115:4211,115:4211])==c['baseline']['sha256']
    fields={f['id']:f for f in c['fields']}
    def transform(left,right,alpha,label,orientation):
        z=np.load(frozen(fields[label]['differenceField'],lock));delta=z['correction_rgb_i16'].astype(np.int16)
        assert str(z['orientation'])==orientation and z['rect_extended_xywh'].tolist()==fields[label]['overlapRectExtendedXYWH']
        if orientation=='horizontal':delta=delta.transpose(1,0,2)
        result=math.blend(left,right,alpha).astype(np.int16)+delta
        assert result.min()>=0 and result.max()<=255
        # append_with_mask blends equal arrays, yielding the exact corrected overlap.
        return result.astype(np.uint8),result.astype(np.uint8),{'dayFieldReplayed':True}
    steps,_=math.assemble(arrays,masks,transform)
    expected_delta=np.clip(steps.astype(np.int16)-raw.astype(np.int16),-c['cap'],c['cap']);expected_delta[:243]=0
    z=np.load(frozen(c['finalCorrection']['file'],lock));delta=z['correction_rgb_i16']
    assert np.array_equal(delta,expected_delta)
    final=np.clip(raw.astype(np.int16)+delta,0,255).astype(np.uint8)
    assert np.array_equal(np.any(delta!=0,axis=2).astype(np.uint8),z['changed_mask_u8'])
    assert not np.any(delta[z['allowed_mask_u8']==0]) and not np.any(delta[:243])
    assert pngsha(final)==s['dayExtended']['sha256'] and pngsha(final[115:4211,115:4211])==s['dayFinal']['sha256']
    assert np.array_equal(final,math.load_rgb(frozen(s['dayExtended']['file'],lock),s['dayExtended']['sha256'],(4326,4326)))
    return {'dayRawPNGByteReplayExact':True,'dayAll15IntermediateRGBFieldReplayExact':True,'dayFinalRGBFieldExactlyReplayed':True,'dayFinalCorePNGByteReplayExact':True,'dayFinalExtendedPNGByteReplayExact':True,'dayFinalSHA256':s['dayFinal']['sha256'],'dayExtendedSHA256':s['dayExtended']['sha256'],'rawCoreSHA256':c['baseline']['sha256'],'rawExtendedSHA256':c['baseline']['extendedSha256'],'DAYColorFieldsAppliedToFestival':False}
def own_sources(s,partial=True):
    arrays={};evidence=[];missing=[]
    for n in s['dayNativeSources']:
        p=T/'native'/f"{n['id']}.png";rp=Path(str(p)+'.generation.json')
        if not p.exists() or not rp.exists():missing.append(n['id']);continue
        r=read(rp);assert Path(r['file']).resolve()==p.resolve() and [r['width'],r['height']]==[1254,1254]
        assert r['route']=='builtin' and r['resizedAfterGeneration'] is False and r.get('finalArtUpscaled') is False
        g=r['geometryMatchedTo'];assert g['dayAuthoritySha256']==g['sha256']==n['sha256'];assert key(g['dayAuthorityFile'])==key(n['file'])
        assert sha(g['file'])==g['sha256'] and sha(g['generationRecord'])==g['generationRecordSha256']
        refs=r['references'];submitted=r['submittedParameters'];assert len(refs)==len(submitted['referenced_image_paths'])
        for q,actual in zip(refs,submitted['referenced_image_paths']):assert key(q['file'])==key(actual) and sha(q['file'])==q['sha256']
        assert refs[0]['sha256']==n['sha256'];assert submitted['model'] is submitted['quality'] is None and r['actualModel'] is r['actualQuality'] is None
        assert sha(r['prompt'])==r['promptSha256'] and sha(r['requestFile'])==r['requestSha256']
        assert Path(r['prompt']).read_text('utf-8')==submitted['prompt']
        request=read(r['requestFile']);assert request['prompt']==submitted['prompt'] and request['referenced_image_paths']==submitted['referenced_image_paths']
        assert sha(r['evidence']['toolResultSourcePath'])==r['sha256']==r['evidence']['toolResultSha256']
        arrays[n['row'],n['column']]=math.load_rgb(p,r['sha256'],(1254,1254))
        evidence.append({'id':n['id'],**ref(p),'record':ref(rp),'dayGeometrySHA256':n['sha256'],'actualReferencesVerified':True,'rawToolBytesVerified':True,'actualModel':None,'actualQuality':None})
    if not partial:assert not missing,f'Missing recorded native: {missing}'
    return arrays,evidence,missing
