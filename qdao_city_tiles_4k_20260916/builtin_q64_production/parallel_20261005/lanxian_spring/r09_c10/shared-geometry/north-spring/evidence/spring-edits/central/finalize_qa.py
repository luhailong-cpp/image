from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
rec=read(OUT/'composition-record.json')
base=np.asarray(Image.open(rec['dayBase']['file']).convert('RGB'))
result=np.asarray(Image.open(OUT/'edited-core4096.png').convert('RGB'))
mask=np.asarray(Image.open(OUT/'alpha-mask-core4096.png'))
assert sha(rec['dayBase']['file'])==rec['dayBase']['sha256']
assert np.array_equal(base[mask==0],result[mask==0])
assert not mask[:256].any() and not mask[-256:].any() and not mask[:,:256].any() and not mask[:,-256:].any()
back=rec['crops'][1]['sourceCrop']
checks=[]
for name,b in [('upper_square_cap',[1070,110,1210,240]),('upper_white_pillar',[1110,440,1220,670]),('lower_square_cap',[410,945,620,1090]),('white_stone_beam',[730,560,850,650])]:
 x1,y1,x2,y2=[b[0]+back[0],b[1]+back[1],b[2]+back[0],b[3]+back[1]]
 equal=np.array_equal(base[y1:y2,x1:x2],result[y1:y2,x1:x2]);assert equal,name
 checks.append({'name':name,'coreRectLTRB':[x1,y1,x2,y2],'byteEqual':True})
qa={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'central_surface_edit_visually_accepted',
 'actualNativeImagesViewed':['front-target-1254.png','back-target-1254.png','both builtin outputs inline','front-composited-1254.png','back-composited-1254.png','front-mask-overlay-1254.png','back-mask-overlay-1254.png','front-target-1254-cap-qa.png','front-generated-1254-cap-qa.png','front-composited-1254-cap-qa.png'],
 'actualOverviewViewed':'central-overview-qa.png (QA downsample only)',
 'findings':['Existing orange masonry surfaces are red lacquer with restrained thin warm-gold bevel accents; no new structure, caps, spheres or ornaments.',
 'The near front cap had leftover original pale-highlight flecks from the initial automatic mask. Compared target/generated/composited 280x250 actual-pixel crops; AI image was clean. One local cap polygon now uses those existing same-coordinate AI pixels, removing the flecks.',
 'Native front/back views and mask overlays reviewed. Tree trunk/roots, leaves, cream square caps, stone railing, paving and cast shadow retain the day geometry. No visible new clipped silhouette, hard color jump across the crop overlap, doubled contour or fake ground decoration.',
 'Some occluded inner planting-hole masonry stays in its original warm brown shading because the conservative tree/soil exclusion preserves that region; no navigable geometry changes.'],
 'oneLocalMaskCorrectionOnly':True,'noAdditionalAICallForHighlight':True,
 'savedPngOutsideMaskByteEqual':True,'wholeTileOuter256PixelsByteEqual':True,'whiteStoneSpotChecks':checks,
 'protectedGreenPixelsByteEqual':rec['protectedGreenPixelsByteEqual'],'protectedTreeAndSoilHoleByteEqual':rec['protectedTreeSoilHoleByteEqual'],
 'resampling':None,'warp':None,'localVisualAccepted':True,'formalTileAccepted':False,
 'finalRGBSHA256':sha(OUT/'edited-core4096.png'),'finalAlphaSHA256':sha(OUT/'alpha-mask-core4096.png'),
 'rootCompositionInstruction':'edited-core4096.png is already flattened onto the exact day base using the alpha. Copy its pixels wherever alpha-mask-core4096.png > 0 into the combined root candidate; do not alpha-blend it onto day a second time.'}
(OUT/'qa-review.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
rec['status']=qa['status'];rec['visualReview']={'file':str(OUT/'qa-review.json'),'sha256':sha(OUT/'qa-review.json'),'acceptedLocalEdit':True}
rec['rootCompositionInstruction']=qa['rootCompositionInstruction']
(OUT/'composition-record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':qa['status'],'rgb':qa['finalRGBSHA256'],'alpha':qa['finalAlphaSHA256'],'qaRecordSha256':sha(OUT/'qa-review.json')}))
