"""Planning-only structural preparation. All new files stay in r10_c14."""
from pathlib import Path
import sys, shutil, hashlib
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from production import ROOT, REPO, read, write, sha, now, deriv
from PIL import Image

F = ROOT / 'r10_c14'
R = F / 'references'
STYLE = REPO / 'designs/gameplay-ui/04-guild.png'
X, Y, H, SIDE = 53248, 36864, 320, 4736
EXT = [X-H, Y-H, SIDE, SIDE]

def request(ident, prompt, refs, roles):
    pp = F / (ident+'.prompt.txt')
    pp.write_text(prompt, encoding='utf-8')
    args = dict(prompt=prompt, referenced_image_paths=[str(p) for p in refs], transparent_background=False)
    write(F/(ident+'.call.json'), args)
    write(F/(ident+'.request.json'), dict(startedAt=now(), configSnapshot=read(REPO/'config/image-generation.json'), prompt=str(pp), promptSha256=sha(pp), references=[dict(file=str(p),sha256=sha(p),role=role) for p,role in zip(refs,roles)], submittedParameters=dict(model=None,quality=None,**args), planningFrameGlobalXYWH=EXT, productionPixels=False, dayTaskAdopted=False, formalAccepted=False))

def freeze(north, expected):
    prep = read(F/'preparation.json')
    north=Path(north); assert sha(north)==expected
    west=Path(prep['west']['file']); nw=Path(prep['northWest']['file'])
    assert sha(west)==prep['west']['sha256']; assert sha(nw)==prep['northWest']['sha256']
    neighbors=[('north',north,[0,3776,4096,4096],[320,0]),('west',west,[3776,0,4096,4096],[0,320]),('northwest',nw,[3776,3776,4096,4096],[0,0])]
    crop=R/'north-native320.png'; Image.open(north).crop((0,3776,4096,4096)).save(crop)
    deriv(crop,[north],dict(kind='unchanged native north crop',cropLTRB=[0,3776,4096,4096],scale=1,resampling=False))
    for appearance, filename in [('penglai_day','shared-layout-target.png'),('penglai_mid_autumn','night-layout-target.png')]:
        layout=REPO/f'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/{appearance}/map-native-layout-reference.png'
        im=Image.open(layout).convert('RGB'); s=im.width/65536
        box=[EXT[0]*s,EXT[1]*s,(EXT[0]+SIDE)*s,(EXT[1]+SIDE)*s]
        canvas=im.transform((SIDE,SIDE),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)
        for role,src,b,xy in neighbors: canvas.paste(Image.open(src).convert('RGB').crop(b),xy)
        out=R/filename; assert not out.exists();canvas.resize((1254,1254),Image.Resampling.LANCZOS).save(out)
        deriv(out,[layout,north,west,nw],dict(kind='planning-only coarse layout with real native 320px north/west/northwest strips',layoutSourceExtentLTRB=box,globalRectXYWH=EXT,compositePixels=[SIDE,SIDE],nativeRegions=[dict(role=r,file=str(p),sha256=sha(p),cropLTRB=b,pasteXY=xy,scale=1) for r,p,b,xy in neighbors],outputPixels=[1254,1254],compositeDownsampling=1254/SIDE,productionPixels=False))
    context=Image.new('RGB',(8192,8192)); context.paste(Image.open(nw),(0,0));context.paste(Image.open(north),(4096,0));context.paste(Image.open(west),(0,4096))
    layout=REPO/'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/penglai_day/map-native-layout-reference.png';im=Image.open(layout).convert('RGB');s=im.width/65536
    context.paste(im.transform((4096,4096),Image.Transform.EXTENT,[X*s,Y*s,(X+4096)*s,(Y+4096)*s],Image.Resampling.BICUBIC),(4096,4096));cp=R/'native-neighbor-context.png';context.resize((1254,1254),Image.Resampling.LANCZOS).save(cp)
    deriv(cp,[nw,north,west,layout],dict(kind='planning-only 2x2 context; NW/N/W native candidates and SE coarse target',globalRectXYWH=[X-4096,Y-4096,8192,8192],outputPixels=[1254,1254],productionPixels=False))
    north_scope=dict(file=str(crop),sha256=sha(crop),pixelSha256=hashlib.sha256(Image.open(crop).convert('RGB').tobytes()).hexdigest(),sourceFile=str(north),sourceFileSha256AtFreeze=sha(north),sourceCropLTRB=[0,3776,4096,4096],scopePassedByRoot=True,wholeSourceStillUnderQA=True,laterWholeSourceRevalidationRequired=True)
    prep.update(north=dict(file=str(north),sha256=sha(north)),northStillPendingFreeze=False,northScopedFreeze=north_scope,frozenAt=now());write(F/'preparation.json',prep)
    plan=read(REPO/'qdao_city_tiles_4k_20260916/q64_production_plans/penglai_mid_autumn.json');tile=next(t for t in plan['tiles'] if t['id']=='r10_c14')
    write(F/'plan.json',dict(createdAt=now(),tile=tile,core=1024,halo=115,overlap=230,nativePatchPixels=[1254,1254],nativeGrid=[4,4],northCandidate=str(north),northCandidateSha256=sha(north),northScopedFreeze=north_scope,candidateSourcesStillUnderScopedRepair=True,westCandidate=str(west),westCandidateSha256=sha(west),northWestCandidate=str(nw),northWestCandidateSha256=sha(nw),referenceFrameGlobalXYWH=EXT,structureSourceFramePixels=[1254,1254],structureCoreLTRB=prep['structureCoreLTRB'],sharedDayStructureAvailable=False,sharedDayTaskAdopted=False,stage='shared_structure_pending_generation',rootReviewPending=True,nativePatchCount=0,formalAccepted=False,navigationVerified=False,clientVerified=False))
    prompt='''Use case: sketch-to-render with exact spatial preservation. Edit Image1 into a SHARED DAYLIGHT GEOMETRY PLANNING PROPOSAL for Penglai Daoist chibi game tile r10_c14. This is planning only; the day-map task has not adopted it.
Image1 is the EXACT frame to preserve. It represents a 4736-square global region including 320 pixels of context around the 4096-square tile. At this 1254-square image scale the central tile spans x84.73..1169.27 and y84.73..1169.27. The top84.73px and left84.73px include true native neighboring map geometry. Their contour endpoints and object scale are authoritative. The collage lines at x84.73/y84.73 are temporary compositing boundaries, not architecture: heal them naturally. Do not move, zoom, recenter or complete intentionally cropped objects.
Image2 is the approved day whole-map 2x2 layout context. Image3 shows the completed native evening neighbors: northwest upper-left, north upper-right, west lower-left, and coarse target lower-right. Image4 is the PRIMARY APPROVED ART STYLE ONLY: clean bright rounded full-bodied Daoist chibi hand painting, soft dimensional volumes, controlled restrained brushwork. No UI, text or characters.
Render one coherent DAYLIGHT version of the exact Image1 composition, recoloring its night strips to day while preserving their contour positions. Continue the native north paving grid, cut-off wooden cargo box and round wooden rail-post bases at their exact endpoints. Continue the native west crate edge, quay coping, block courses, harbor water and wooden rail from the existing pixels. Preserve the broad pale stone pedestrian area in the upper left, existing small mooring fixtures beside the wall, diagonal tall pale stone quay wall crossing the middle from lower left toward upper right, its existing stone posts and masonry buttress, turquoise harbor water to the lower/right side, the already present wooden dock passing diagonally across the lower half with its existing posts and rails, the cropped dock support at the right edge, and only the existing cropped mast and cream sail entering from the bottom. Keep every occupied footprint, wall height, walkway width and dock width fixed. Retain cropped objects; never fit a whole ship or whole box into this tile.
Resolve blurred surfaces as clean rounded stone and wood without introducing new architecture, steps, posts, lanterns, cargo, foliage, boats, ornaments or grout branches. Preserve the exact camera, perspective, framing, slopes and object count from Image1. Native neighbor contours override small differences in the coarse original layout. No depth of field: all visible surfaces have crisp hand-painted edges. One fully opaque 1254 square, full bleed, no labels, guides, border or watermark.'''
    request('shared-structure',prompt,[R/'shared-layout-target.png',R/'layout-day-context.png',cp,STYLE],['exact framed coarse target with authoritative native geometry strips','approved coarse day layout context only','actual native neighboring candidates and target location','approved style only'])
    print(str(F/'shared-structure.call.json'))

def save(ident, source, output):
    req=read(F/(ident+'.request.json'));src=Path(source);dst=R/output
    assert Image.open(src).size==(1254,1254);assert not dst.exists();shutil.copy2(src,dst)
    write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin; no exposed model/quality selectors or returned metadata.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],planningFrameGlobalXYWH=EXT,sourceUpscaled=False,resizedAfterGeneration=False,productionPixels=False,nativeDetailCount=0,dayTaskAdopted=False,formalAccepted=False))
    print(str(dst));print(sha(dst))

if __name__=='__main__':
    if sys.argv[1]=='freeze':freeze(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=='save':save(*sys.argv[2:5])
