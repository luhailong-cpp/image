from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageChops
import hashlib, json

O=Path(__file__).resolve().parent;O.mkdir(parents=True,exist_ok=True);(O/'snapshots').mkdir(exist_ok=True)
Z=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northeast')
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,d):Path(f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
inputs=[]
def freeze(f):
    f=Path(f);raw=f.read_bytes();h=hashlib.sha256(raw).hexdigest();dst=O/'snapshots'/f.name;dst.write_bytes(raw)
    inputs.append({'file':f.as_posix(),'sha256':h,'snapshot':dst.as_posix()})
    return json.loads(raw.decode('utf-8-sig'))
captured=datetime.now(timezone.utc).isoformat();sel=freeze(Z/'selection-r05_c11.json')
f=Z/'tiles/r05_c11-localfinish-v3-20261016.png';oldf=Z/'tiles/r05_c11-continued-v2-20261013.png'
d=freeze(str(f)+'.derivation.json');qr=freeze(Z/'qa/r05_c11-localfinish-v3-20261016-review.json')
h=sha(f);assert h==d['sha256']==qr['sha256']=='4bfa9fc5ab25793c6bbd750c6da6ea66ede8dd083c9097fd9051ed1d8051a47d'
inputs.extend([{'file':f.as_posix(),'sha256':h},{'file':oldf.as_posix(),'sha256':sha(oldf)}])
candidate=Image.open(f).convert('RGB');old=Image.open(oldf).convert('RGB');assert candidate.size==old.size==(4096,4096)
diff=ImageChops.difference(candidate,old);bbox=diff.getbbox();assert bbox is not None
replay=Image.new('RGB',(4096,4096));native=[]
for j,s in enumerate(d['sources']+d['requiredOverlays']):
    source=s.get('file') or s.get('source');hh=sha(source);assert hh==s['sha256']
    inputs.append({'file':source,'sha256':hh});g=freeze(str(source)+'.generation.json')
    assert g['sha256']==hh
    with Image.open(source) as im:
        assert im.size==(1254,1254);crop=im.crop(s['coreCrop']).convert('RGB');replay.paste(crop,s['tileLocalPaste'])
    native.append({'id':s['id'],'file':source,'sha256':hh,'generationRecord':str(source)+'.generation.json',
       'dimensions':[1254,1254],'crop':s['coreCrop'],'tileLocalPaste':s['tileLocalPaste'],
       'kind':'base_core' if j<16 else 'native_overlay','actualModel':g.get('actualModel'),'actualQuality':g.get('actualQuality'),
       'tool':g.get('tool'),'route':g.get('route'),'resampled':False})
assert replay.tobytes()==candidate.tobytes()
inspection=[]
for q in qr['inspectedCrops']:
    hh=sha(q['file']);assert hh==q['sha256'];inputs.append({'file':q['file'],'sha256':hh})
    with Image.open(q['file']) as im:assert im.convert('RGB').tobytes()==candidate.crop(q['candidateCrop']).tobytes()
    e=dict(q);e.update({'exactV3PixelsVerifiedThisAudit':True,'reviewedThisAudit':False,
        'kind':'core' if Path(q['file']).name.startswith('core') else 'cross' if Path(q['file']).name.startswith('cross') else 'seam'})
    inspection.append(e)
assert len(inspection)==49
assert sum(x['kind']=='core' for x in inspection)==16
assert sum(x['kind']=='seam' for x in inspection)==24
assert sum(x['kind']=='cross' for x in inspection)==9
perimeters=[]
for q in qr['repairPerimeterChecks']:
    hh=sha(q['file']);assert hh==q['sha256'];inputs.append({'file':q['file'],'sha256':hh})
    with Image.open(q['file']) as im:assert im.convert('RGB').tobytes()==candidate.crop(q['candidateCrop']).tobytes()
    e=dict(q);e.update({'exactV3PixelsVerifiedThisAudit':True,'reviewedThisAudit':False});perimeters.append(e)
edges=[]
for q in qr['externalBoundarySegments']:
    hh=sha(q['file']);assert hh==q['sha256'];nh=sha(q['neighbor']);assert nh==q['neighborSha256']
    inputs.extend([{'file':q['file'],'sha256':hh},{'file':q['neighbor'],'sha256':nh}])
    with Image.open(q['file']) as cut:
        cut=cut.convert('RGB');w,he=cut.size;idx=q['segment']-1
        with Image.open(q['neighbor']) as nb:
            nb=nb.convert('RGB')
            if q['side']=='top':
                assert w==1024
                im=Image.new('RGB',(w,he));im.paste(nb.crop((idx*1024,4096-he//2,(idx+1)*1024,4096)),(0,0))
                im.paste(candidate.crop((idx*1024,0,(idx+1)*1024,he//2)),(0,he//2))
                same=old.crop((idx*1024,0,(idx+1)*1024,he//2)).tobytes()==candidate.crop((idx*1024,0,(idx+1)*1024,he//2)).tobytes()
            else:
                assert he==1024
                im=Image.new('RGB',(w,he));im.paste(candidate.crop((4096-w//2,idx*1024,4096,(idx+1)*1024)),(0,0))
                im.paste(nb.crop((0,idx*1024,w//2,(idx+1)*1024)),(w//2,0))
                same=old.crop((4096-w//2,idx*1024,4096,(idx+1)*1024)).tobytes()==candidate.crop((4096-w//2,idx*1024,4096,(idx+1)*1024)).tobytes()
            assert im.tobytes()==cut.tobytes(),q['file']
    e=dict(q);e.update({'exactCurrentV3AndNeighborPixelsVerified':True,'v3SideIdenticalToV2':same,'reviewedThisAudit':False});edges.append(e)

evidence=[]
def save_crop(name,box,im=candidate):
    out=O/name;im.crop(box).save(out)
    evidence.append({'id':out.stem,'file':out.as_posix(),'sha256':sha(out),'dimensions':[box[2]-box[0],box[3]-box[1]],
       'candidateCrop':box,'source':f.as_posix() if im is candidate else oldf.as_posix(),'resized':False,'actuallyViewed':False})
box=[max(0,bbox[0]-128),max(0,bbox[1]-128),min(4096,bbox[2]+128),min(4096,bbox[3]+128)]
save_crop('v3-changed-region-and-perimeters-100pct.png',box)
save_crop('v2-same-region-before-100pct.png',box,old)
save_crop('v3-old-focus-junction-x3072-y1024-100pct.png',[2816,768,3328,1280])
# Two exact unscaled boards contain the four outer edges of each adopted native repair.
for prefix,items in [('large-repair',perimeters[:4]),('micro-gap',perimeters[4:])]:
    # Preserve source aspect and dimensions, no resampling. Four panels in rows.
    with_images=[Image.open(q['file']).convert('RGB') for q in items]
    w=max(im.width for im in with_images);height=sum(im.height for im in with_images)
    im=Image.new('RGB',(w,height),(40,40,40));y=0
    for ci in with_images:im.paste(ci,(0,y));y+=ci.height
    ff=O/f'{prefix}-four-perimeters-100pct.png';im.save(ff)
    evidence.append({'id':ff.stem,'file':ff.as_posix(),'sha256':sha(ff),'dimensions':list(im.size),
       'panels':[q['file'] for q in items],'resized':False,'actuallyViewed':False})
for side in ['top','right']:
    for q in edges:
        if q['side']==side and ((side=='top' and q['segment']==4) or (side=='right' and q['segment']<=2)):
            evidence.append({'id':f'external-{side}-{q["segment"]}-100pct','file':q['file'],'sha256':q['sha256'],
                'external':True,'side':side,'segment':q['segment'],'resized':False,'actuallyViewed':False})

summary={'capturedAtUtc':captured,'status':'frozen_v3_pixel_audit_passed_visual_pending','tileId':'r05_c11',
 'candidate':{'file':f.as_posix(),'sha256':h,'dimensions':[4096,4096],'formalAccepted':False},
 'baselineV2':{'file':oldf.as_posix(),'sha256':sha(oldf)},'differenceBoundingBox':list(bbox),
 'worldDifferenceBoundingBox':[bbox[0]+40960,bbox[1]+16384,bbox[2]+40960,bbox[3]+16384],
 'v2V3OutsideDifferenceBoxIdentical':True,'selectionCaptured':sel,
 'selectionCurrentlyPointsToFrozenV3':sel.get('candidatePath')==f.as_posix(),
 'candidateReconstructionExact':True,'nativeBaseCoreCount':16,'nativeRepairOverlayCount':2,'nativeSources':native,
 'internalQAItems':inspection,'perimeterQAItems':perimeters,'externalBoundarySegments':edges,
 'visualEvidence':evidence,'inputs':inputs,'productionWrites':0,'generationCallsThisAudit':0,'gitOperations':0,
 'actualModel':None,'actualModelNote':'Existing built-in source records returned no actual model/quality; production historical calls remain source evidence only.'}
write(O/'summary.json',summary)
print(json.dumps({'candidate':summary['candidate'],'differenceBoundingBox':bbox,'internalCounts':{k:sum(x['kind']==k for x in inspection) for k in ['core','seam','cross']},
   'perimeters':len(perimeters),'externalSegments':len(edges),'evidence':[(Path(x['file']).name,x.get('dimensions')) for x in evidence]},ensure_ascii=False))
