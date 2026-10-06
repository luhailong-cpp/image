from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image

tile=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(im):return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
corep=tile/'candidate/core4096.png';core=Image.open(corep).convert('RGB')
assert sha(corep)=='0cefa2ece52b708f6b7021bfa878d466451cc1a0fd337cc9679754e949686c8b'
earlyp=tile/'early-vertical-qa/manifest.json';early=read(earlyp)
inherited=[]
for item in early['checks']:
    assert item['actualViewed'] is True
    assert rgb(core.crop(item['coreBox']))==item['decodedRgbSha256']
    inherited.append({'file':item['file'],'targetCoreBox':item['coreBox'],
        'decodedRgbSha256':item['decodedRgbSha256'],'pixelIdenticalToActuallyViewedCrop':True})
assert rgb(core.crop((0,0,4096,3072)))==early['canvasRawRGBSha256']
np=tile/'early-north-qa/review.json';north=read(np)
assert rgb(core.crop((0,0,4096,1024)))==north['topRowRawRGBSha256']
assert sha(Path(north['northSelected']['file']))==north['northSelected']['sha256']
notes={
 'internal_vertical_1_part4':'Shrub leaves, existing leaf shadow on orange planter cap and ivory wall are continuous; no artificial vertical stripe or severed contour at x1024.',
 'internal_vertical_2_part4':'Pale curved wall, adjacent post, water boundary and reflected rim remain connected at x2048. Bevel shades follow structure.',
 'internal_vertical_3_part4':'Bridge arch masonry and dark underside meet the water continuously at x3072. Reflections retain existing forms with no straight artificial strip.',
 'vertical_c2_r4':'Existing foliage and orange cap bevel continue through x1139; natural leaf shadow retained.',
 'vertical_c3_r4':'Pale post, submerged lower face and blue water reflection continuous at x2163.',
 'vertical_c4_r4':'Dark arch/water boundary and blue reflective surface coherent through x3187; no new foam or vertical guide band.',
 'vertical_c1_r1':'First-column x115 strip preserves original foliage/paving junction and grooves; no false guide boundary.',
 'vertical_c1_r2':'Quiet paving and diagonal groove continuous; low-contrast broad brush variation retained.',
 'vertical_c1_r3':'Original diagonal groove and rounded foliage preserve footprint; no sharp artificial strip.',
 'vertical_c1_r4':'Bright/dark rounded foliage continues naturally; no guide-generated vertical edge.'}
qa=read(tile/'qa/qa.manifest.json');guide=read(tile/'qa/guide-bands/manifest.json')
available={Path(v['file']).stem:v for v in qa['checks']+guide['checks']}
checks=[]
for name,note in notes.items():
    item=available[name];p=Path(item['file']);assert sha(p)==item['sha256']
    box=item.get('sourceBox',item.get('coreBox'))
    assert Image.open(p).convert('RGB').tobytes()==core.crop(box).tobytes()
    checks.append({'file':str(p),'sha256':sha(p),'coreBox':box,'actualViewed':True,
        'viewMethod':'tools.view_image(detail=original)','requiresRepair':False,'observation':note})
reports=[]
for relative in ('qa/remaining-horizontal-review.json','qa/outer-edge-review.json',
                 'early-horizontal-qa/manifest.json','early-north-qa/review.json','early-vertical-qa/manifest.json'):
    p=tile/relative;reports.append({'file':str(p),'sha256':sha(p)})
result={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root',
    'source':{'file':str(corep),'sha256':sha(corep)},'status':'all_exported_scopes_covered_no_required_repair_identified',
    'newRootOriginalPixelChecks':checks,'newRootOriginalPixelCount':10,
    'earlyVerticalReview':{'file':str(earlyp),'sha256':sha(earlyp),'inheritedActuallyViewedCount':24,
        'first3072RowsRawRgbIdentical':True,'cropProofs':inherited},
    'earlyNorthInheritance':{'report':str(np),'sha256':sha(np),'first1024RowsRawRgbIdentical':True,
        'northSelectedSourceUnchanged':True,'inheritedActuallyViewedCount':10,
        'ownNorthEdgeFourCropsCoveredAsExactBottomHalvesOfReviewedNorthJoinCrops':True},
    'overview':{'file':str(tile/'candidate/preview1024.png'),'sha256':sha(tile/'candidate/preview1024.png'),
        'actuallyViewed':True,'role':'Downsampled overview only; not native seam evidence',
        'observation':'Blank red/gold lantern, bridge, blue water and green bank preserve the regional composition and approved bright rounded painting. No obvious missing object or compositing stripe in overview.'},
    'coverage':{'standardNativeCrops':53,'guideBoundaryCrops':32,'externalNorthCrops':4,'exportedTotal':89,
        'actualOriginalPixelImagesViewedAcrossTeam':85,
        'differenceExplanation':'Four own-north edge exports are exact256-high halves already inspected inside the four512-high external north comparisons; no separate redundant views claimed.',
        'allExportedScopesCoveredByActualViewsAndByteIdentity':True},
    'reports':reports,'knownMinorResiduals':['Subtle material brush variation remains.','Two very small irregular highlights in native r01_c03 retained as painted bevel variation; no broken structural groove or guide-band defect identified.'],
    'unvalidated':['West/east/south adjacent tiles are not yet generated or jointly accepted.','Client loading/navigation and formal acceptance are not established.'],
    'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False}
out=tile/'qa/root-final-review.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'allScopesCovered':89,'reportSha256':sha(out)}))
