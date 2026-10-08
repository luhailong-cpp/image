from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import read,write,sha,now,deriv
from PIL import Image,ImageDraw,ImageFilter,ImageChops
F=Path(__file__).resolve().parent
R=F/'references'; Q=F/'qa'; B=F/'repairs/west-beam'
FRAME=[52928,36544,4736,4736]
FOCUS=[52928,36544+760*4736/1254,320*4736/1254,320*4736/1254]

def compose():
    ai=R/'west-beam-post-clean-native.png'; base=R/'structure-lamp-aligned.png'
    rec=read(str(ai)+'.generation.json')
    rec.update(planningFrameGlobalXYWH=FOCUS,focusedSourceFrameCropLTRB=[0,760,320,1080],editSource=dict(file=str(R/'west-beam-inpaint-native.png'),sha256=sha(R/'west-beam-inpaint-native.png'),generationRecord=str(R/'west-beam-inpaint-native.png.generation.json')))
    write(str(ai)+'.generation.json',rec)
    patch=Image.open(ai).convert('RGB').resize((320,320),Image.Resampling.LANCZOS)
    p=B/'final-beam-planning-patch320.png';patch.save(p)
    deriv(p,[ai],dict(kind='planning-only reduction of AI-painted focused repair',sourcePixels=[1254,1254],outputPixels=[320,320],resampling='LANCZOS',sourceFramePasteXY=[0,760],productionPixels=False))
    orig=Image.open(base).convert('RGB'); canvas=orig.copy();canvas.paste(patch,(0,760))
    cp=B/'final-beam-fullframe-canvas.png';canvas.save(cp)
    deriv(cp,[base,p],dict(kind='planning-only focused AI patch positioned in original exact frame',pasteXY=[0,760],globalFrameXYWH=FRAME,geometryWarp=False))
    # Select only the locally repainted rail/post footprint and neighboring infill.
    # No code-drawn scene geometry; the mask only chooses already generated pixels.
    mask=Image.new('L',(1254,1254),0);draw=ImageDraw.Draw(mask)
    draw.polygon([(0,971),(90,909),(238,802),(299,791),(310,802),(310,1070),(232,1070),(212,938),(0,1070)],fill=255)
    mask=mask.filter(ImageFilter.GaussianBlur(5))
    mask.paste(0,(0,0,1254,790));mask.paste(0,(320,0,1254,1254));mask.paste(0,(0,1080,1254,1254))
    mp=B/'final-selection-mask.png';mask.save(mp)
    out=R/'structure-beam-final.png';Image.composite(canvas,orig,mask).save(out)
    assert ImageChops.difference(Image.open(out).crop((0,0,1254,790)),orig.crop((0,0,1254,790))).getbbox() is None
    deriv(out,[base,cp,mp],dict(kind='local selection of AI-painted continuous full-thickness rail and plain rounded raised attachment post',mask=str(mp),maskSha256=sha(mp),sourceFrameAllowedLTRB=[0,790,320,1080],upper790RowsPixelIdentical=True,geometryWarp=False,codeDrawnStructure=False,globalFrameXYWH=FRAME,productionPixels=False))
    box=[205*1254/4736,205*1254/4736,4531*1254/4736,4531*1254/4736]
    planning=R/'planning-extended4326-beam-final.png'
    Image.open(out).transform((4326,4326),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(planning)
    deriv(planning,[out],dict(kind='enlarged planning only, never final native detail',sourceExtentLTRB=box,outputPixels=[4326,4326],globalFrameXYWH=[53133,36749,4326,4326],coreLTRB=[115,115,4211,4211],productionPixels=False,resampling='BICUBIC'))
    plan=read(F/'plan.json');west=Path(plan['westCandidate']); w=Image.open(west).convert('RGB'); target=Image.open(planning).crop((115,115,4211,4211))
    for i in [2,3]:
        q=Q/f'west-join-segment{i+1}-beam-final.png'; im=Image.new('RGB',(640,1024)); im.paste(w.crop((3776,i*1024,4096,(i+1)*1024)),(0,0));im.paste(target.crop((0,i*1024,320,(i+1)*1024)),(320,0));im.save(q)
        deriv(q,[west,planning],dict(kind='native-size macro planning seam inspection',segment=i+1,seamX=320,westCropLTRB=[3776,i*1024,4096,(i+1)*1024],targetCoreCropLTRB=[0,i*1024,320,(i+1)*1024],notNativeSeamAcceptance=True))
    print(str(out));print(str(Q/'west-join-segment4-beam-final.png'))

def guides():
    frozen=read(B/'frozen-upper-guides.json')
    for r in frozen['files']:assert sha(r['file'])==r['sha256']
    index=read(F/'guides/index.json');write(B/'guide-index-before-final.json',index)
    planning=R/'planning-extended4326-beam-final.png';im=Image.open(planning)
    changed=[];unchanged=[]
    for r in index['records']:
        p=Path(r['file']); new=im.crop(r['cropLTRB'])
        if ImageChops.difference(new,Image.open(p)).getbbox() is None:
            unchanged.append(r['id']);continue
        assert r['id'] in ['p31','p32','p41','p42']
        assert not (F/'native'/(r['id']+'.png')).exists()
        assert not (F/'native'/(r['id']+'.request.json')).exists()
        write(B/(r['id']+'-before-final.generation.json'),read(str(p)+'.generation.json'))
        new.save(p);r['sha256']=sha(p);changed.append(r['id'])
        deriv(p,[planning],{k:v for k,v in r.items() if k not in ['file','sha256']})
    for r in frozen['files']:assert sha(r['file'])==r['sha256']
    for row in range(1,5):
        for col in range(1,5):
            a=Image.open(F/f'guides/p{row}{col}.png')
            if col<4: assert a.crop((1024,0,1254,1254)).tobytes()==Image.open(F/f'guides/p{row}{col+1}.png').crop((0,0,230,1254)).tobytes()
            if row<4: assert a.crop((0,1024,1254,1254)).tobytes()==Image.open(F/f'guides/p{row+1}{col}.png').crop((0,0,1254,230)).tobytes()
    index.update(source=dict(file=str(planning),sha256=sha(planning)),updatedAt=now(),overlapsPixelIdentical=True,unchangedUpperGuideFilesRetained=True);write(F/'guides/index.json',index)
    record=dict(updatedAt=now(),newPlanning=dict(file=str(planning),sha256=sha(planning)),changedGuides=changed,unchangedGuides=unchanged,allFrozenUpperGuidesShaUnchanged=True,frozenRecord=str(B/'frozen-upper-guides.json'),noNativeOutputsOrRequestsConsumedChangedGuides=True,allGuideOverlapsPixelIdentical=True)
    write(B/'guide-update-final.json',record)
    plan=read(F/'plan.json');plan.update(nightStructure=str(R/'structure-beam-final.png'),planningExtended4326=str(planning),beamStructureRepair=dict(status='continuous beam and plain raised existing post corrected locally; root review and shared day proposal update pending',guideUpdate=str(B/'guide-update-final.json')),rootReviewPending=True)
    plan['nativePatchConstraints']['p41']='CRITICAL WESTERN RAIL GEOMETRY: Continue the actual native rail top/bottom edges, full thickness, slope and highlight as one straight coherent beam. The corrected planning guide raises the existing right post attachment to meet this beam; preserve the same post footprint. Do not recreate the old low attachment, step, taper, doubled rail or extra post. Actual wall and waterline endpoints are authoritative.'
    write(F/'plan.json',plan);print(record)

def day_request():
    sys.path.insert(0,str(F))
    from prepare_structure import request,STYLE
    ref=B/'shared-day-focused-reference.png'
    Image.open(R/'shared-structure.png').crop((0,760,320,1080)).resize((1254,1254),Image.Resampling.LANCZOS).save(ref)
    deriv(ref,[R/'shared-structure.png'],dict(kind='planning-only appearance reference enlargement',sourceCropLTRB=[0,760,320,1080],outputPixels=[1254,1254],geometryAuthoritative=False))
    prompt='''Use case: lighting-weather. Recolor Image1 into clean bright DAYLIGHT while keeping every scene contour and all geometry exactly fixed. Image1 is the exact corrected focused game-map crop: one continuous thick diagonal wooden beam attaches to one existing plain rounded wooden post on the right, with a slightly raised top. The full beam upper and lower contours, thickness, diagonal slope, highlight path, attachment height, round post silhouette, foot, wall block positions, waterline and dock must remain pixel-aligned. Do not change the camera, perspective, framing, crop or object count. Image2 provides only the established DAYLIGHT color and material palette of this same location, NOT its old incorrect rail geometry: use warm honey wood, pale ivory-gray stone and turquoise water consistent with Image2. Remove blue-violet night lighting and warm lantern cast from Image1, but retain its exact geometry. Image3 is the approved clean rounded Daoist chibi painted style only. Do not add decorative bands, ropes, supports, posts, beams, objects, text or ornaments. One opaque1254-square planning crop, no zoom, border or watermark. This is a shared geometry proposal in the night task only, not an accepted change to the day task.'''
    request('west-beam-shared-day',prompt,[R/'west-beam-post-clean-native.png',ref,STYLE],['exact corrected geometry edit target; recolor only','day appearance palette only; old beam shape is not authoritative','approved style only'])
    req=read(F/'west-beam-shared-day.request.json');req.update(planningFrameGlobalXYWH=FOCUS,focusedSourceFrameCropLTRB=[0,760,320,1080]);write(F/'west-beam-shared-day.request.json',req)
    print(str(F/'west-beam-shared-day.call.json'))

def day_compose():
    ai=R/'west-beam-shared-day-native.png';base=R/'shared-structure.png';src=R/'west-beam-post-clean-native.png'
    rec=read(str(ai)+'.generation.json');rec.update(planningFrameGlobalXYWH=FOCUS,focusedSourceFrameCropLTRB=[0,760,320,1080],editSource=dict(file=str(src),sha256=sha(src),generationRecord=str(src)+'.generation.json'));write(str(ai)+'.generation.json',rec)
    orig=Image.open(base).convert('RGB');canvas=orig.copy();canvas.paste(Image.open(ai).convert('RGB').resize((320,320),Image.Resampling.LANCZOS),(0,760))
    cp=B/'shared-beam-fullframe-canvas.png';canvas.save(cp);deriv(cp,[base,ai],dict(kind='planning-only reduction and positioning of AI daylight recolor',sourcePixels=[1254,1254],patchPixels=[320,320],resampling='LANCZOS',sourceFramePasteXY=[0,760],globalFrameXYWH=FRAME))
    mp=B/'final-selection-mask.png';out=R/'shared-structure-beam-final.png';Image.composite(canvas,orig,Image.open(mp)).save(out)
    deriv(out,[base,cp,mp],dict(kind='local selection of AI-painted shared geometry proposal with corrected beam and existing-post attachment',mask=str(mp),globalFrameXYWH=FRAME,upper790RowsPixelIdentical=True,dayTaskAdopted=False,productionPixels=False))
    q=Q/'shared-night-beam-final-comparison.png'; pair=Image.new('RGB',(1254,627));pair.paste(Image.open(out).crop((0,627,627,1254)),(0,0));pair.paste(Image.open(R/'structure-beam-final.png').crop((0,627,627,1254)),(627,0));pair.save(q)
    deriv(q,[out,R/'structure-beam-final.png'],dict(kind='same-frame lower-left source quadrant geometry comparison',left='shared daylight proposal',right='night planning',cropLTRB=[0,627,627,1254],resampling=False))
    plan=read(F/'plan.json');plan.update(proposedSharedStructure=str(out));plan['beamStructureRepair']['status']='night and shared geometry locally corrected; root review status is separate';write(F/'plan.json',plan)
    print(str(q))

def review():
    old=read(Q/'structure-review.json');history=B/'structure-review-before-final.json'
    if not history.exists():write(history,old)
    plan=read(F/'plan.json')
    old.update(reviewedAt=now(),status='corrected_beam_ready_for_root_review',rootReviewPending=plan['rootReviewPending'],sharedStructure=dict(file=plan['proposedSharedStructure'],sha256=sha(plan['proposedSharedStructure'])),nightStructure=dict(file=plan['nightStructure'],sha256=sha(plan['nightStructure'])),northScopedFreeze=plan['northScopedFreeze'])
    old['historicalViewsBeforeBeamRepair']=old['actualViews']
    # Old upper/right quadrant and boundary views remain valid because only lower-left pixels changed.
    old['actualViews']=[r for r in old['actualViews'] if Path(r['file']).name not in ['west-join-segment3.png','west-join-segment4.png','day-night-quadrant3.png']]
    for p in [Q/'west-join-segment3-beam-final.png',Q/'west-join-segment4-beam-final.png',Q/'shared-night-beam-final-comparison.png',R/'structure-beam-final.png',R/'west-beam-post-clean-native.png']:
        old['actualViews'].append(dict(file=str(p),sha256=sha(p),actuallyViewed=True,viewTool='view_image',viewDetail='high'))
    old['nativeBoundaryReview']['west']='Macro beam correction now continues the real west upper/lower contours without the former large false vertical step. Same existing right dock post is raised locally to receive it. Minor planning/native edge and wall texture differences still require native exact-context continuation; this is not final native seam acceptance.'
    old['homologyReview'].update(views=4,notes='The three unaffected original quadrants retain their comparison. Updated lower-left comparison preserves corrected continuous beam, same post footprint with raised attachment, and all dock occupancy in shared day proposal and night plan. Day task has not adopted this proposal.')
    old['beamRepairReview']=dict(visibleOutcome='continuous full-thickness beam, plain rounded same-footprint right post, no extra bands',selectionMask=str(B/'final-selection-mask.png'),sourceFrameAllowedLTRB=[0,790,320,1080],upper790RowsPixelIdentical=True,allFrozenUpperGuideFilesShaUnchanged=True,guideUpdate=str(B/'guide-update-final.json'),rootReviewPending=plan['rootReviewPending'])
    old['nativeDetailCount']=0;old['productionPixelsFromPreparation']=False
    write(Q/'structure-review.json',old)
    p=F/'west-beam-post-clean.request.json';req=read(p);write(B/'post-clean-request-before-mapping-clarification.json',req)
    req.update(planningFrameGlobalXYWH=FOCUS,mappingClarifiedAt=now(),mappingClarification='Local focused crop mapping corrected in record; submitted prompt, reference bytes and call parameters unchanged.');write(p,req)
    checks=[]
    for name in ['west-beam-post-clean-native.png','west-beam-shared-day-native.png']:
        p=R/name;rec=read(str(p)+'.generation.json');assert sha(p)==rec['sha256'];assert sha(rec['evidence']['sourceOutputPath'])==rec['evidence']['sourceOutputSha256'];assert sha(rec['prompt'])==rec['promptSha256']
        for ref in rec['references']:assert sha(ref['file'])==ref['sha256']
        assert rec['actualModel'] is None and rec['actualQuality'] is None
        assert rec['planningFrameGlobalXYWH']==FOCUS
        checks.append(dict(file=str(p),sha256=sha(p),hostSourceAndPromptAndReferencesVerified=True,actualModel=None,actualQuality=None))
    write(B/'final-source-audit.json',dict(checkedAt=now(),generatedSources=checks,planningOnly=True,noDayTaskFilesWritten=True,frozenGuideCheck=read(B/'guide-update-final.json')))
    print('review and final source audit saved')

def root_authorize():
    plan=read(F/'plan.json')
    views=[R/'structure-beam-final.png',Q/'west-join-segment3-beam-final.png',Q/'west-join-segment4-beam-final.png',Q/'shared-night-beam-final-comparison.png']
    record=dict(recordedAt=now(),authorizationSource='Root collaboration NEW_TASK: final macro structure approved for lower two native rows after actual original-size viewing of these four images.',scope='macro geometry authorization, not formal native seam pass',actualViews=[dict(file=str(p),sha256=sha(p),actuallyViewedByRoot=True,viewDetail='original') for p in views],finding='Former large beam step removed; same post attachment and foot plausible. Native real west pixels must resolve remaining brushwork, waterlines and highlight differences.',allowedRows=[3,4],allGuidesFrozen=True,formalAccepted=False)
    write(Q/'root-structure-authorization.json',record)
    write(B/'guide-freeze-at-native-authorization.json',dict(frozenAt=now(),guideIndexSha256=sha(F/'guides/index.json'),files=[dict(file=r['file'],sha256=sha(r['file'])) for r in read(F/'guides/index.json')['records']]))
    plan.update(rootReviewPending=False,stage='native_generation_authorized',structurePreparationStatus='root_macro_geometry_review_passed_and_guides_frozen',rootStructureAuthorization=str(Q/'root-structure-authorization.json'))
    plan['beamStructureRepair'].update(status='root approved corrected shared/night macro geometry for native generation',rootReviewPending=False)
    write(F/'plan.json',plan)
    review=read(Q/'structure-review.json');review.update(status='root_macro_geometry_approved_native_generation_authorized',rootReviewPending=False,rootAuthorization=str(Q/'root-structure-authorization.json'));review['beamRepairReview']['rootReviewPending']=False;write(Q/'structure-review.json',review)
    print('native generation authorization recorded, guides frozen')

if __name__=='__main__':globals()[sys.argv[1]]()
