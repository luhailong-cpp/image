"""One four-native-image bottom material repair; no shared-state updates."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, shutil, sys
import numpy as np
from PIL import Image

HERE=Path(__file__).resolve().parent
TILE=HERE.parent
SESSION=TILE.parent
PROJECT=TILE.parents[3]
BASE=HERE/'versions/hard-core-20260923T070734660600Z'
BATCH=HERE/'bottom-material-batch1-20260923'
NEIGHBOR=SESSION/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png'
STYLE=PROJECT/'designs/gameplay-ui/04-guild.png'
MATERIAL=TILE/'references/clean-stone-material-native-crop.png'
SOURCE_SHA='a02bfaed46979a0a2900be3b85a4a1ef11d4aae76fee148bf961165609a7d645'
ASSEMBLY_SHA='c5e7836db6d66a0b62eb1805b748f9c2bd6a7154931bc1cd6fd4eed57a803b5b'
NEIGHBOR_SHA='5ce3e9099c4292a3c2d2b854bcc6d2cfd3b8858bb6960bc8e7966699ade4742c'
STYLE_SHA='85d0c8260237fb6381d6c54005d5f2ac9f4b065a16d318e3e12e6498312a40a6'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
now=lambda:datetime.now(timezone.utc).isoformat()
def require(x,m):
    if not x:raise ValueError(m)
def info(p):return {'file':str(Path(p).resolve()),'sha256':sha(p)}
def write(p,v):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load(p,size):
    with Image.open(p) as im:
        im.load();require(im.format=='PNG' and im.size==tuple(size),'Unexpected PNG '+str(p))
        require(im.mode in ['RGB','RGBA'],'Unexpected image mode')
        if im.mode=='RGBA':require(im.getextrema()[3]==(255,255),'Transparency forbidden')
        return np.array(im.convert('RGB'))
def stable(prep):
    for key in ['source','sourceRecord','neighbor','style','material']:
        b=prep[key];require(sha(b['file'])==b['sha256'],'Input changed '+key)

def prepare():
    require(sha(BASE/'r08_c09.png')==SOURCE_SHA and sha(BASE/'assembly.json')==ASSEMBLY_SHA,'Base changed')
    require(sha(NEIGHBOR)==NEIGHBOR_SHA and sha(STYLE)==STYLE_SHA,'Fixed reference changed')
    require(not BATCH.exists(),'Batch already exists')
    BATCH.mkdir()
    before=load(BASE/'r08_c09.png',[4096,4096]);bottom=load(NEIGHBOR,[4096,4096])
    config=read(PROJECT/'config/image-generation.json')
    schema={'checkedAtUtc':now(),'tool':'image_gen.imagegen','exposedParameters':['prompt','referenced_image_paths','num_last_images_to_include'],
      'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'sizeSelectorAvailable':False,
      'actualModel':None,'actualQuality':None,'configSnapshot':config,
      'officialSourcesRead':['https://openai.com/index/introducing-chatgpt-images-2-5/','https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst'],
      'officialFindings':'Images 2.5 is available in Codex; Sunburst API lists max quality. These facts do not prove any specific builtin backend.',
      'apiCliUsed':False}
    write(BATCH/'capability-check.json',schema)
    write(BATCH/'config-snapshot.json',config)
    # Each 1024-wide ownership interval has real 1:1 surrounding context.
    # Edge contexts are inset to avoid inventing unavailable side-neighbor pixels.
    entries=[]
    for i,x0 in enumerate([0,909,1933,2842]):
        q=BATCH/f'patch-{i+1:02}';q.mkdir()
        context=np.concatenate([before[3469:,x0:x0+1254],bottom[:627,x0:x0+1254]],axis=0)
        Image.fromarray(context).save(q/'context-native-1254.png')
        yy=np.arange(1254,dtype=np.float32)[:,None]
        # A 32px top-only material return. No geometric warping or image blur.
        a=np.clip((yy-(3768-3469))/32,0,1);a=a*a*(3-2*a);a[yy>=627]=0
        mask=np.repeat(np.rint(a*255).astype(np.uint8),1254,axis=1)
        Image.fromarray(mask).save(q/'mask.png')
        prompt=f'''Use case: precise-object-edit. Edit IMAGE 1 ONLY, exact original native 1254 x 1254 pixels, same crop, camera, scale, paving geometry and lighting. This is bottom-edge repair {i+1}/4 of Tianyong city tile r08_c09. The horizontal line y=627 is an artificial tile boundary, not a stone joint. IMAGE 1 contains 627 rows of the new upper tile and 627 rows of the actual fixed lower neighboring tile. The ENTIRE lower half y>=627 is immutable existing artwork: reproduce it unchanged, do not clean it, recolor it, shift it, draw through it, or alter any geometry. Also leave upper rows y<299 unchanged.
Repair ONLY material continuity in the upper strip y=299..626. Eliminate the straight horizontal material jump at y=627 by repainting a natural, restrained transition in the upper side. At the boundary continue the existing lower-half broad cream/gold/slate tonal shapes into the upper side, gently simplify them into the clean upper surface within the upper strip. Keep the full actual lower context unchanged. Do not spread dense flakes, veins, stipple or cloudy mottling into the clean upper tile; preserve its smooth premium hand-painted Q/chibi stone planes. The upper strip must meet both its unedited upper return and the actual lower neighbor without any rectangular color band.
Every carved outline, slab division, bevel edge, highlight path, shadow footprint and ring curvature must keep its exact original position. This is a MATERIAL-ONLY repair, not a geometric redesign. No extra lines, duplicate joints, stair steps, props, vegetation, decorations, lettering or interface. No whole-image color shift. No blur, soft-focus band, feathered fake seam, sharpen halo, noisy stone grain or invented marbling.
IMAGE 2 is the user-confirmed designs style reference: its clean bright rounded refined painting/material finish ONLY. Never import its UI, text, characters, symbols or layout. IMAGE 3 is the existing clean original-pixel stone material reference ONLY. The exact bottom boundary colors and structures remain governed by IMAGE 1's fixed lower half. Output only the single opaque native square terrain image, no collage or border.'''
        (q/'prompt.txt').write_text(prompt,encoding='utf-8',newline='')
        request={'prompt':prompt,'referenced_image_paths':[str(q/'context-native-1254.png'),str(STYLE),str(MATERIAL)]}
        write(q/'request.json',request)
        prep={'id':f'patch-{i+1:02}','createdAtUtc':now(),'source':info(BASE/'r08_c09.png'),'sourceRecord':info(BASE/'assembly.json'),
          'neighbor':info(NEIGHBOR),'style':info(STYLE),'material':info(MATERIAL),'context':info(q/'context-native-1254.png'),'mask':info(q/'mask.png'),
          'worldBoxLTRB':[x0,3469,x0+1254,4723],'ownedCandidateXRange':[i*1024,(i+1)*1024],'allowedCandidateBandY':[3768,4096],
          'nativePixels':[1254,1254],'trueBoundaryLocalY':627,'fixedLowerHalf':True,'referenceResized':False,
          'maskTopReturnPixels':32,'sideFeatherPixels':0,'bottomBoundaryFeatherPixels':0,'registration':'none','maximumAllowedShiftPixels':0,
          'configSnapshot':config,'request':info(q/'request.json'),'prompt':info(q/'prompt.txt'),
          'references':[info(p) for p in request['referenced_image_paths']],'formalAccepted':False}
        write(q/'prepared.json',prep);entries.append({'id':prep['id'],'prepared':info(q/'prepared.json'),'request':info(q/'request.json')})
    write(BATCH/'batch.json',{'patches':entries,'maximumNativeGenerations':4,'source':info(BASE/'r08_c09.png'),'neighbor':info(NEIGHBOR),'formalAccepted':False})
    print(json.dumps({'batch':str(BATCH),'patches':entries},ensure_ascii=False))

def ingest(ident):
    q=BATCH/ident;prep=read(q/'prepared.json');stable(prep)
    receipt=read(q/'receipt.json');require(receipt['request']==read(q/'request.json'),'Actual request mismatch')
    require(sha(q/'request.json')==prep['request']['sha256'],'Request bytes changed')
    for ref in prep['references']:require(sha(ref['file'])==ref['sha256'],'Reference changed')
    match=re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.S)
    require(match is not None,'Missing tool output path');raw=Path(match.group(1));load(raw,[1254,1254])
    dst=q/'native-1254.png';require(not dst.exists(),'Native already saved');shutil.copyfile(raw,dst)
    require(sha(raw)==sha(dst),'Native copy differs')
    gen={'schemaVersion':1,**info(dst),'width':1254,'height':1254,'format':'PNG','generatedAt':None,
      'observedCompletionAt':receipt['completedAtUtc'],'timestampSemantics':'clock tool UTC after completion; server generation time undisclosed',
      'tool':'image_gen.imagegen','route':'builtin','configSnapshot':prep['configSnapshot'],'submittedParameters':{'model':None,'quality':None},
      'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Host-managed tool has no model/quality selector and disclosed no verified model/quality metadata',
      'prompt':prep['prompt'],'references':prep['references'],'request':prep['request'],'evidence':info(q/'receipt.json'),'editBefore':prep['context'],
      'originalNativeOutput':info(raw),'resized':False,'upscaled':False,'rawBytesPreserved':True,'formalAccepted':False}
    write(q/'native-1254.png.generation.json',gen);print(json.dumps(gen,ensure_ascii=False))

def apply():
    before=load(BASE/'r08_c09.png',[4096,4096]);after=before.copy();sources=[]
    require(sha(BASE/'r08_c09.png')==SOURCE_SHA and sha(NEIGHBOR)==NEIGHBOR_SHA,'Base/neighbor changed')
    fullmask=np.zeros((4096,4096),np.uint8)
    for i in range(4):
        q=BATCH/f'patch-{i+1:02}';p=read(q/'prepared.json');stable(p)
        for key in ['context','mask','request']:require(sha(p[key]['file'])==p[key]['sha256'],'Prepared '+key+' changed')
        gen=read(q/'native-1254.png.generation.json');require(sha(q/'native-1254.png')==gen['sha256'],'Native changed')
        native=load(q/'native-1254.png',[1254,1254]);context=load(q/'context-native-1254.png',[1254,1254])
        mask=np.array(Image.open(q/'mask.png'));require(not np.any(mask[627:]),'Mask enters fixed neighbor')
        alpha=mask[:,:,None].astype(np.float32)/255
        result=np.rint(context*(1-alpha)+native*alpha).astype(np.uint8)
        require(np.array_equal(result[mask==0],context[mask==0]),'Outside mask changed')
        require(np.array_equal(result[627:],context[627:]),'Neighbor half changed')
        x0=p['worldBoxLTRB'][0];left,right=p['ownedCandidateXRange'];l=left-x0;r=right-x0
        require(np.array_equal(before[3469:,left:right],context[:627,l:r]),'Context/base differs')
        after[3469:,left:right]=result[:627,l:r];fullmask[3469:,left:right]=mask[:627,l:r]
        sources.append({'prepared':info(q/'prepared.json'),'native':info(q/'native-1254.png'),'generationRecord':info(q/'native-1254.png.generation.json'),
          'ownedCandidateXRange':[left,right],'nativeOwnedXRange':[l,r],'mask':info(q/'mask.png'),'registration':'none','shiftPixels':[0,0],'colorCorrection':'none'})
    changed=np.any(before!=after,axis=2)
    require(not np.any(changed & (fullmask==0)),'Pixels outside authorized mask changed')
    require(np.array_equal(before[:3768],after[:3768]),'Upper candidate changed')
    require(sha(NEIGHBOR)==NEIGHBOR_SHA,'Neighbor file changed')
    version=HERE/'versions'/('bottom-material-v1-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
    version.mkdir();Image.fromarray(after).save(version/'r08_c09.png');Image.fromarray(fullmask).save(version/'allowed-mask.png')
    rec={'schemaVersion':1,'createdAtUtc':now(),'status':'repair_candidate_pending_visual_review','tile':'r08_c09','candidate':info(version/'r08_c09.png'),
      'sourceCandidate':info(BASE/'r08_c09.png'),'sourceRecord':info(BASE/'assembly.json'),'neighbor':info(NEIGHBOR),'sources':sources,
      'mask':info(version/'allowed-mask.png'),'allowedCandidateBandY':[3768,4096],'changedPixels':int(changed.sum()),
      'outsideAllowedMaskPixelsUnchanged':True,'neighborCoreUnchanged':True,'sourceFileUnchanged':True,'allInternalJunctionsUnchanged':True,
      'nativeArtEnlarged':False,'registration':'none','resampling':'none','topReturnFeatherPixels':32,'patchOwnershipCutsX':[1024,2048,3072],
      'mechanicalScope':'Native AI pixels only. 32-pixel upper material return; no geometric registration or image blur. Review required.',
      'actualModel':None,'actualQuality':None,'formalAccepted':False,'productionAccepted':False,'script':info(Path(__file__))}
    write(version/'repair.json',rec)
    qa=version/'qa';qa.mkdir();items=[];bottom=load(NEIGHBOR,[4096,4096])
    def save(name,array,kind,box):
        f=qa/(name+'.png');Image.fromarray(array).save(f);items.append({'id':name,**info(f),'kind':kind,'pixelScale':'1:1','coordinates':box,'reviewed':False})
    for s in range(4):
        x=s*1024
        save(f'bottom-edge-{s+1:02}',np.concatenate([after[3968:,x:x+1024],bottom[:128,x:x+1024]],axis=0),'bottom_edge',{'xRange':[x,x+1024],'boundaryLocalY':4096})
        save(f'top-return-{s+1:02}',after[3640:3928,x:x+1024],'top_return',{'boxLTRB':[x,3640,x+1024,3928],'returnY':[3768,3800]})
    for c in range(1,4):
        x=c*1024
        save(f'affected-vertical-{c:02}',after[3072:,x-128:x+128],'affected_internal_seam',{'x':x,'yRange':[3072,4096]})
        save(f'return-junction-{c:02}',after[3656:3912,x-128:x+128],'repair_return_junction',{'centerXY':[x,3784]})
    write(qa/'index.json',{'candidate':info(version/'r08_c09.png'),'repair':info(version/'repair.json'),'evidence':items,
      'unchangedInheritedScope':{'sourceReview':info(BASE/'visual-review.json'),'internalHorizontalSeams':[1024,2048,3072],'internalJunctions':9,'pixelEqualityVerified':True},
      'otherEdges':'pending neighboring cores and inspection','externalFourTileJunctions':'pending','formalAccepted':False})
    print(json.dumps({'version':str(version),'candidate':rec['candidate'],'repair':info(version/'repair.json'),'qa':str(qa/'index.json')},ensure_ascii=False))

if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='ingest':ingest(sys.argv[2])
    elif sys.argv[1]=='apply':apply()
    else:raise ValueError('prepare|ingest|apply')
