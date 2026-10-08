"""07-only NE planning preparation. No AI/API invocation; never modifies shared day art."""
from pathlib import Path
import sys,shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from production import REPO,read,write,sha,now,deriv
F=ROOT/'r10_c11';R=F/'references'
X,Y,H,S=40960,36864,115,4326
EXT=[X-H,Y-H,S,S]
STYLE=REPO/'designs/gameplay-ui/04-guild.png'
DAY=ROOT.parent/'penglai_day/r10_c11/references/structure.png'
DAY_SHA='c99d87ab58e440e26c03b52d112dfe7c1eece234b80a2b72eeb1b3e2361c55fd'
EAST=ROOT/'r10_c12/output/r10_c12.png'
EAST_SHA='3ca7d1d8b5711e0b8d315fe9f3c0a4fe5f032ba3dc2555edfa9854eca6dc2be2'
def ref(p):return dict(file=str(p),sha256=sha(p))
def prepare():
    assert not (F/'plan.json').exists(),'Prepared tile already exists; inspect rather than overwrite'
    handoff=read(ROOT/'handoff.json')
    candidates={q['tile']:q for q in handoff['baselineCandidates']}
    n=candidates['r09_c11'];ne=candidates['r09_c12']
    NORTH=Path(n['file']);NE=Path(ne['file']);LAYOUT=Path(handoff['layout']['file'])
    for p,s in [(DAY,DAY_SHA),(EAST,EAST_SHA),(NORTH,n['sha256']),(NE,ne['sha256']),(LAYOUT,handoff['layout']['sha256'])]:
        assert sha(p)==s,str(p)
    assert Image.open(DAY).size==(1254,1254)
    images={role:Image.open(p).convert('RGB') for role,p in [('north',NORTH),('east',EAST),('northeast',NE)]}
    assert all(im.size==(4096,4096) for im in images.values())
    R.mkdir(parents=True,exist_ok=True)
    operations=[
      dict(role='north',file=str(NORTH),sourceCropLTRB=[0,3981,4096,4096],canvasPasteXY=[115,0],scale=1),
      dict(role='east',file=str(EAST),sourceCropLTRB=[0,0,115,4096],canvasPasteXY=[4211,115],scale=1),
      dict(role='northeast',file=str(NE),sourceCropLTRB=[0,3981,115,4096],canvasPasteXY=[4211,0],scale=1)
    ]
    # Resized day pixels are only planning support; exact native neighbors are pasted at physical coordinates.
    canvas=Image.open(DAY).convert('RGB').resize((S,S),Image.Resampling.LANCZOS)
    for op in operations:
        source=Path(op['file']);piece=images[op['role']].crop(op['sourceCropLTRB'])
        native=R/(op['role']+'-native115.png');piece.save(native)
        deriv(native,[source],dict(kind='exact_native_context_crop',sourceCropLTRB=op['sourceCropLTRB'],scale=1,sourceUpscaling=False,productionPixels=False))
        canvas.paste(piece,op['canvasPasteXY']);op['sha256']=sha(source)
    target=R/'day-structure-with-night-ne-halo.png'
    canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(target)
    deriv(target,[DAY,NORTH,EAST,NE],dict(kind='planning_only_shared_day_geometry_with_actual_north_east_northeast_halo',globalRectXYWH=EXT,daySourcePixels=[1254,1254],daySourceFrameGlobalXYWH=EXT,compositePixels=[S,S],nativeRegions=operations,outputPixels=[1254,1254],outputScale=1254/S,sourceUpscalingOnlyForPlanning=True,notProductionPixels=True))
    # Actual N/E/NE neighbor previews are spatially arranged around the target in a 2x2 frame.
    layout=Image.open(LAYOUT).convert('RGB');ls=layout.width/65536
    qcontext=[X,Y-4096,8192,8192]
    qbox=[qcontext[0]*ls,qcontext[1]*ls,(qcontext[0]+8192)*ls,(qcontext[1]+8192)*ls]
    context=layout.transform((8192,8192),Image.Transform.EXTENT,qbox,Image.Resampling.BICUBIC)
    context.paste(images['north'],(0,0));context.paste(images['northeast'],(4096,0));context.paste(images['east'],(4096,4096))
    cp=R/'native-night-neighbor-context.png';context.resize((1254,1254),Image.Resampling.LANCZOS).save(cp)
    deriv(cp,[NORTH,NE,EAST,LAYOUT],dict(kind='planning_only_actual_N_NE_E_context_plus_coarse_target',globalRectXYWH=qcontext,gridRoles=[['north','northeast'],['coarse_original_night_target','east']],actualNeighborNativePixels=[4096,4096],outputPixels=[1254,1254],sourceUpscalingOnlyForCoarseLayout=True,notProductionPixels=True))
    for role,path in [('north',NORTH),('east',EAST)]:
        p=R/(role+'-preview.png');images[role].resize((1254,1254),Image.Resampling.LANCZOS).save(p)
        deriv(p,[path],dict(kind='downsampled_actual_neighbor_preview_only',role=role,scale=1254/4096,notProductionPixels=True))
    color=R/'night-layout-local.png'
    box=[EXT[0]*ls,EXT[1]*ls,(EXT[0]+S)*ls,(EXT[1]+S)*ls]
    layout.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(color)
    deriv(color,[LAYOUT],dict(kind='coarse_whole_city_night_color_reference_only_not_geometry_authority',globalRectXYWH=EXT,layoutCropLTRB=box,outputPixels=[1254,1254],sourceUpscalingOnlyForPlanning=True,notProductionPixels=True))
    fullplan=read(REPO/'qdao_city_tiles_4k_20260916/q64_production_plans/penglai_mid_autumn.json')
    tile=next(t for t in fullplan['tiles'] if t['id']=='r10_c11')
    assert tile['finalPixelRect']==[X,Y,4096,4096]
    core=[H*1254/S,H*1254/S,(H+4096)*1254/S,(H+4096)*1254/S]
    plan=dict(createdAt=now(),tile=tile,appearance='penglai_mid_autumn',core=1024,halo=115,overlap=230,nativePatchPixels=[1254,1254],nativeGrid=[4,4],nativeWorkflow=dict(engine='multi_edge_v1',wavefront='NE',AIInputsTransformed=False,firstPilotOnly=True,codeReview=ref(ROOT/'tools/multi_edge/root-code-review.json')),northCandidate=str(NORTH),northCandidateSha256=sha(NORTH),eastCandidate=str(EAST),eastCandidateSha256=sha(EAST),northEastCandidate=str(NE),northEastCandidateSha256=sha(NE),referenceFrameGlobalXYWH=EXT,structureSourceFramePixels=[1254,1254],structureCoreLTRB=core,planningExtendedPixels=[4326,4326],sharedDayStructure=ref(DAY),sharedDayStructureReadOnly=True,sharedDayTaskAdopted=False,structureTarget=ref(target),stage='night_structure_prepared_not_submitted',rootReviewPending=True,nativePatchCount=0,formalAccepted=False,clientVerified=False,navigationVerified=False)
    write(F/'plan.json',plan)
    prompt='''Use case: lighting-weather with exact geometry preservation. Edit Image1 into the same-frame Mid-Autumn evening STRUCTURAL PLANNING art for tile r10_c11 of the clean rounded Daoist Q fantasy game town. Output one fully opaque 1254 by 1254 square, keeping its exact camera, scale, crop and every occupied footprint.
Image1 is the authoritative same-frame DAY composition with real completed NIGHT neighbor strips already placed across its TOP and RIGHT outer halo. It represents global frame [40845,36749,4326,4326]; the central 4096-square tile occupies x33.34..1220.66,y33.34..1220.66 of this 1254 image. TOP y0..33.34 uses the actual NORTH tile, RIGHT x1220.66..1253 uses the actual EAST tile, and the upper-right corner contains actual NORTHEAST pixels. Continue those real boundary contours and material colors naturally without a straight collage line. Preserve their positions; do not shift or widen the frame.
Image2 is the exact shared DAY structural reference and must remain the geometry authority. Preserve the large golden-leaf tree and its trunk/roots in the upper-left, all bush and grass masses, the descending faceted pale cliff slabs with their exact cracks and silhouettes, the curving channel of water and shoreline foam, the green trees at the right and lower-right, and the small cropped wooden fence and pale walkway at the bottom-right. Keep the same object counts, footprint, leaf mass boundaries, slopes, river width, fence positions and deliberate cropped objects. Never complete a cut-off tree/fence inside the square. No new rocks, steps, trees, boats, posts, buildings, lanterns or decorations.
Image3 gives REAL NIGHT neighbor context in a 2x2 spatial arrangement: actual NORTH at upper-left, actual NORTHEAST at upper-right, coarse target position at lower-left, and actual EAST at lower-right. These completed night colors and exact Image1 halo endpoints take precedence over the coarse color reference. Do not copy the context's full scene into this crop.
Image4 is ONLY the same-area original whole-city NIGHT color reference; do not adopt differences in its geometry or objects. Relight Image1 toward clean luminous blue-violet moonlit stone, deep cobalt/turquoise water with restrained light-blue foam, jade/teal greenery, and softly warm ochre/golden foliage. Keep the scene bright, clean, rounded and readable. The existing golden tree stays the same tree, recolored for evening without becoming a glowing neon object. Do not invent local warm lamps or lanterns to justify lighting.
Image5 is the PRIMARY APPROVED PAINTING STYLE only: bright clean full-bodied Daoist chibi game art, smooth rounded volumes, controlled hand-painted highlights and organized subtle brushwork. Never copy its UI, writing or characters. No text, HUD, border, watermark, photorealistic noise, blur, plastic glare or sharpening halos. Change lighting and surface colors only; retain the shared composition exactly. This is a planning guide, not a completed native 4K tile.'''
    pp=F/'night-structure.prompt.txt';pp.write_text(prompt,encoding='utf-8')
    refs=[target,DAY,cp,color,STYLE]
    roles=['same frame shared day target with authoritative actual night NE halo','shared day structure: geometry authority, read only','actual night N/E/NE context and coarse target position','original whole-night local colors only','approved Daoist chibi painting style']
    call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
    write(F/'night-structure.call.json',call)
    write(F/'night-structure.request.json',dict(preparedAt=now(),submissionState='prepared_only_not_submitted',notSubmittedYet=True,configSnapshot=read(REPO/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,**call),prompt=str(pp),promptSha256=sha(pp),references=[dict(**ref(p),role=role) for p,role in zip(refs,roles)],sourceNeighbors={role:ref(p) for role,p in [('north',NORTH),('east',EAST),('northeast',NE)]},referenceFrameGlobalXYWH=EXT,nativeRegions=operations,productionPixels=False,dayTaskAdopted=False,formalAccepted=False))
    write(F/'preparation.json',dict(preparedAt=now(),scope='r10_c11 NE planning only; no AI generation started',plan=ref(F/'plan.json'),request=ref(F/'night-structure.request.json'),call=ref(F/'night-structure.call.json'),target=ref(target),sharedDayStructure=ref(DAY),nativeNeighborHashesVerified=True,nativePhysicalFrameNotTransformed=True,productionPixels=False,rootMustViewBeforeGeneration=True,rootReviewPending=True))
    sys.path.insert(0,str(ROOT/'tools/multi_edge'));import cli
    _,_,wave,neighbors=cli.setup('r10_c11')
    assert wave=='NE' and set(neighbors)=={'north','east','northeast'}
    print(str(F/'night-structure.call.json'));print('NE plan/setup validation passed; generation not started.')
def save(source):
    req=read(F/'night-structure.request.json');src=Path(source);dst=R/'structure.png'
    assert Image.open(src).size==(1254,1254) and not dst.exists()
    for item in req['references']:assert sha(item['file'])==item['sha256']
    shutil.copy2(src,dst)
    write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin; model and quality selectors/actual values not exposed.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],planningFrameGlobalXYWH=EXT,sourceUpscaled=False,resizedAfterGeneration=False,productionPixels=False,nativeDetailCount=0,sharedDayTaskAdopted=False,formalAccepted=False))
    print(str(dst));print(sha(dst))
if __name__=='__main__':
    if len(sys.argv)==1 or sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='save':save(sys.argv[2])
    else:raise ValueError('Use prepare or save SOURCE; this script never calls an AI service')

