from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
OUT=Path(__file__).resolve().parent
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def savej(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p,role):
 with Image.open(p) as im:sz=list(im.size)
 return {'file':str(p),'sha256':sha(p),'pixels':sz,'role':role}
source=read(OUT/'source-crops.json');basepath=Path(source['source']['file'])
assert sha(basepath)==source['source']['sha256']
base=np.asarray(Image.open(basepath).convert('RGB')).copy()
support=Image.new('L',(4096,4096));d=ImageDraw.Draw(support)
# Conservative envelope of the existing orange masonry; excluded tree/soil hole below.
frontpoly=[(1330,1875),(1485,1697),(1640,1551),(1820,1605),(2070,1515),(2360,1640),(2480,1700),(2530,1870),(2400,2200),(2050,2648),(1328,2400)]
backpoly=[(2300,1400),(2875,1610),(2896,1700),(2600,2040),(2310,2250),(2100,2110),(2070,1660)]
d.polygon(frontpoly,fill=255);d.polygon(backpoly,fill=255)
holelocal=[(288,484),(407,287),(604,168),(639,0),(880,0),(859,130),(1130,335),(1068,398),(823,561),(775,545),(588,474),(443,516)]
hole=[(x+1200,y+1400) for x,y in holelocal]
d.polygon(hole,fill=0)
support_a=np.asarray(support)>0
support.save(OUT/'surface-envelope-and-tree-exclusion.png')
accum=np.zeros((4096,4096,3),np.float32);weights=np.zeros((4096,4096),np.float32)
crop_masks=[]
for c in source['crops']:
 name=c['name'];b=c['cropInCoreLTRB'];x,y,x2,y2=b
 src=base[y:y2,x:x2].astype(np.int16)
 gp=OUT/f'{name}-generated-1254.png';g=np.asarray(Image.open(gp).convert('RGB')).astype(np.int16)
 assert g.shape==(1254,1254,3)
 r,gg,bb=src[:,:,0],src[:,:,1],src[:,:,2]
 warm=(r>gg+8)&(gg>bb+6)
 # Only AI-created red paint transitions on existing warm orange surface pixels.
 red=(g[:,:,0]>g[:,:,1]*1.35)&(g[:,:,0]>g[:,:,2]*1.35)
 pigment_shift=(g[:,:,0]-g[:,:,1])-(r-gg)
 seed=warm&red&(pigment_shift>24)&((gg-g[:,:,1])>14)&support_a[y:y2,x:x2]
 expanded=np.asarray(Image.fromarray((seed*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)))>0
 # Expand four pixels within the original orange surface to include AI thin gold bevel lines.
 selected=expanded&warm&support_a[y:y2,x:x2]
 maskim=Image.fromarray((selected*255).astype(np.uint8))
 inward=np.asarray(maskim.filter(ImageFilter.MinFilter(3)))>0
 alpha=np.where(selected,np.where(inward,255,160),0).astype(np.uint8)
 # Original pale highlight on this visible orange cap was missed by the pigment gate.
 # Cover the inspected cap top/face at identical coordinates with the existing AI result.
 # This polygon stays inside orange masonry, away from foliage and the object silhouette.
 cap_override=[(618,744),(684,698),(799,740),(809,760),(807,831),(737,894),(622,849)]
 if name=='front':
  alpha_image=Image.fromarray(alpha);ImageDraw.Draw(alpha_image).polygon(cap_override,fill=255)
  alpha=np.asarray(alpha_image).copy()
 # More accurate front rendering owns its native span; crossfade only the shared orange surface.
 globalx=np.arange(x,x2,dtype=np.float32)[None,:]
 if name=='front':ownership=np.broadcast_to(np.clip((2454-globalx)/100,0,1),(1254,1254))
 else:ownership=np.broadcast_to(np.clip((globalx-2354)/100,0,1),(1254,1254)).copy()
 # Back can own pixels above the front crop, including the rear bar.
 if name=='back':ownership[:max(0,1400-y),:]=1
 w=ownership*(alpha.astype(np.float32)/255)
 accum[y:y2,x:x2]+=g.astype(np.float32)*w[:,:,None];weights[y:y2,x:x2]+=w
 Image.fromarray(alpha).save(OUT/f'{name}-surface-mask-1254.png')
 crop_masks.append({'name':name,'sourceCrop':b,'mask':info(OUT/f'{name}-surface-mask-1254.png','surface-only candidate alpha before overlap ownership')})
 config=Path('D:/work/image/config/image-generation.json');tool=read(OUT/f'{name}-tool-result.json')
 refs=[]
 for idx,p in enumerate(tool['submittedParameters']['referenced_image_paths']):
  roles=['exact native day selected crop, edit target','primary painting/material style only','Spring red/gold material only; same-object overlap on back request']
  refs.append(info(Path(p),roles[idx]))
 original=Path(tool['originalToolFile'])
 rec={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'useCase':'precise-object-edit','route':'builtin_image_gen',
  'tool':'image_gen.imagegen','configTarget':read(config),'configFile':str(config),'configSha256':sha(config),
  'submittedParameters':tool['submittedParameters'],'actualModel':None,'actualQuality':None,
  'unverifiedReason':'Builtin tool exposes no model or quality selectors and returns neither; config is only a target.',
  'startedAt':tool['startedAt'],'completedAt':tool['completedAt'],'toolMetadata':str(OUT/f'{name}-tool-result.json'),
  'originalToolFile':str(original),'originalToolSha256':sha(original),
  'originalToolModifiedAtUtc':datetime.fromtimestamp(original.stat().st_mtime,timezone.utc).isoformat(),
  'savedOutput':info(gp,'unaltered builtin returned native image'),'savedByteIdenticalToTool':sha(original)==sha(gp),
  'promptFile':str(OUT/f'{name}-prompt.txt'),'promptSha256':sha(OUT/f'{name}-prompt.txt'),
  'references':refs,'daySelectedSource':source['source'],'cropInCoreLTRB':b,'resampling':None,'warp':None}
 savej(OUT/f'{name}-generated-1254.png.generation.json',rec)
