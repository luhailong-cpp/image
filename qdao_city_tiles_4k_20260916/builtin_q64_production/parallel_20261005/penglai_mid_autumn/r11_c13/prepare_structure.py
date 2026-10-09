"""R11 C13 planning only. Writes stay in this tile; never generates native art."""
from pathlib import Path
import sys,json,hashlib,shutil,datetime
sys.dont_write_bytecode=True
from PIL import Image,ImageChops
F=Path(__file__).resolve().parent; ROOT=F.parent; REPO=Path('D:/work/image')
R=F/'references'; Q=F/'qa'; E=F/'evidence'
X,Y,H,S=49152,40960,320,4736
FRAME=[X-H,Y-H,S,S]
N=ROOT/'r10_c13/output/r10_c13-candidate.png'
NSHA='c6c7176ea72228aca772c78a17fe8e3b5fc699904f46205d62ae482f420d1a5b'
DAY=ROOT.parent/'penglai_day/r11_c13/references/structure.png'
DAY_SHA='e28b8946b0a67445cb9c7fdf563ad6bb0fe6da6ae558fe07ed245eea607cd074'
STYLE=REPO/'designs/gameplay-ui/04-guild.png'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
    p=Path(p);assert p.resolve().is_relative_to(F.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def ref(p,**kw):return dict(file=str(p),sha256=sha(p),**kw)
def image_save(im,p,sources,operation):
    p=Path(p);assert p.resolve().is_relative_to(F.resolve());assert not p.exists(),p
    p.parent.mkdir(parents=True,exist_ok=True);im.save(p)
    write(str(p)+'.generation.json',dict(file=str(p),sha256=sha(p),createdAt=now(),width=im.width,height=im.height,derivedFrom=[ref(s) for s in sources],operation=operation,productionPixels=False,formalAccepted=False))
def layout(ap):return REPO/f'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/{ap}/map-native-layout-reference.png'
def crop_layout(p,frame,size):
    im=Image.open(p).convert('RGB');k=im.width/65536; x,y,w,h=frame
    return im.transform(size,Image.Transform.EXTENT,[x*k,y*k,(x+w)*k,(y+h)*k],Image.Resampling.BICUBIC)
def setup():
    assert sha(N)==NSHA and sha(DAY)==DAY_SHA
    for d in [R,Q,E,F/'guides']:d.mkdir(parents=True,exist_ok=True)
    write(E/'day-structure-source-history.json',read(str(DAY)+'.generation.json'))
    write(E/'model-verification.json',dict(checkedAt=now(),configSnapshot=read(REPO/'config/image-generation.json'),officialRelease='https://openai.com/index/introducing-chatgpt-images-2-5/',officialModel='https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst',observed='Official model page identifies GPT Image 2.5 Sunburst as most capable; supports max quality. Release lists ChatGPT, ChatGPT Work and Codex. Same batch configuration retained.',actualModel=None,actualQuality=None,selectorsExposed=False))
    ni=Image.open(N).convert('RGB');dc=R/'day-structure-snapshot.png'
    shutil.copy2(DAY,dc);write(str(dc)+'.generation.json',dict(file=str(dc),sha256=sha(dc),copiedAt=now(),derivedFrom=[ref(DAY),ref(str(DAY)+'.generation.json')],operation=dict(kind='unchanged read-only day geometry snapshot',globalFrameXYWH=[X-115,Y-115,4326,4326],scale=1),productionPixels=False,dayTaskModified=False))
    for n,b in [('north-native320.png',[0,3776,4096,4096]),('north-native115.png',[0,3981,4096,4096]),('north-native1254.png',[0,2842,4096,4096])]:image_save(ni.crop(b),R/n,[N],dict(kind='exact native north crop',cropLTRB=b,scale=1,resampling=False))
    image_save(ni.resize((1254,1254),Image.Resampling.LANCZOS),R/'north-context-preview.png',[N],dict(kind='native full context downsample only',sourcePixels=[4096,4096],outputPixels=[1254,1254],globalFrameXYWH=[X,Y-4096,4096,4096]))
    for ap,name in [('penglai_day','day-layout-context.png'),('penglai_mid_autumn','night-layout-context.png')]:
        lp=layout(ap);image_save(crop_layout(lp,[X-2048,Y-4096,8192,8192],(1254,1254)),R/name,[lp],dict(kind='coarse official context crop only',globalFrameXYWH=[X-2048,Y-4096,8192,8192],outputPixels=[1254,1254]))
    canvas=crop_layout(layout('penglai_day'),FRAME,(S,S));canvas.paste(Image.open(dc).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS),(205,205));canvas.paste(ni.crop((0,3776,4096,4096)),(320,0))
    image_save(canvas.resize((1254,1254),Image.Resampling.LANCZOS),R/'night-edit-target.png',[layout('penglai_day'),dc,N],dict(kind='exact-frame planning day geometry with real night north anchor',globalFrameXYWH=FRAME,dayStructureGlobalFrameXYWH=[X-115,Y-115,4326,4326],dayPasteXY=[205,205],dayPlanningUpscale=[4326,4326],northCropLTRB=[0,3776,4096,4096],northPasteXY=[320,0],northBeforeCompositeScale=1,outputPixels=[1254,1254],allResamplingPlanningOnly=True))
    tile=next(t for t in read(REPO/'qdao_city_tiles_4k_20260916/q64_production_plans/penglai_mid_autumn.json')['tiles'] if t['id']=='r11_c13')
    core=[320*1254/S,320*1254/S,(320+4096)*1254/S,(320+4096)*1254/S]
    nscope=ref(R/'north-native320.png',pixelSha256=hashlib.sha256(ni.crop((0,3776,4096,4096)).tobytes()).hexdigest(),sourceFile=str(N),sourceFileSha256AtFreeze=NSHA,sourceCropLTRB=[0,3776,4096,4096],wholeSourceStillUnderQA=False)
    write(F/'preparation.json',dict(createdAt=now(),north=ref(N),northScopedFreeze=nscope,sharedDayStructure=ref(dc),sharedDaySourceFrameGlobalXYWH=[X-115,Y-115,4326,4326],structureFrameGlobalXYWH=FRAME,structureCoreLTRB=core,missingNeighbors=['west','east','south','northwest'],dayTaskModified=False,planningOnly=True))
    write(F/'plan.json',dict(createdAt=now(),tile=tile,core=1024,halo=115,overlap=230,nativePatchPixels=[1254,1254],nativeGrid=[4,4],northCandidate=str(N),northCandidateSha256=NSHA,northScopedFreeze=nscope,candidateSourcesStillUnderScopedRepair=False,referenceFrameGlobalXYWH=FRAME,structureSourceFramePixels=[1254,1254],structureCoreLTRB=core,sharedDayStructureAvailable=True,sharedDayStructureSource=ref(dc),sharedDayTaskAdopted=False,dayTaskModified=False,stage='night_structure_pending_generation',rootReviewPending=True,nativePatchCount=0,formalAccepted=False,navigationVerified=False,clientVerified=False))
    prompt='''Use case: lighting-weather and exact geometry continuation. Edit Image1 into the Mid-Autumn EVENING version of this exact isometric Daoist Q game-map crop r11_c13. Output one opaque1254 square with identical framing and object scale. This is a tightly cropped continuous map, never a standalone scene. NO SKY, horizon, moon disc, stars, mountains, border, text, UI or people.
Image1 is the exact 4736-global-pixel square frame [48832,40640,4736,4736]. The actual4096 tile occupies x84.73..1169.27,y84.73..1169.27 in this1254 image. Its top84.73px contain actual native NIGHT north-neighbor pixels at x84.73..1169.27: these real canopy, paving, wall and wooden rail endpoints are authoritative. Heal the temporary straight composite edge at y84.73 without retaining a band. Continue these forms downward with the same slopes, thicknesses, scale and perspective into the target. Do not duplicate the north scene or shift its contours to match the coarse guide.
Image2 is the actual completed north neighbor FULL CONTEXT, which lies ABOVE the target. Image3 is its exact bottom1254-native-row crop to clarify the boundary contours. Image4 is the existing DAY structure of this same tile in a slightly smaller4326-global-pixel frame (its central4096 core is x33.33..1220.67); use its occupied footprints and object counts, never its daytime illumination. Image5 is the original whole-map NIGHT context for lighting only. Image6 is the PRIMARY APPROVED art style only: bright clean rounded full-bodied Daoist chibi hand painting, smooth dimensional materials, crisp restrained brushwork; never reproduce its UI.
Preserve the existing blue striped market canopy entering from upper-left and its timber frame, the existing small grouped cargo boxes and tied parcels lower-left of center, the open paved walking surface, pale rounded quay wall running diagonally from bottom-left toward upper-right, its existing rounded caps and wooden water fenders, deep blue harbor water to the right/lower-right, and the existing partial wooden boat corner clipped at right. Preserve the wall width, height, post positions, cargo footprints and cropped framing. The actual north neighbor controls any conflicting upper-boundary details: its blue canopy must continue seamlessly, its pale wall edge and single wooden rail retain their exact entry points and orientation. Never invent extra posts, beams, stalls, crates, lanterns, boat parts, windows or pavement branches. Do not rotate, recenter, widen, zoom, finish cropped objects or make a complete boat.
Use the north neighbor's clear blue-violet evening stone, warm golden amber light on honey wood, saturated blue fabric, pale blue stone wall and cobalt water, with restrained clean warm highlights. Bright readable evening, not murky darkness. Match its organized broad surface brushwork. No photographic grain, noise, blur or sharpening halos. All contours coherent and softly rounded with readable material edges. Preserve geometry first; this is planning only, later native patches supply final detail.'''
    refs=[R/'night-edit-target.png',R/'north-context-preview.png',R/'north-native1254.png',dc,R/'night-layout-context.png',STYLE]
    pp=F/'night-structure.prompt.txt';pp.write_text(prompt,encoding='utf-8')
    call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
    write(F/'night-structure.call.json',call);write(F/'night-structure.request.json',dict(startedAt=now(),configSnapshot=read(REPO/'config/image-generation.json'),prompt=str(pp),promptSha256=sha(pp),references=[ref(p,role=r) for p,r in zip(refs,['exact edit frame with true north anchor','native north whole context','exact native north boundary context','existing day geometry only','official night lighting context','approved painting style'])],submittedParameters=dict(model=None,quality=None,**call),planningFrameGlobalXYWH=FRAME,productionPixels=False,nativeDetailCount=0,dayTaskModified=False,formalAccepted=False))
    print(F/'night-structure.call.json')
