"""Replay c14 DAY seam ownership with native festival edits and bounded RGB fields.

Only own r08_c14/west-final is written. There is no generation, registration,
resampling, automatic acceptance, state mutation, or publication in this script.
"""
from pathlib import Path
from datetime import datetime, timezone
import sys
sys.dont_write_bytecode = True
import json
import shutil
import numpy as np
from PIL import Image
import compose_west as cw
import finish_west as fw

ROOT = Path(__file__).resolve().parent
DEST = ROOT/'r08_c14/west-final'
OUT, QA, FIELDS = DEST/'output', DEST/'qa', DEST/'fields'
DAY_MANIFEST = ROOT.parent/'donghai_day/tiles/west-integration-r08_c14-manifest.json'
BASES = [
 ('r08_c13',ROOT/'r08_c13/completed-candidate-v2/output/r08_c13.png','bd2ccf25c06f3e22797cd153c26df45247ee9d099adb8d191a72d282cb78b1c6'),
 ('r08_c14',Path(cw.read(ROOT/'r08_c14/repairs/west-common-edge/final-base.json')['file']),cw.read(ROOT/'r08_c14/repairs/west-common-edge/final-base.json')['sha256']),
]

def setup():
    cw.TILE=ROOT/'r08_c14';cw.NATIVE=cw.TILE/'repairs/west-common-edge/native'
    cw.DEST,cw.OUT,cw.QA,cw.MASKS=DEST,OUT,QA,DEST/'masks'
    cw.ORIGIN=(49152,28672)
    cw.DAY_MANIFEST=DAY_MANIFEST
    source_contract=cw.read(cw.TILE/'repairs/west-common-edge/source-contract.json')
    cw.DAY_MANIFEST_SHA=source_contract['dayManifest']['sha256']
    cw.check(DAY_MANIFEST,cw.DAY_MANIFEST_SHA)
    cw.EXPECTED_PARAMETERS=cw.read(DAY_MANIFEST)['parameters']
    expected={'pairPixels':[8192,4096],'stripPairRectXYXY':[3469,0,4723,4096],
      'patchYStarts':[0,1024,2048,2842],'longitudinalOverlaps':[230,230,460],
      'insertionOverlapEachSidePixels':150,'transitionWidthPixels':2,
      'registration':False,'colorCorrection':False,'imageBlur':False,'maskBlur':False,
      'resampling':False,'noUpscaling':True}
    cw.require(cw.EXPECTED_PARAMETERS==expected,'Unexpected DAY c14 geometry contract')
    tone=source_contract['festivalBaselines'][1]
    cw.check(tone['file'],tone['sha256'])
    cw.check(BASES[1][1],BASES[1][2])
    cw.require(np.array_equal(cw.rgb(tone['file'],(4096,4096))[:,:627],cw.rgb(BASES[1][1],(4096,4096))[:,:627]),'Final c14 west context differs from submitted tone base')
    fw.DEST,fw.OUT,fw.QA,fw.FIELDS=DEST,OUT,QA,FIELDS

