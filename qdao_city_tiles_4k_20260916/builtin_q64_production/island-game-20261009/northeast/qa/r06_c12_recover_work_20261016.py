from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from native_work import *

if sys.argv[1]=='recover03':
    ident='r06_c12_p04_03'
    src=Path('C:/Users/luyua/.codex/generated_images/01a135cf-d17c-7762-8d59-9feb3c6594a0/exec-a7677cd8-9453-4093-a879-af1145201192.png')
    receipt=ZONE/'receipts'/f'{ident}.tool.json'
    assert not receipt.exists() and src.exists()
    refs=read(ZONE/'prompts'/f'{ident}.inputs.json')
    for ref in refs: assert sha(ref['file'])==ref['sha256']
    write(receipt,{'id':ident,'tool':'image_gen.imagegen','source':src.as_posix(),'actualModel':None,'output_hint':None,'recovery':'Unarchived PNG found in the previous worker generated_images directory. Visually matches prepared p04_03 anchored guide and prompt; native dimensions verified. No duplicate generation. Original response is unavailable in recovery worker context; no output_hint fabricated.','sourceSha256':sha(src),'sourceLastWriteTimeUtc':datetime.fromtimestamp(src.stat().st_mtime,timezone.utc).isoformat(),'recoveredAtUtc':now()})
    from argparse import Namespace
    ingest(Namespace(id=ident,source=str(src),no_progress=True))
    p=ZONE/'native'/f'{ident}.png.generation.json';q=read(p)
    q['generatedAt']=None;q['archivedAtUtc']=now();q['generatedAtReason']='Recovered from existing returned PNG; exact original tool completion timestamp unavailable.'
    q['evidence']['fields']=['recoveredSourcePath','sourceSha256','sourceLastWriteTimeUtc'];write(p,q)
