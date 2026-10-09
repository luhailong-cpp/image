"""r09_c15 source preflight (partial allowed) and immutable raw/tone assembly."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from datetime import datetime, timezone
import argparse,json
import numpy as np
from PIL import Image
import contract as c
import shared_math as math
import tone_math as tone

T=c.T
def save(p,a,meta):
    p.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(a).save(p)
    info={**c.ref(p),'pixels':[a.shape[1],a.shape[0]]}
    c.dump(Path(str(p)+'.generation.json'),{**info,**meta,'generatedByAI':False,'actualModel':None,'actualQuality':None})
    return info
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--preflight',action='store_true');parser.add_argument('--build',action='store_true');args=parser.parse_args()
    lock,s,a,color=c.load_contract();masks=c.load_masks(lock,a);proof=c.verify_day(lock,s,a,color,masks)
    arrays,entries,missing=c.own_sources(s,partial=not args.build)
    report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceContract':c.ref(c.LOCK),'DAYReplay':proof,'ownNativeCount':len(entries),'missingNative':missing,'ownNativeSources':entries,'assemblyPixelOutputsWritten':False,'formalAccepted':False,'westNeighborKnown':False,'northQAReference':lock['northAuthority'],'paletteAuthorityAtGeneration':lock['historicalPaletteAuthority']}
    c.dump(T/'assembler/preflight.json',report)
    if not args.build:
        print(json.dumps({k:v for k,v in report.items() if k!='ownNativeSources'},ensure_ascii=False));return
    raw_dir=T/'shared-assembly/output';out=T/'tone-assembly/output';qa=T/'tone-assembly/qa';fields=T/'tone-assembly/fields'
    assert not (out/'tone-assembly-manifest.json').exists() and not (raw_dir/'shared-assembly-manifest.json').exists(),'Immutable outputs already exist'
    for p in (raw_dir,out,qa,fields):p.mkdir(parents=True,exist_ok=True)
    raw,operations=math.assemble(arrays,masks)
    common={'sourceContract':c.ref(c.LOCK),'DAYReplay':proof,'nativeSources':entries,'tile':'r09_c15','globalCoreXYWH':[57344,32768,4096,4096],'globalExtendedXYWH':[57229,32653,4326,4326],'haloPixels':115,'sourceResampled':False,'artUpscaled':False,'geometryWarped':False,'formalAccepted':False,'wholeCityComplete':False,'DAYWritten':False,'globalRegistryModified':False,'geometryRepairNativeRequired':0,'DAYRGBFieldsAppliedToFestival':False,'northQAReference':lock['northAuthority'],'historicalGenerationPaletteAuthority':lock['historicalPaletteAuthority'],'westNeighbor':None,'westUnknown':True}
    raw_ext=save(raw_dir/'extended-context.png',raw,{**common,'operation':'Exact frozen DAY alpha masks over corresponding festival native pixels','globalRectXYWH':common['globalExtendedXYWH']})
    raw_core=save(raw_dir/'r09_c15.png',raw[115:4211,115:4211],{**common,'operation':'Unresampled core crop of exact shared-mask raw','cropFromExtendedXYXY':[115,115,4211,4211],'globalRectXYWH':common['globalCoreXYWH']})
    c.dump(raw_dir/'shared-assembly-manifest.json',{**common,'candidate':raw_core,'extendedContext':raw_ext,'operations':operations,'status':'raw exact-mask baseline, not visually reviewed','script':c.ref(Path(__file__))})
    tone.FIELDS=fields
    rows=[];tone_ops=[]
    for row in range(1,5):
        merged=arrays[row,1].copy()
        for col in range(2,5):
            label=f'vertical_r{row:02}_c{col-1:02}_c{col:02}'
            merged,detail=tone.append(merged,arrays[row,col].copy(),masks[label],label,'vertical');tone_ops.append(detail)
        rows.append(merged)
    merged=rows[0]
    for row in range(2,5):
        label=f'horizontal_r{row-1:02}_r{row:02}'
        merged,detail=tone.append(merged,rows[row-1],masks[label],label,'horizontal');tone_ops.append(detail)
    delta=np.clip(merged.astype(np.int16)-raw.astype(np.int16),-24,24).astype(np.int8)
    final=(raw.astype(np.int16)+delta.astype(np.int16)).astype(np.uint8)
    support=np.zeros((4326,4326),bool)
    for boundary in (1024,2048,3072):
        support[:,boundary-256:boundary+230+256]=True;support[boundary-256:boundary+230+256,:]=True
    assert not np.any(delta[~support]) and int(np.abs(delta.astype(np.int16)).max())<=24
    fp=fields/'final-applied-delta-rgb.npz';np.savez_compressed(fp,delta_rgb=delta)
    maskp=fields/'final-applied-delta-mask.png';Image.fromarray(np.any(delta!=0,axis=2).astype(np.uint8)*255).save(maskp)
    tone_meta={**common,'operation':'New bounded RGB difference fields computed only from festival native overlaps; frozen DAY alpha ownership reused','maximumFinalChannelChange':int(np.abs(delta.astype(np.int16)).max()),'maximumPermittedFinalChannelChange':24,'perStepChannelLimit':18,'imageBlur':False,'outsideLocalSeamSupportExactlyPreserved':True,'finalAppliedCorrectionField':c.ref(fp),'actualCorrectionMask':c.ref(maskp),'sharedBaselineManifest':c.ref(raw_dir/'shared-assembly-manifest.json'),'operations':tone_ops,'visualReview':'pending'}
    ext=save(out/'extended-context.png',final,{**tone_meta,'globalRectXYWH':common['globalExtendedXYWH']})
    core=final[115:4211,115:4211]
    candidate=save(out/'r09_c15.png',core,{**tone_meta,'globalRectXYWH':common['globalCoreXYWH'],'cropFromExtendedXYXY':[115,115,4211,4211]})
    assert np.array_equal(math.load_rgb(ext['file'],ext['sha256'],(4326,4326)).astype(np.int16),raw.astype(np.int16)+np.load(fp)['delta_rgb'].astype(np.int16))
    q=[]
    def crop(label,rect):
        x0,y0,x1,y1=rect
        q.append({'id':label,**save(qa/f'{label}.png',core[y0:y1,x0:x1],{'operation':'exact native-pixel QA crop','source':candidate,'sourceCropXYXY':rect,'resized':False,'visualReview':'pending'}),'coreRectXYXY':rect})
    for axis in ('x','y'):
        for boundary in (1024,2048,3072):
            for part in range(4):
                rect=[boundary-448,part*1024,boundary+448,(part+1)*1024] if axis=='x' else [part*1024,boundary-448,(part+1)*1024,boundary+448]
                crop(f'{axis}{boundary}-return-part{part+1:02}',rect)
    for x in (1024,2048,3072):
        for y in (1024,2048,3072):crop(f'junction-x{x}-y{y}',[x-256,y-256,x+256,y+256])
    for name,rect in [('nw',[0,0,512,512]),('ne',[3584,0,4096,512]),('sw',[0,3584,512,4096]),('se',[3584,3584,4096,4096])]:crop(f'corner-{name}',rect)
    north=math.load_rgb(c.frozen(lock['northAuthority']['file'],lock),lock['northAuthority']['sha256'],(4096,4096))
    for part in range(4):
        x0,x1=part*1024,(part+1)*1024
        adjacent=np.concatenate((north[-256:,x0:x1],core[:256,x0:x1]),axis=0)
        q.append({'id':f'north-adjacent-part{part+1:02}',**save(qa/f'north-adjacent-part{part+1:02}.png',adjacent,{'operation':'true north/candidate adjacent pixel strips','northSource':lock['northAuthority'],'candidateSource':candidate,'northCropXYXY':[x0,3840,x1,4096],'candidateCropXYXY':[x0,0,x1,256],'resized':False,'visualReview':'pending'})})
        matching=np.concatenate((north[-115:,x0:x1],final[:115,115+x0:115+x1]),axis=0)
        q.append({'id':f'north-same-coordinate-halo-part{part+1:02}',**save(qa/f'north-same-coordinate-halo-part{part+1:02}.png',matching,{'operation':'top115 true north pixels and bottom115 candidate halo at identical global coordinates','northSource':lock['northAuthority'],'candidateExtendedSource':ext,'resized':False,'visualReview':'pending'})})
    manifest={**tone_meta,'candidate':candidate,'extendedContext':ext,'qa':q,'qaCoverage':{'internalReturnSegments':24,'junctions':9,'corners':4,'northAdjacentSegments':4,'northSameCoordinateHaloPairs':4,'westQAProvided':False},'savedExtendedPixelsExactlyEqualRawPlusRecordedDelta':True,'script':c.ref(Path(__file__)),'algorithmProvenance':c.ref(T/'assembler/algorithm-provenance.json'),'reportedNativeQAFlags':c.ref(T/'assembler/reported-native-qa-flags.json'),'status':'complete native pixel candidate, actual QA pending'}
    for n in entries:assert c.sha(n['file'])==n['sha256']
    c.dump(out/'tone-assembly-manifest.json',manifest)
    print(json.dumps({'candidate':candidate,'extendedContext':ext,'manifest':c.ref(out/'tone-assembly-manifest.json'),'qaCount':len(q),'maxRGBDelta':tone_meta['maximumFinalChannelChange']},ensure_ascii=False))
if __name__=='__main__':main()