def load_inputs(day):
    baselines=[];pixels=[]
    for tile,path,digest in BASES:
        cw.check(path,digest)
        rec=Path(str(path)+'.generation.json');r=cw.read(rec)
        cw.require(r['sha256']==digest,'Baseline record/pixels disagree')
        baselines.append({'tile':tile,**cw.info(path),'generationRecord':cw.info(rec)})
        pixels.append(cw.rgb(path,(4096,4096)))
    cleanup_path=ROOT/'audit/duplicate-cache-cleanup.json'
    cleanup=cw.read(cleanup_path)
    geometry={p['id']:p for p in day['nativeRepairSources']}
    patches=[];sources=[]
    for i,y in enumerate(cw.STARTS,1):
        name=f's{i}';path=cw.NATIVE/(name+'.png');rec=Path(str(path)+'.generation.json');r=cw.read(rec)
        cw.check(path,r['sha256']);cw.require(cw.same(path,r['file']),'Native path binding differs')
        cw.require(r['route']=='builtin' and r['tool']=='image_gen.imagegen','Wrong generation route')
        cw.require([r['width'],r['height']]==[1254,1254] and r['resizedAfterGeneration'] is False and r['finalArtUpscaled'] is False,'Source resampled')
        cw.require(r['globalRectXYWH']==[52621,28672+y,1254,1254],'Wrong source geometry coordinates')
        refs=r['references'];sub=r['submittedParameters']
        cw.require(len(refs)==len(sub['referenced_image_paths']),'Reference count differs')
        for ref,submitted in zip(refs,sub['referenced_image_paths']):
            cw.require(cw.same(ref['file'],submitted),'Reference order differs');cw.check(ref['file'],ref['sha256'])
        g=geometry[name];cw.check(g['file'],g['sha256'])
        cw.require(cw.same(refs[0]['file'],g['file']) and refs[0]['sha256']==g['sha256'],'Wrong primary DAY geometry')
        cw.require(r['geometryMatchedTo']['sha256']==g['sha256'],'Geometry binding differs')
        cw.require(all(sub.get(k,'missing') is None for k in ('model','quality')) and all(r.get(k,'missing') is None for k in ('actualModel','actualQuality')),'Unsupported model lock claim')
        cw.check(r['prompt'],r['promptSha256']);cw.check(r['requestFile'],r['requestSha256'])
        cw.require(Path(r['prompt']).read_text(encoding='utf-8-sig').strip()==sub['prompt'].strip(),'Prompt changed')
        ev=r['evidence'];cw.require(ev['toolResultSha256']==r['sha256'],'Tool/native digest differs')
        raw=Path(ev['toolResultSourcePath'])
        if raw.is_file():
            cw.check(raw,r['sha256']);tool={'file':str(raw),'sha256':r['sha256'],'cacheAvailable':True}
        else:
            entries=[e for e in cleanup['entries'] if cw.same(e['nativeFile'],path) and cw.same(e['originalToolResultSourcePath'],raw)]
            cw.require(len(entries)==1,'Deleted raw has no cleanup proof');proof=entries[0]
            cw.require(proof['status']=='deleted' and proof['verifiedCacheSha256']==proof['retainedNativeSha256AfterDeletion']==r['sha256'],'Cleanup does not prove byte identity')
            tool={'file':str(raw),'sha256':r['sha256'],'cacheAvailable':False,'availability':'authorized-byte-identical-cache-deletion','retainedNative':cw.info(path),'cleanupProof':cw.info(cleanup_path)}
        sources.append({'id':name,**cw.info(path),'record':cw.info(rec),'toolResult':tool,'references':refs,
          'dayGeometry':{'file':g['file'],'sha256':g['sha256']},'pairRectXYXY':[3469,y,4723,y+1254],
          'submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None,'sourceResampled':False})
        patches.append(cw.rgb(path,(1254,1254)))
    return np.concatenate(pixels,axis=1),baselines,patches,sources

def make_qa(result,outputs):
    image=Image.fromarray(result);items=[]
    def crop(name,box,**extra):
        meta={'derivedFrom':outputs,'pairRectXYXY':list(box),'pixelScale':1,'visualReview':'pending',**extra}
        items.append({**cw.save_image(QA/(name+'.png'),image.crop(box),meta),**meta})
    for name,center in (('common-edge',4096),('attachment-left',3544),('attachment-right',4648)):
        for part in range(4):
            width=512 if name=='common-edge' else 896
            crop(f'{name}-return-part{part+1:02}',[center-width//2,part*1024,center+width//2,(part+1)*1024],coversFullCorrectionReturn=name!='common-edge')
    for i,y in enumerate(cw.STARTS[1:],1):
        overlap=230 if i<3 else 460
        crop(f'longitudinal-{i}-return',[cw.X0,y-fw.RADIUS,cw.X1,min(cw.H,y+overlap+fw.RADIUS)],coversFullCorrectionReturn=True)
    for name,x in (('left',cw.X0),('right',cw.X1)):
        crop('corner-'+name+'-top',[x-256,0,x+256,512])
        crop('corner-'+name+'-bottom',[x-256,3584,x+256,4096])
    crop('attachment-top-full',[cw.X0,0,cw.X1,256],outerNeighborPresent=False)
    crop('attachment-bottom-full',[cw.X0,3840,cw.X1,4096],outerNeighborPresent=False)
    return items

def main():
    setup()
    day,contract,masks,seams=cw.load_day_contract()
    base,baselines,patches,sources=load_inputs(day)
    original=cw.compose(base,patches,masks)
    result,reports,final_field=fw.matched_four(base,patches,masks,original)
    delta=result[:,3469:4723].astype(np.int16)-original[:,3469:4723].astype(np.int16)
    cw.require(np.abs(delta).max()<=24,'Tone field exceeds bound')
    cw.require(np.array_equal(result[:,:3469],base[:,:3469]) and np.array_equal(result[:,4723:],base[:,4723:]),'Pixels escaped authorized common-edge strip')
    with np.load(final_field['field']['file']) as archive:
        replay=original[:,3469:4723].astype(np.int16)+archive['delta_rgb'].astype(np.int16)
        cw.require(np.array_equal(replay,result[:,3469:4723]),'Saved final correction field does not replay pixels')
    for seam in seams:
        for source_key,dest_key,suffix in (('sourceMaskNpz','appliedMaskNpz','npz'),('sourceMaskPng','appliedMaskPng','png')):
            src=seam[source_key];dest=cw.MASKS/(seam['id']+'.'+suffix)
            shutil.copyfile(src['file'],cw.writable(dest));cw.check(dest,src['sha256']);seam[dest_key]=cw.info(dest)
        cw.save_json(cw.MASKS/(seam['id']+'.json'),seam)
    dependencies=baselines+sources
    common={'derivedFrom':dependencies,'dayGeometryContract':contract,'daySeams':seams,'colorCorrection':True,
      'colorCorrectionField':final_field,'geometryFlow':False,'spatialResampling':False,'formalAccepted':False,'visualReview':'pending'}
    outputs=[]
    for name,pixels,rect in (('pair-r08_c13-c14',result,[0,0,8192,4096]),('r08_c13',result[:,:4096],[0,0,4096,4096]),('r08_c14',result[:,4096:],[4096,0,8192,4096])):
        saved=cw.save_image(OUT/(name+'.png'),pixels,{**common,'pairRectXYXY':rect,'globalOriginXY':[49152,28672]})
        cw.require(np.array_equal(cw.rgb(saved['file'],(pixels.shape[1],pixels.shape[0])),pixels),'Saved pixels differ')
        outputs.append({'id':name,**saved})
    preview=cw.save_image(OUT/'preview-1024.png',Image.fromarray(result).resize((1024,512),Image.Resampling.LANCZOS),{'derivedFrom':outputs[:1],'operation':'Downscaled overview only','resized':True,'finalArt':False,'notNativePixelQA':True})
    qa=make_qa(result,outputs)
    for src in dependencies:cw.check(src['file'],src['sha256'])
    manifest={**common,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'script':cw.info(__file__),
      'sharedCode':[cw.info(cw.__file__),cw.info(fw.__file__)],'status':'complete-pixel-candidates-pending-native-visual-review',
      'outputs':outputs,'preview':preview,'qa':qa,'toneOperations':reports,'parameters':cw.EXPECTED_PARAMETERS,
      'toneParameters':{'perLongitudinalSourceStepMax':18,'perInsertionStepMax':24,'maximumFinalChannelDelta':24,'falloffRadius':256,'differenceFieldSmoothing':'3 box passes radius12 on difference field only; artwork unblurred'},
      'pixelVerification':{'outsideRepairExactlyIdentical':True,'outsideRepairChangedPixels':0,'authorizedPairRectXYXY':[3469,0,4723,4096],
        'c13West3469ColumnsExactlyPreserved':True,'c14East3469ColumnsExactlyPreserved':True,
        'savedPngPixelsMatchComputed':True,'finalDeltaFieldExactlyReplaysPixels':True,'maximumToneChannelDelta':int(np.abs(delta).max())},
      'sourcePngBytesUnchanged':True,'globalStateModified':False,'wholeCityComplete':False,'clientAcceptance':False,
      'qaCoverage':{'commonEdgeLength':4096,'leftAndRightAttachmentLength':4096,'correctionReturns':True,'longitudinalReturns':3,'corners':4,'outerNorthSouthNeighborSupplied':False,'pixelScale':1,'visualReview':'pending'}}
    cw.save_json(OUT/'west-final-manifest.json',manifest)
    print(json.dumps({'outputs':outputs,'qaCount':len(qa),'maximumToneChannelDelta':int(np.abs(delta).max()),'manifest':str(OUT/'west-final-manifest.json')},indent=2))

if __name__=='__main__':main()

