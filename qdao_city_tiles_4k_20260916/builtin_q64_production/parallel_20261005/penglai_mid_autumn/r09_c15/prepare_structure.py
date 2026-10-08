"""Same-batch west-supported planning; no AI invocation and no day writes."""
from pathlib import Path
import sys, shutil
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from production import REPO,read,write,sha,now,deriv
F=ROOT/'r09_c15';R=F/'references'
DAY=ROOT.parent/'penglai_day/r09_c15/references/structure.png'
WEST=ROOT/'r09_c14/output/r09_c14-candidate.png'
STYLE=REPO/'designs/gameplay-ui/04-guild.png'
X,Y=57344,32768
EXT=[X-115,Y-115,4326,4326]
def ref(p):return dict(file=str(p),sha256=sha(p))
def prepare():
    assert not (F/'plan.json').exists()
    assert sha(DAY)=='1d0362414df322ffff61339fca5f82e7639fc08e95934ee0a80535eec3bace2f'
    assert sha(WEST)=='26ef781afe2fe0d6d8352f4a6f57e88780b93a7ed26cb41411efbc35d44432dc'
    assert read(ROOT/'r09_c14/output/manifest.json')['scopedLocalSeamsPassed']
    R.mkdir(parents=True,exist_ok=True)
    west=Image.open(WEST).convert('RGB');assert west.size==(4096,4096)
    strip=R/'west-native115.png';west.crop((3981,0,4096,4096)).save(strip)
    deriv(strip,[WEST],dict(kind='actual_native_west_context',cropLTRB=[3981,0,4096,4096],scale=1,productionPixels=False))
    target=Image.open(DAY).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS)
    target.paste(Image.open(strip),(0,115))
    tp=R/'day-structure-with-night-west-halo.png';target.resize((1254,1254),Image.Resampling.LANCZOS).save(tp)
    deriv(tp,[DAY,WEST],dict(kind='planning_only_shared_day_with_actual_night_west_halo',globalRectXYWH=EXT,daySourceFrameGlobalXYWH=EXT,nativeCropLTRB=[3981,0,4096,4096],nativePasteXY=[0,115],outputPixels=[1254,1254],sourceUpscalingOnlyForPlanning=True,productionPixels=False))
    wp=R/'west-preview.png';west.resize((1254,1254),Image.Resampling.LANCZOS).save(wp)
    deriv(wp,[WEST],dict(kind='actual_neighbor_preview_only',scale=1254/4096,productionPixels=False))
    handoff=read(ROOT/'handoff.json');layout=Path(handoff['layout']['file']);assert sha(layout)==handoff['layout']['sha256']
    im=Image.open(layout).convert('RGB');s=im.width/65536;box=[EXT[0]*s,EXT[1]*s,(EXT[0]+4326)*s,(EXT[1]+4326)*s]
    lp=R/'night-layout-local.png';im.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(lp)
    deriv(lp,[layout],dict(kind='original_night_color_reference_only',globalRectXYWH=EXT,cropLTRB=box,productionPixels=False))
    fullplan=read(handoff['plan']['file']);tile=next(t for t in fullplan['tiles'] if t['id']=='r09_c15')
    assert tile['finalPixelRect']==[X,Y,4096,4096]
    write(F/'plan.json',dict(createdAt=now(),tile=tile,core=1024,halo=115,overlap=230,nativePatchPixels=[1254,1254],nativeGrid=[4,4],westCandidate=str(WEST),westCandidateSha256=sha(WEST),referenceFrameGlobalXYWH=EXT,structureSourceFramePixels=[1254,1254],structureCoreLTRB=[115*1254/4326]*2+[(115+4096)*1254/4326]*2,sharedDayStructure=ref(DAY),sharedDayStructureReadOnly=True,stage='night_structure_prepared',rootReviewPending=True,formalAccepted=False,clientVerified=False,navigationVerified=False,schedulingNote='Independent ready west-supported tile moved forward from east expansion; only existing r09_c14 required. No other existing adjacent tile, so no opposite-side closure is introduced.'))
    prompt='''Use case: lighting-weather with exact geometry preservation. Edit Image1 into a clean Mid-Autumn evening planning reference for the continuous Daoist chibi harbor map, tile r09_c15. Return one opaque1254 square at EXACTLY the same frame, camera, scale and object locations.
Image1 is the authoritative shared daylight composition with real NIGHT western-neighbor pixels in its left outer halo. The full frame represents [57229,32653,4326,4326]; the central4096 tile occupies x/y33.34..1220.66. The left33.34-pixel strip is real neighboring context, NOT a border, pole or vertical wall. Continue its existing rock, rope rail, draped cloth, foliage and paving endpoints naturally. Remove the temporary straight collage line. Preserve the existing neighbor's colors and contour endpoints.
Image2 is the shared DAY geometry authority. Keep the rounded rocks at the upper/right edges, the smaller mossy rock at upper-left and the single tiny isolated water rock. Keep the same diagonal rope-bound timber fence, existing ivory and coral fabric panels, exact posts and ties, sparse plants, lower paving, cropped foreground wood and stone square post. Do not zoom, change shoreline/rock footprints, alter rail slope or complete cropped objects. When small details on the left differ, the real Image1 boundary and Image3 actual neighbor take priority, including the continuation of its existing ivory cloth.
Image3 is the actual completed WEST night tile; only its rightmost edge touches this target left edge. It supplies material/night-color context, not a replacement scene. Image4 is the original whole-city NIGHT color/layout context for this exact area; use its night colors, while Image1/2 retain geometry. Image5 is approved PRIMARY ART STYLE only: bright clean rounded Daoist chibi hand painting with smooth full volumes and controlled subtle brushwork; do not copy its UI or writing.
Relight the existing scene to readable luminous blue-violet evening rocks and paving, cobalt-blue harbor water with restrained light-blue waves, jade/teal plants, warm honey wood and muted coral/ivory cloth. Preserve all current occupied footprints and counts. No new lamp, boat, building, post, stone, sign, decoration, character or text. Do not darken into muddy black shadows or turn waves into noisy glitter. No blur, grain, photographic detail, sharpening halos, border or watermark. Change lighting and paint colors only, keeping the shared whole-crop geometry. This is planning only, not native4K production.'''
    pp=F/'night-structure.prompt.txt';pp.write_text(prompt,encoding='utf-8')
    refs=[tp,DAY,wp,lp,STYLE];call=dict(prompt=prompt,referenced_image_paths=[str(p) for p in refs],transparent_background=False)
    write(F/'night-structure.call.json',call)
    write(F/'night-structure.request.json',dict(preparedAt=now(),configSnapshot=read(REPO/'config/image-generation.json'),submittedParameters=dict(model=None,quality=None,**call),prompt=str(pp),promptSha256=sha(pp),references=[dict(**ref(p),role=role) for p,role in zip(refs,['exact target and actual W halo','shared day geometry','actual W night color and edge context','coarse original night colors only','approved style'])],planningFrameGlobalXYWH=EXT,productionPixels=False,formalAccepted=False))
    print(str(F/'night-structure.call.json'))
def save(source):
    req=read(F/'night-structure.request.json');src=Path(source);dst=R/'structure.png'
    assert not dst.exists() and Image.open(src).size==(1254,1254)
    for r in req['references']:assert sha(r['file'])==r['sha256']
    shutil.copy2(src,dst)
    write(str(dst)+'.generation.json',dict(file=str(dst),sha256=sha(dst),generatedAt=now(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=req['configSnapshot'],submittedParameters=req['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host-managed builtin; no exposed or returned model/quality metadata.',evidence=dict(sourceOutputPath=str(src),sourceOutputSha256=sha(src),resultId=src.stem),prompt=req['prompt'],promptSha256=req['promptSha256'],references=req['references'],planningFrameGlobalXYWH=EXT,sourceUpscaled=False,resizedAfterGeneration=False,productionPixels=False,formalAccepted=False))
    print(str(dst));print(sha(dst))
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='save':save(sys.argv[2])