elif sys.argv[1]=='prepare04':
    ident='r06_c12_p04_04'
    inp=ZONE/'prompts'/f'{ident}.inputs.json';refs=read(inp)[:3]
    for filename in ['designs/mail-ui-v1/01-mail-event.png','designs/team-ui-v2/team-ui-v2.png']:
        p=ROOT/filename;assert p.exists();refs.append({'file':p.as_posix(),'sha256':sha(p),'role':'approved Daoist Q painting style only; ignore UI, text, characters, night scenery and layout'})
    write(inp,refs)
    prompt='''Use case: precise-object-edit. Complete Image1 into one native 1254x1254 crisp hand-painted Daoist Q game-map crop with 1024px central core and 115px halo. The sharp TOP230 and LEFT230 are exact native overlap anchors. The blurred remainder is coordinate layout only. Repaint only the blurred part with clear native detail while preserving composition, camera, scale and cropped object positions. This close crop contains a blue glazed barrel-tile roof beneath a diagonal gold-capped red ridge beam, with dense green tree foliage and warm brown branches behind it above the beam. Continue the ridge from LEFT exactly as a single straight coherent beam with unchanged thickness, slope, shadows and fine gold trim. Continue each blue tile row from LEFT with the same tile width, natural curvature, perspective, dark overlap seams and restrained painterly highlights. Continue the TOP green-and-yellow tree foliage and branch contours organically behind the beam, matching its leaf size and density. No new finials, cloud ornaments, buildings, loose objects or leaves on the roof. This is only a close roof fragment, never a whole building.
Image2 is sole full-map layout authority. Image3 is material and spring-festival architecture style only, not a coordinate crop. Images4 and5 are the approved Daoist Q painting style only; ignore all UI, words, characters and night scenery. Keep sharp native anchor geometry, object contours, lighting and texture scale; continue smoothly without a straight border, frozen rectangle, shifted joint or repeated objects. Gentle warm daylight, detailed painterly surfaces equally in focus. No characters, pots, text, UI, watermark, nighttime, distant blur or smeared upscaled pixels. Return only the finished exact 1254-square image.'''
    p=ZONE/'prompts'/f'{ident}.prompt.txt';assert not p.exists();p.write_text(prompt,encoding='utf-8')
    record={'id':ident,'worker':'repair_recover16','status':'imagegen_prepared','preparedAtUtc':now(),'tool':'image_gen.imagegen','actualModel':None,'parameters':{'prompt':prompt,'referenced_image_paths':[v['file'] for v in refs],'transparent_background':False},'rules':{'agentsSha256':sha(ROOT/'AGENTS.md'),'splitSha256':sha(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')},'formalAccepted':False}
    write(ZONE/'qa/r06_c12-recovery-progress-20261016.json',record)
    print(json.dumps(record['parameters'],ensure_ascii=False))
elif sys.argv[1]=='finalize':
    tid='r06_c12';review=ZONE/'qa/r06_c12-continued-v1-20261016-review.json';q=read(review)
    notes={
        'cross-1-1':'Stone slab joints, narrow golden joint edges and surface pattern continuous through crossing.',
        'cross-1-2':'Paving joint endpoints and lower foliage contour align through crossing.',
        'cross-1-3':'Diagonal paving seams and stone texture scale remain coherent at crossing.',
        'cross-2-1':'Tree branch and leaf contours join without rectangular edge or duplicate branch.',
        'cross-2-2':'Central trunk and surrounding foliage flow continuously across crossing.',
        'cross-2-3':'Paving, foliage contour and tree shadows meet without offset.',
        'cross-3-1':'Branch network, foliage and cropped gold curved eave retain continuous geometry.',
        'cross-3-2':'Gold-red ridge, decorative cloud edge and blue barrel tiles join continuously.',
        'cross-3-3':'Leaf clusters, branches and partial gold ridge remain continuous through crossing.'}
    for it in q['items']:
        assert sha(it['file'])==it['sha256']
        if it['kind']=='cross':
            key=Path(it['file']).stem.removesuffix('-100pct');it.update(status='passed_visual_review_native100pct',note=notes[key],reviewedAtUtc=now())
    q.update(passedCount=49,pendingCount=0,failedCount=0,internalReview='passed16core24seam9cross_native1to1',wholeTileLayoutReview='passed against original full-map layout and local context; daylight pavement, trees, cropped roof position retained',formalAccepted=False,updatedAtUtc=now());write(review,q)
    full=Path(q['candidatePath']);p=full.with_suffix('.png.derivation.json');d=read(p)
    d.update(status='complete_native_coverage_internal_QA_passed_external_pending',internalReview=q['internalReview'],reviewRecord=review.as_posix(),externalSeams='top4096 boundary passed; left/right/bottom pending neighbor availability',formalAccepted=False,updatedAtUtc=now());write(p,d)
    p=ZONE/f'selection-{tid}.json';s=read(p);s.update(selectionIsPartialCandidate=False,candidateSha256=sha(full),nativeCoreCount=16,internalReview=q['internalReview'],reviewRecord=review.as_posix(),externalReview='top4096 passed; left/right/bottom pending',formalAccepted=False,pendingIssues=[],updatedAtUtc=now());write(p,s)
    p=ZONE/'qa/r06_c12-recovery-progress-20261016.json';record=read(p);record.update(status='completed_native_tile_internalQA_passed',inFlight=None,nativeCoreCount=16,candidatePath=full.as_posix(),candidateSha256=sha(full),reviewRecord=review.as_posix(),qaPassed=49,formalAccepted=False,externalPending=q['externalPending'],updatedAtUtc=now());write(p,record)
    p=ZONE/'qa/r06_c12-continued-progress-20261013.json';record=read(p);record.update(status='completed_native_tile_internalQA_passed',inFlight=None,selectedCoreCount=16,candidatePath=full.as_posix(),candidateSha256=sha(full),reviewRecord=review.as_posix(),qaPassed=49,formalAccepted=False,updatedAtUtc=now());write(p,record)
    print(json.dumps({'candidatePath':full.as_posix(),'sha256':sha(full),'qaPassed':49,'formalAccepted':False,'review':review.as_posix()}))
