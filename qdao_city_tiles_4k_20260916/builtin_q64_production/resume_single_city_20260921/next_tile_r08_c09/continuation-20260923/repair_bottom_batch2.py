"""Second bounded bottom repair, maximum 3 native generations; only c09 changes."""
from pathlib import Path
import importlib.util, hashlib, json, sys
from datetime import datetime,timezone
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('first',HERE/'repair_bottom_batch1.py')
g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
require=g.require;info=g.info;write=g.write;read=g.read;sha=g.sha;load=g.load;now=g.now
BASE=HERE/'versions/bottom-material-v1-20260923T074753663242Z'
BATCH=HERE/'bottom-material-batch2-20260923'
SOURCE_SHA='534b82614f5b9dfbfd4441f8f6e10080668989bc11c2f560ed501bf12183ffbf'
RECORD_SHA='46cec1bf96325fc6cfe3fb1aac877b16143d85234104364db11c4610361b2c12'
PATCHES=[(1,0,0,1024,3768),(3,1933,2048,3072,3912),(4,2842,3072,4096,3768)]
def prepare():
    require(sha(BASE/'r08_c09.png')==SOURCE_SHA and sha(BASE/'repair.json')==RECORD_SHA,'Base changed')
    require(sha(g.NEIGHBOR)==g.NEIGHBOR_SHA and sha(g.STYLE)==g.STYLE_SHA,'Fixed reference changed')
    require(not BATCH.exists(),'Batch exists')
    BATCH.mkdir()
    before=load(BASE/'r08_c09.png',[4096,4096]);bottom=load(g.NEIGHBOR,[4096,4096]);config=read(g.PROJECT/'config/image-generation.json')
    write(BATCH/'config-snapshot.json',config)
    write(BATCH/'capability-check.json',{'checkedAtUtc':now(),'tool':'image_gen.imagegen','exposedParameters':['prompt','referenced_image_paths','num_last_images_to_include'],'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'sizeSelectorAvailable':False,'actualModel':None,'actualQuality':None,'configSnapshot':config,'apiCliUsed':False,'previousOfficialEvidence':info(HERE/'bottom-material-batch1-20260923/capability-check.json'),'evidenceSemantics':'Tool metadata rechecked this batch; previous same-session official web check does not prove builtin backend.'})
    entries=[]
    for i,x0,left,right,start in PATCHES:
        q=BATCH/f'patch-{i:02}';q.mkdir()
        context=np.concatenate([before[3469:,x0:x0+1254],bottom[:627,x0:x0+1254]],axis=0)
        Image.fromarray(context).save(q/'context-native-1254.png')
        yy=np.arange(1254,dtype=np.float32)[:,None]
        a=np.clip((yy-(start-3469))/24,0,1);a=a*a*(3-2*a);a[yy>=627]=0
        mask=np.repeat(np.rint(a*255).astype(np.uint8),1254,axis=1);Image.fromarray(mask).save(q/'mask.png')
        if i==3:
            instruction='This edit is focused on the narrow polished gold bevel where it crosses y=627 around x=477..497. Inspect the actual fixed lower-side bevel tangent and repaint only its upper-side meeting point to remove the tiny kink/step. Continue the exact curve with the same edge width and highlight, do not translate or warp the whole image. Preserve every other slab position and carving. Keep the existing clean restrained smooth materials. Do not invent veins or flakes.'
        else:
            instruction='The previous upper-side repair copied too much cloudy marbling from the lower neighbor. REMOVE that excess upper-side cloud and vein pattern now. Upper rows y=299..559 should return to the same smooth, broad, nearly featureless softly shaded painted stone as the clean upper region. In the final upper rows y=560..626 only, keep the MINIMUM sparse low-contrast tonal extensions required to meet the actual fixed lower edge; diminish irregular shapes quickly toward the clean upper area. Do not carry the lower stone veining upward across the whole band. The lower reference is authoritative for the contact edge and geometry only, not the texture style for the upper tile. The upper surface must read as a single clean light painted plane, not cloudy marble.'
        prompt=f'''Use case: precise-object-edit. Native 1254x1254 image edit, exact same crop, camera, composition and geometry. Edit IMAGE 1 ONLY. It is actual original pixels across r08_c09 bottom tile boundary. Top 627 rows belong to candidate c09, bottom 627 rows belong to immutable r09_c09. The artificial boundary is at y=627 and MUST NOT become a new horizontal stone line.
Preserve ALL pixels in lower half y>=627, and upper rows y<{start-3469}, as closely as the editing tool permits. Only upper y={start-3469}..626 may be repainted. Mechanical application will discard every generated pixel outside this band.
{instruction}
Every slab joint, relief outline, gold edge, highlight, shadow footprint and ring curve stays in its original place, except carefully repainting an existing bevel's upper-side connection if needed to meet the exact fixed lower tangent. Do not add objects, extra joints, decoration or text. No blur, soft-focus stripe, global recolor, grain, flaky noise, contour duplication or geometry-disguising feather. Return to unedited upper band invisibly using the same crisp painted finish.
IMAGE 2 is the approved designs reference for clean bright round Daoist Q/chibi painting finish ONLY. Do not import UI, characters or letters. IMAGE 3 is the original-pixel clean stone material reference, emphasize its quiet planes and restrained gradients. The full lower half of IMAGE 1 remains fixed. Return one opaque native square image, no labels, guides or collage.'''
        (q/'prompt.txt').write_text(prompt,encoding='utf-8',newline='')
        request={'prompt':prompt,'referenced_image_paths':[str(q/'context-native-1254.png'),str(g.STYLE),str(g.MATERIAL)]}
        write(q/'request.json',request)
        prep={'id':f'patch-{i:02}','createdAtUtc':now(),'source':info(BASE/'r08_c09.png'),'sourceRecord':info(BASE/'repair.json'),'neighbor':info(g.NEIGHBOR),'style':info(g.STYLE),'material':info(g.MATERIAL),'context':info(q/'context-native-1254.png'),'mask':info(q/'mask.png'),'worldBoxLTRB':[x0,3469,x0+1254,4723],'ownedCandidateXRange':[left,right],'allowedCandidateBandY':[start,4096],'nativePixels':[1254,1254],'trueBoundaryLocalY':627,'fixedLowerHalf':True,'referenceResized':False,'maskTopReturnPixels':24,'sideFeatherPixels':0,'bottomBoundaryFeatherPixels':0,'registration':'none','maximumAllowedShiftPixels':0,'configSnapshot':config,'request':info(q/'request.json'),'prompt':info(q/'prompt.txt'),'references':[info(p) for p in request['referenced_image_paths']],'formalAccepted':False}
        write(q/'prepared.json',prep);entries.append({'id':prep['id'],'prepared':info(q/'prepared.json'),'request':info(q/'request.json')})
    write(BATCH/'batch.json',{'patches':entries,'maximumNativeGenerations':3,'source':info(BASE/'r08_c09.png'),'neighbor':info(g.NEIGHBOR),'formalAccepted':False})
    print(json.dumps({'batch':str(BATCH),'patches':entries}))
def apply():
    require(sha(BASE/'r08_c09.png')==SOURCE_SHA and sha(BASE/'repair.json')==RECORD_SHA,'Source changed')
    before=load(BASE/'r08_c09.png',[4096,4096]);after=before.copy();fullmask=np.zeros((4096,4096),np.uint8);sources=[]
    for i,x0,left,right,start in PATCHES:
        q=BATCH/f'patch-{i:02}';p=read(q/'prepared.json');g.stable(p)
        for k in ['context','mask','request']:require(sha(p[k]['file'])==p[k]['sha256'],'Changed '+k)
        gen=read(q/'native-1254.png.generation.json');require(sha(q/'native-1254.png')==gen['sha256'],'Native changed')
        native=load(q/'native-1254.png',[1254,1254]);context=load(q/'context-native-1254.png',[1254,1254]);mask=np.array(Image.open(q/'mask.png'))
        require(not np.any(mask[627:]),'Neighbor mask nonzero')
        a=mask[:,:,None].astype(np.float32)/255;out=np.rint(context*(1-a)+native*a).astype(np.uint8)
        require(np.array_equal(out[mask==0],context[mask==0]),'Outside mask changed')
        l=left-x0;r=right-x0;require(np.array_equal(before[3469:,left:right],context[:627,l:r]),'Context mismatch')
        after[3469:,left:right]=out[:627,l:r];fullmask[3469:,left:right]=mask[:627,l:r]
        sources.append({'prepared':info(q/'prepared.json'),'native':info(q/'native-1254.png'),'generationRecord':info(q/'native-1254.png.generation.json'),'mask':info(q/'mask.png'),'ownedCandidateXRange':[left,right],'allowedCandidateBandY':[start,4096],'registration':'none','resampling':'none','colorCorrection':'none'})
    changed=np.any(before!=after,axis=2);require(not np.any(changed&(fullmask==0)),'Outside mask changed');require(sha(g.NEIGHBOR)==g.NEIGHBOR_SHA,'Neighbor changed')
    v=HERE/'versions'/('bottom-material-v2-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'));v.mkdir()
    Image.fromarray(after).save(v/'r08_c09.png');Image.fromarray(fullmask).save(v/'allowed-mask.png')
    rec={'schemaVersion':2,'createdAtUtc':now(),'status':'repair_candidate_pending_visual_review','tile':'r08_c09','candidate':info(v/'r08_c09.png'),'sourceCandidate':info(BASE/'r08_c09.png'),'sourceRecord':info(BASE/'repair.json'),'neighbor':info(g.NEIGHBOR),'sources':sources,'mask':info(v/'allowed-mask.png'),'changedPixels':int(changed.sum()),'outsideAllowedMaskPixelsUnchanged':True,'neighborCoreUnchanged':True,'sourceFileUnchanged':True,'allInternalJunctionsUnchanged':True,'nativeArtEnlarged':False,'registration':'none','resampling':'none','topReturnFeatherPixels':24,'actualModel':None,'actualQuality':None,'formalAccepted':False,'productionAccepted':False,'script':info(Path(__file__)),'helper':info(HERE/'repair_bottom_batch1.py')}
    write(v/'repair.json',rec)
    qa=v/'qa';qa.mkdir();items=[];bottom=load(g.NEIGHBOR,[4096,4096])
    def save(name,arr,kind,coords):
        f=qa/(name+'.png');Image.fromarray(arr).save(f);items.append({'id':name,**info(f),'kind':kind,'pixelScale':'1:1','coordinates':coords,'reviewed':False})
    for n in range(4):
        x=n*1024
        save(f'bottom-edge-{n+1:02}',np.concatenate([after[3968:,x:x+1024],bottom[:128,x:x+1024]],axis=0),'bottom_edge',{'xRange':[x,x+1024],'boundaryLocalY':4096})
        start=3912 if n==2 else 3768
        save(f'top-return-{n+1:02}',after[start-128:min(4096,start+160),x:x+1024],'top_return',{'xRange':[x,x+1024],'returnY':[start,start+24],'unchangedSegment':n==1})
    for n,x in enumerate([1024,2048,3072]):
        save(f'affected-vertical-{n+1:02}',after[3072:,x-128:x+128],'affected_internal_seam',{'x':x,'yRange':[3072,4096]})
        for y in [3780,3924]:
            save(f'return-junction-{n+1:02}-y{y}',after[y-128:min(4096,y+128),x-128:x+128],'repair_return_junction',{'centerXY':[x,y]})
    save('focus-gold-joint',np.concatenate([after[3904:,2304:2688],bottom[:192,2304:2688]],axis=0),'focus_bottom_edge',{'xRange':[2304,2688],'boundaryAtImageY':192})
    for n in [0,3]:
        x=n*1024
        save(f'wide-bottom-{n+1:02}',np.concatenate([after[3584:,x:x+1024],bottom[:512,x:x+1024]],axis=0),'wide_bottom_edge',{'xRange':[x,x+1024],'boundaryAtImageY':512})
    write(qa/'index.json',{'candidate':rec['candidate'],'repair':info(v/'repair.json'),'sourceReview':info(BASE/'visual-review.json'),'evidence':items,'formalAccepted':False,'internalUntouchedScopes':'Top area before y3768 unchanged; previous pending core-cut tonal questions remain pending.','otherExternalEdgesAndFourTileJunctions':'pending'})
    print(json.dumps({'version':str(v),'candidate':rec['candidate'],'repair':info(v/'repair.json'),'qa':str(qa/'index.json')}))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='ingest':g.BATCH=BATCH;g.ingest(sys.argv[2])
    elif sys.argv[1]=='apply':apply()
    else:raise ValueError('prepare|ingest|apply')

