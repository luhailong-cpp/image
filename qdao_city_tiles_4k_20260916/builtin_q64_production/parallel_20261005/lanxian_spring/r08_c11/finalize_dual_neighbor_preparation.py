"""Complete dual-neighbor planning references; never writes selected source art."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image

OUT = Path(__file__).resolve().parent
BASE = OUT.parent
STYLE = Path('D:/work/image/designs/gameplay-ui/04-guild.png')
NOW = datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,o):
    p=Path(p); assert p.resolve().is_relative_to(OUT)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p,role=None):
    p=Path(p); d={'file':p.as_posix(),'sha256':sha(p),'bytes':p.stat().st_size}
    if role:d['role']=role
    if p.suffix=='.png':d['pixels']=list(Image.open(p).size)
    return d

prep=read(OUT/'preparation.json')
wm=BASE/'r08_c10/selected-v2/delivery.manifest.json'
sm=BASE/'r09_c11/selected/delivery.manifest.json'
assert sha(sm)=='098734aab55fc12d0bbfe96be06155b0755be16261dcf9f923cb19ab9cbcaf26'
wd=read(wm);sd=read(sm)
wp=Path(wd['outputs']['extended4326.png']['file'])
sp=Path(sd['outputs']['extended']['file'])
assert sha(wp)==wd['outputs']['extended4326.png']['sha256']=='06bd63d0da7240864a45dd7fee4f38ef8382ceba7a6c9e6bff1e0f2bcd591072'
assert sha(sp)==sd['outputs']['extended']['sha256']=='284aa79bf05978112c4b304911dfc0b9083006aeac49c6f49fc9245c85bea647'
assert not (BASE.parent/'lanxian_day/r08_c11').exists()
west=Image.open(wp).convert('RGB').crop((4096,0,4326,4326))
south=Image.open(sp).convert('RGB').crop((0,0,4326,230))
wstrip=OUT/'guides/west-r08_c10-exact230x4326.png'
sstrip=OUT/'guides/south-r09_c11-exact4326x230.png'
assert Image.open(wstrip).convert('RGB').tobytes()==west.tobytes()
assert Image.open(sstrip).convert('RGB').tobytes()==south.tobytes()

ownership={
    'guideOnly':True,
    'wholeCityCornerLTRB':[40845,32653,41075,32883],
    'targetExtendedCornerLTRB':[0,4096,230,4326],
    'splitYInTargetExtended':4211,
    'guidePastePolicy':'Paste west230 and south230; restore the upper115 rows of their southwest230 square from west. Lower115 rows remain south. Exact unblended source choice, no resampling at4326.',
    'cornerGuideOwnerRects':[
        {'targetExtendedLTRB':[0,4096,230,4211],'source':'west','sourceCropLTRB':[4096,4096,4326,4211]},
        {'targetExtendedLTRB':[0,4211,230,4326],'source':'south','sourceCropLTRB':[0,115,230,230]}],
    'committedCoreAuthority':[
        {'targetExtendedLTRB':[0,115,115,4211],'source':'west','reason':'Actual existing r08_c10 core; preserve exact when reusing outside target core.'},
        {'targetExtendedLTRB':[115,4211,4211,4326],'source':'south','reason':'Actual existing r09_c11 core; preserve exact when reusing outside target core.'}],
    'provisionalHaloPolicy':'The west right115 and south upper115 are provisional generated halos, not independently accepted target-core geometry. Their disagreement cannot be solved by claiming both230 strips exact. Use both as references and inspect/redraw the new target core to connect the committed neighbor core edges.',
    'diagonalCornerPolicy':'Lower-left115 square belongs to diagonal r09_c10, absent from the two immediate core domains. Guide takes south halo provisionally; final four-tile corner must verify against diagonal selected source.',
    'knownConflict':'Leaf contours and tones differ visibly in the overlapping230 square. Hard split has a visible leaf step. Guide preparation is ready; pixel continuity and final corner acceptance remain pending.',
    'requiresNativeSouthwestCornerReview':True,
    'simultaneousFull230EqualityClaimAllowed':False,
    'finalCornerAccepted':False,
}
guide=Image.open(OUT/'guides/common-day-layout-only-4326.png').convert('RGB')
guide.paste(west,(0,0));guide.paste(south,(0,4096))
guide.paste(west.crop((0,4096,230,4211)),(0,4096))
sources=[info(OUT/'guides/common-day-layout-only-4326.png','True mapped whole-city crop; enlarged layout only'),info(wstrip,'Exact west native context'),info(sstrip,'Exact south native context'),info(wm,'Current west selection'),info(sm,'Current south selection')]
records=[]
for name,im,operation in [
    ('shared-layout-with-west-south-context-4326.png',guide,'Unblended exact native neighbor strips pasted over layout-only guide. Corner follows explicit split ownership.'),
    ('shared-layout-with-west-south-context-1254.png',guide.resize((1254,1254),Image.Resampling.LANCZOS),'Downscale4326 to1254 LANCZOS for regional layout reference only; NOT production pixels.')]:
    p=OUT/'guides'/name;im.save(p)
    rec={**info(p,'Shared day/spring structural guide only'),'createdAtUtc':NOW,'newAIGeneration':False,'actualModel':None,'actualQuality':None,'derivedFrom':sources,'operation':operation,'ownership':ownership,'productionPixelsAllowed':False,'formalAccepted':False,'wholeCityExtendedLTRB':[40845,28557,45171,32883],'coreInExtendedLTRB':[115,115,4211,4211]}
    write(str(p)+'.derivation.json',rec);records.append(rec)
write(OUT/'corner-source-ownership.json',ownership)

prompt='''Create one opaque 1254 x 1254 regional structural guide for the original Daoist chibi game 五行奇谈. This is the single canonical neutral geometry for tile r08_c11, shared by daytime and Spring Festival appearances. Output the same exact crop and camera as Image 1. Whole-city extended pixel rectangle [40845,28557,45171,32883] in a 65536-square city. No zoom, recentering, rotation, added margin or changed composition.

Image 1 is the true mapped local city crop with sharper WEST and SOUTH neighbor context pasted onto its edges. It establishes composition and all footprints, not finished detail. Image 2 is the separate exact 230 x 4326 west neighbor strip. Image 3 is the separate exact 4326 x 230 south neighbor strip. These native strips establish entering leaf, branch, paving, shadow and water endpoints. Image 4 is the user-approved rendering style: rounded full forms, bright clean painted materials, polished Daoist chibi quality. Use Image 4 only for rendering quality; do not copy its UI, typography, frames, characters, badges, lanterns or new objects.

Reconstruct the existing local contents: rounded pink flowering canopy in the upper half, its dark brown trunk and dark green planting inside the existing curved gray stone planter; pale cream paved open route left and center with existing tree shadows; large existing yellow-green willow canopy lower center/right, drooping leaves and its brown trunk exiting the bottom; clipped dark green rounded tree canopy entering lower-left; turquoise river on the right with the existing pale stone retaining edge/balustrade and square posts; the clipped existing orange vertical architectural support at the extreme upper-right. Keep all these canopy envelopes, trunk positions, planter footprints, shoreline, route widths and open areas. Continue the native SOUTH strip's existing foliage, trunks, willow leaves and water into this exact crop. Do not invent a bridge, new planter, tree, road, wall, building, steps, decorations or props.

The sharp guide band edges at x230 and y4096 in a4326 canvas (about x66.67 and y1187.33 in the1254 guide) are paste boundaries, not scene geometry. Reconcile detail naturally across them without drawing straight walls, strips, posts, shadows or seams there. The southwest230-square corner has a visible source disagreement: the guide uses west in its upper115 rows and south in its lower115 rows. This horizontal split is NOT a real leaf edge. Preserve the actual committed west core edge (westmost115 context pixels above target y4211) and actual committed south core edge (southernmost115 context pixels to the right of target x115); use provisional inner halo details as continuity guidance, not as a demand to duplicate their conflicting leaf contours. Join foliage organically at the corner without a rectangular kink.

Keep natural gray/cream stone, brown trunks, fresh green foliage, existing pink blossoms and bright turquoise water. Do not add Spring Festival objects or red/gold ornaments to this neutral shared structural base. No text, signs, logos, interface, people, weapons or border. High oblique isometric top-down game-map view, consistent soft sunlight and shadows, clean smooth painterly surfaces with readable rounded material edges. Render the local crop with crisp natural small detail, avoiding photorealism, noisy grain, plastic sheen, bevel-grid artifacts and blurred enlarged pixels. This output is a guide only: final4K game pixels will be made separately from sixteen native1254 pieces; do not claim this guide is4K or an accepted tile.'''
prompt_file=OUT/'regional-prompt-pending.txt';prompt_file.write_text(prompt+'\n',encoding='utf-8')
refs=[{'path':str(OUT/'guides/shared-layout-with-west-south-context-1254.png'),'role':'Exact mapped shared layout with west and south constraints'}, {'path':str(wstrip),'role':'Native west230 context'}, {'path':str(sstrip),'role':'Native south230 context'}, {'path':str(STYLE),'role':'User-approved material and painting style only'}]
request={'schemaVersion':1,'createdAtUtc':NOW,'tile':'r08_c11','status':'ready_for_parent_submission_after_final_view','submitted':False,'newAIGeneration':False,'promptFile':info(prompt_file),'prompt':prompt,'references':[{**r,'sha256':sha(r['path']),'pixels':list(Image.open(r['path']).size)} for r in refs],'submittedParameters':{'prompt':prompt,'referenced_image_paths':[r['path'] for r in refs],'transparent_background':False},'configurationTarget':read(OUT/'source-evidence/config-snapshot.json'),'actualModel':None,'actualQuality':None,'modelAndQualityEvidence':'Built-in imagegen exposes no model or quality selector. Actual returned values must remain null unless disclosed.','guideOnly':True,'productionPixelsAllowed':False,'cornerOwnershipFile':info(OUT/'corner-source-ownership.json'),'formalAccepted':False}
write(OUT/'regional-request-pending.json',request)

prep.update(updatedAtUtc=NOW,status='dual_neighbor_context_ready_corner_continuity_requires_native_review',generationAllowedInThisPreparationStep=False,generationHoldReason=None,parentMayGenerateAfterActualReferenceView=True)
prep['southNeighbor'].update(status='selected_complete_native_candidate_verified',sourceFile=str(sp),sourceSha256=sha(sp),manifest=info(sm),mustRefreshBeforeGeneration=False,noSouthPixelsFabricated=True)
prep['sourceQualification'].update(southHashesVerified=True,exactSouth230CropVerified=True,southNeighborFormalAccepted=sd['formalAccepted'],cornerSourcesIdentical=False,cornerFinalAccepted=False)
prep['artifacts']+=records
prep['cornerSourceOwnership']=ownership
prep['beforeGeneration']=[x for x in prep['beforeGeneration'] if not x.startswith('South r09_c11 is unfinished')]
prep['beforeGeneration'].append('Actually inspect both exact source strips and the southwest conflict; carry explicit core ownership and unresolved corner QA into native production. Do not claim both full230 bands can be preserved simultaneously.')
for cell in prep['nativePieceContract']:
    pending=cell.pop('externalSouthBandPending',None)
    cell['externalSouthContextBand']=pending
    if cell['cell']=='r04_c01':cell['cornerOwnershipFile']=str(OUT/'corner-source-ownership.json')
write(OUT/'preparation.json',prep)
nav=read(OUT/'navigation-contract.json');nav.update(updatedAtUtc=NOW,southContextPending=False,mustRefreshSouthBeforeGeneration=False,southContext=info(sstrip),cornerSourceOwnership=ownership)
nav['rules'].append('The south mixed-resolution boundary at y4096 is not scene geometry. Exact committed neighbor core pixels outrank contradictory provisional halos; southwest corner needs separate native continuity inspection.')
write(OUT/'navigation-contract.json',nav)
qa=read(OUT/'qa/southwest-corner-comparison.json')
qa.update(actuallyViewed=True,reviewedAtUtc=NOW,observed='Visible leaf contour and tone disagreements. Horizontal upper-west/lower-south ownership split creates a visible guide-only step; final corner not accepted.',chosenGuideOwnership=ownership)
write(OUT/'qa/southwest-corner-comparison.json',qa)
print(json.dumps({'guide':records[-1]['file'],'guideSha256':records[-1]['sha256'],'southSha256':sha(sp),'westSha256':sha(wp),'promptFile':str(prompt_file),'request':str(OUT/'regional-request-pending.json'),'finalCornerAccepted':False},ensure_ascii=False))
