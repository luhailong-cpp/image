"""Audit row 2/3 sources and actual viewing evidence without changing any pixels."""
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
import numpy as np
from PIL import Image

T = Path(__file__).resolve().parents[1]
N = T/'native'
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def anchor(p): return {'file':str(p),'sha256':sha(p)}
plan = read(T/'plan.json')
assert sha(T/'plan.json') == '6e5346045bd7a137aef880090b1ebb70415f0a05c83dedfdd02874d96d4d4de5'
assert sha(T/'guides/index.json') == plan['guideIndexSha256']
guide_index = {x['id']:x for x in read(T/'guides/index.json')['guides']}
reviews = {
 'p21':'Actual original1254 viewed. Rope-bound rail, post and ivory/coral fabric maintain layout; no new objects or zoom. Final actual west seam still requires assembly QA.',
 'p22':'Actual original1254 viewed. Timber post, diagonal rail, fabric and two rocks preserve placement. Water and foam have newly painted detail. Final north/left contour continuity unverified until assembly.',
 'p23':'Actual original1254 viewed. Cobalt water, foam, right-top cliff and bottom cropped timber remain at intended positions. No sky or horizon introduced. Native seam continuity pending assembly.',
 'p24':'Actual original1254 viewed. Cliff face, top/right foliage and curling foam retain silhouettes. Native seam continuity pending assembly.',
 'p31':'Actual original1254 viewed. Support timber and foreground plants retain layout. Fine straight tonal boundary persists near patch x115 in lower paving, approximately y950..1254; upper left foliage also deserves actual west seam inspection. Do not treat this native view as west seam approval.',
 'p32':'Actual original1254 viewed. Single warm lantern and support, ivory/coral cloth and left timber preserve composition. No duplicate lights. Native joins pending assembly.',
 'p33':'Actual original1254 viewed. Rope circles, timber post, cloth folds and water preserve intended structure. Native joins pending assembly.',
 'p34':'Actual original1254 viewed. Wood railing, rope wrap, cloth and water remain at intended scale and framing. Native joins pending assembly.'}
items=[]
for row in (2,3):
 for col in range(1,5):
    ident=f'p{row}{col}'
    p=N/(ident+'.png')
    reqp=N/(ident+'.request.json');callp=N/(ident+'.call.json');genp=N/(ident+'.png.generation.json')
    req,call,gen=read(reqp),read(callp),read(genp)
    assert sha(p)==gen['sha256']==gen['evidence']['sourceOutputSha256']==sha(gen['evidence']['sourceOutputPath'])
    assert req['submittedParameters']==gen['submittedParameters']
    submitted=dict(req['submittedParameters'])
    assert submitted.pop('model') is None and submitted.pop('quality') is None
    assert submitted==call and gen['actualModel'] is None and gen['actualQuality'] is None
    assert Path(req['prompt']).read_text(encoding='utf-8')==call['prompt']
    assert sha(req['prompt'])==req['promptSha256']==gen['promptSha256']
    assert req['references']==gen['references']
    assert [x['file'] for x in req['references']]==call['referenced_image_paths']
    for ref in req['references']: assert sha(ref['file'])==ref['sha256']
    guide=T/'guides'/(ident+'.png')
    assert sha(guide)==guide_index[ident]['sha256']
    expected=[plan['tile']['finalPixelRect'][0]-115+(col-1)*1024,plan['tile']['finalPixelRect'][1]-115+(row-1)*1024,1254,1254]
    assert req['globalPatchXYWH']==gen['globalPatchXYWH']==expected
    canvas=Image.new('RGBA',(1254,1254),(0,0,0,0))
    for region in req['contextRegions']:
        assert region['scale']==1 and sha(region['file'])==region['sha256']
        im=Image.open(region['file']).convert('RGBA')
        canvas.paste(im.crop(region['cropLTRB']),region['pasteXY'])
    assert np.array_equal(np.asarray(canvas),np.asarray(Image.open(N/(ident+'-context.png')).convert('RGBA')))
    target=Image.open(guide).convert('RGBA');target.alpha_composite(canvas)
    assert np.array_equal(np.asarray(target.convert('RGB')),np.asarray(Image.open(N/(ident+'-edit-target.png')).convert('RGB')))
    im=Image.open(p).convert('RGBA')
    assert im.size==(1254,1254) and im.getchannel('A').getextrema()==(255,255)
    assert gen['route']=='builtin' and not gen['sourceUpscaled'] and not gen['resizedAfterGeneration']
    items.append({**anchor(p),'id':ident,'pixels':[1254,1254],'actuallyViewed':True,'nativeScale':1,
        'targetGuideStyleActuallyViewedBeforeCall':True,'verdict':'native_detail_reviewed_pending_full_seam_QA',
        'review':reviews[ident],'provenancePassed':True,'generation':anchor(genp),
        'request':anchor(reqp),'call':anchor(callp),'contextSourceCount':len(req['contextRegions'])})
report={'createdAt':datetime.now(timezone.utc).isoformat(),'tile':'r09_c15','rows':[2,3],
    'worker':'/root/r09c14_row2_resume','frozenPlan':anchor(T/'plan.json'),'guideIndex':anchor(T/'guides/index.json'),
    'westSourceAtAudit':anchor(plan['westCandidate']),'westSourceHashMatchesFrozenPlan':sha(plan['westCandidate'])==plan['westCandidateSha256'],
    'nativeHelper':anchor(T.parent/'native_patch.py'),'allEightSaved':True,'allEightProvenancePassed':True,
    'actualModel':None,'actualQuality':None,'modelQualityEvidence':'Same batch target only; builtin has no exposed model/quality selector or returned value.',
    'items':items,'fullSeamQAStillRequired':True,'formalAccepted':False,'noPixelChangesByAudit':True,
    'pendingConcerns':[{'id':'p31-west-paving-tone-line','file':str(N/'p31.png'),
        'patchRegionApproxLTRB':[100,950,135,1254],'tileRegionApproxLTRB':[-15,2883,20,3187],
        'observation':'Fine vertical tonal boundary at actual west join around patch x115 remains visible in paving; top foliage at same west edge also needs native seam QA.',
        'parentNotified':True,'assembledVerdict':'unverified'}],
    'assemblyHold':'Parent instructed to await r09_c14 whole-source migration after separate southwest correction, although actual right-side reference pixels are to remain unchanged. No assembly output written.'}
out=T/'qa/native-rows23-review.json';assert not out.exists()
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(out),'sha256':sha(out),'allEightProvenancePassed':True,'pendingConcerns':len(report['pendingConcerns'])}))