mask=np.rint(np.minimum(weights,1)*255).astype(np.uint8)
valid=weights>0
paint=base.copy();paint[valid]=np.rint(accum[valid]/weights[valid,None]).astype(np.uint8)
result=((paint.astype(np.uint32)*mask[:,:,None]+base.astype(np.uint32)*(255-mask[:,:,None])+127)//255).astype(np.uint8)
Image.fromarray(mask).save(OUT/'alpha-mask-core4096.png')
Image.fromarray(result).save(OUT/'edited-core4096.png')
outside=bool(np.array_equal(result[mask==0],base[mask==0]));assert outside
assert not np.any(mask[~support_a]);assert sha(basepath)==source['source']['sha256']
changed=np.any(result!=base,axis=2);ys,xs=np.where(changed)
green=(base[:,:,1]>base[:,:,0]*1.05)&(base[:,:,1]>base[:,:,2]*1.12)
assert not np.any(changed&green)
holemask=Image.new('L',(4096,4096));ImageDraw.Draw(holemask).polygon(hole,fill=255)
holea=np.asarray(holemask)>0;assert np.array_equal(result[holea],base[holea])
for c in source['crops']:
 x,y,x2,y2=c['cropInCoreLTRB'];name=c['name']
 Image.fromarray(result[y:y2,x:x2]).save(OUT/f'{name}-composited-1254.png')
 overlay=base[y:y2,x:x2].copy();localmask=mask[y:y2,x:x2]>0
 overlay[localmask]=(overlay[localmask].astype(np.float32)*0.4+np.array([255,0,200])*0.6).astype(np.uint8)
 Image.fromarray(overlay).save(OUT/f'{name}-mask-overlay-1254.png')
qa=(1200,1290,3000,2850)
Image.fromarray(result[qa[1]:qa[3],qa[0]:qa[2]]).resize((1200,1040),Image.Resampling.LANCZOS).save(OUT/'central-overview-qa.png')
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'status':'composited_pending_actual_visual_review',
 'dayBase':source['source'],'crops':crop_masks,'supportEnvelopePolygons':[frontpoly,backpoly],'protectedTreeAndSoilPolygon':hole,
 'maskMethod':'within explicit orange-entity envelope minus protected tree/soil hole: source warm-orange RGB gate; AI red-pigment-change seeds; grow4px only within eligible original warm-orange surface to include fine gold bevel;1px inward alpha160 edge. Inspected small front cap polygon includes original pale highlight to eliminate unpainted speckles using the existing AI pixels. Overlap ownership x2354..2454 blended native samples; no resampling/warp.',
 'manualHighlightCoverage':{'crop':'front','polygonCropLocal':cap_override,'polygonCore':[[x+1200,y+1400] for x,y in cap_override],'reason':'old pale highlight excluded by initial color gate looked like scraped paint; same-coordinate AI source is clean'},
 'sourceOrangeGate':'R>G+8 and G>B+6','AISeedGate':'generated R>1.35G and R>1.35B; delta(R-G)>24; originalG-generatedG>14',
 'resampling':None,'warp':None,'AIImageCount':2,'outputs':[info(OUT/'edited-core4096.png','RGB native edited core for root composition'),info(OUT/'alpha-mask-core4096.png','full-core alpha mask')],
 'outsideMaskByteEqual':outside,'noChangeOutsideEntityEnvelope':True,'protectedGreenPixelsByteEqual':True,'protectedTreeSoilHoleByteEqual':True,
 'sourceBaseFileUnchanged':True,'changedPixels':int(changed.sum()),'changedBBoxLTRB':[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)],
 'sourceSelectedEdgePixelsUnaffected':True,'previewOnlyResampling':'central-overview-qa.png only uses LANCZOS; not production',
 'formalAccepted':False,'visualReview':None}
savej(OUT/'composition-record.json',report)
print(json.dumps({'outputs':report['outputs'],'changedBBox':report['changedBBoxLTRB'],'changedPixels':report['changedPixels']}))