def save(source,ident='night-structure',name='structure.png'):
    src=Path(source);dst=R/name;assert Image.open(src).size==(1254,1254);assert not dst.exists();shutil.copy2(src,dst)
    req=read(F/(ident+'.request.json'));write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin exposes no model or quality selector and returns no actual version/quality metadata.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],planningFrameGlobalXYWH=req['planningFrameGlobalXYWH'],sourceUpscaled=False,resizedAfterGeneration=False,productionPixels=False,nativeDetailCount=0,formalAccepted=False))
    print(dst);print(sha(dst))
def guides():
    assert sha(N)==NSHA
    src=Path(read(F/'plan.json').get('nightStructure',str(R/'structure.png')));k=1254/S;box=[205*k,205*k,4531*k,4531*k]
    im=Image.open(src).convert('RGB').transform((4326,4326),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)
    extended=R/'planning-extended4326.png';image_save(im,extended,[src],dict(kind='planning only crop and enlargement, never native final art',sourceExtentLTRB=box,globalFrameXYWH=[X-115,Y-115,4326,4326],coreLTRB=[115,115,4211,4211],resampling='BICUBIC'))
    records=[]
    for r in range(1,5):
        for c in range(1,5):
            ident=f'p{r}{c}';b=[(c-1)*1024,(r-1)*1024,(c-1)*1024+1254,(r-1)*1024+1254];p=F/'guides'/f'{ident}.png'
            op=dict(id=ident,cropLTRB=b,globalPatchXYWH=[X-115+(c-1)*1024,Y-115+(r-1)*1024,1254,1254],core=1024,halo=115,planningOnly=True)
            image_save(im.crop(b),p,[extended],op);records.append(ref(p,**op))
    for r in range(1,5):
        for c in range(1,5):
            a=Image.open(F/f'guides/p{r}{c}.png')
            if c<4:assert a.crop((1024,0,1254,1254)).tobytes()==Image.open(F/f'guides/p{r}{c+1}.png').crop((0,0,230,1254)).tobytes()
            if r<4:assert a.crop((0,1024,1254,1254)).tobytes()==Image.open(F/f'guides/p{r+1}{c}.png').crop((0,0,1254,230)).tobytes()
    write(F/'guides/index.json',dict(createdAt=now(),source=ref(extended),records=records,overlapsPixelIdentical=True,productionPixels=False,finalUseForbidden=True))
    ni=Image.open(N).convert('RGB');target=im.crop((115,115,4211,4211))
    for i in range(4):
        q=Image.new('RGB',(1024,640));q.paste(ni.crop((i*1024,3776,(i+1)*1024,4096)),(0,0));q.paste(target.crop((i*1024,0,(i+1)*1024,320)),(0,320))
        image_save(q,Q/f'north-join-segment{i+1}.png',[N,extended],dict(kind='true native north vs enlarged planning; macro geometry only',seamY=320,northCropLTRB=[i*1024,3776,(i+1)*1024,4096],targetCoreCropLTRB=[i*1024,0,(i+1)*1024,320],notNativeSeamAcceptance=True))
    pair=Image.new('RGB',(1254,1254));pair.paste(ni.resize((627,627),Image.Resampling.LANCZOS),(313,0));pair.paste(target.resize((627,627),Image.Resampling.LANCZOS),(313,627));image_save(pair,Q/'north-target-context.png',[N,extended],dict(kind='N above target overview; margins are QA display only',nativeSeamAccepted=False))
    image_save(target.resize((1254,1254),Image.Resampling.LANCZOS),Q/'core-preview.png',[extended],dict(kind='planning core overview',cropLTRB=[115,115,4211,4211],productionPixels=False))
    pp=read(F/'plan.json');pp.update(nightStructure=str(src),planningExtended4326=str(extended),guideIndex=str(F/'guides/index.json'),stage='structure_ready_for_root_review',rootReviewPending=True,nativePatchCount=0);write(F/'plan.json',pp)
    print('16 guides and 6 planning QA ready; native forbidden pending root review')
if __name__=='__main__':
    if sys.argv[1]=='setup':setup()
    elif sys.argv[1]=='save':save(*sys.argv[2:])
    elif sys.argv[1]=='guides':guides()
