from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib, json, re
from PIL import Image

OUT = Path(__file__).resolve().parent
SESSION = OUT.parent.parent
PROD = SESSION.parent
BASE = PROD.parent
ROOT = BASE.parent
KEYS = ['tianyong_festival','penglai_day','penglai_mid_autumn','donghai_day','donghai_lantern','lanxian_day','lanxian_spring']

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def info(p):
    return {'file':str(p),'sha256':sha(p)}
def local(p):
    p = p.replace('\\','/')
    for old in ['E:/work/image','D:/luyuan/wuxingqitan/image']:
        if p.startswith(old+'/'):
            return ROOT / p[len(old)+1:]
    return Path(p)
def write(p,v):
    Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')

plans = []
batch = read(PROD/'current-batch.json')
for key in KEYS:
    p = BASE/'q64_production_plans'/f'{key}.json'
    d = read(p)
    tiles = d['tiles']
    assert len(tiles)==256
    assert {t['id'] for t in tiles}=={f'r{r:02}_c{c:02}' for r in range(1,17) for c in range(1,17)}
    for t in tiles:
        assert t['finalPixelRect']==[(t['column']-1)*4096,(t['row']-1)*4096,4096,4096]
    layout=BASE/'builtin_q64_all_city_references'/key/'map-native-layout-reference.png'
    candidates=[]
    for c in batch['candidates']:
        if c['appearance'] != key: continue
        f=BASE/c['file']; e={'tile':c['tile'],'file':str(f),'exists':f.exists(),'historicalExpectedSha256':c['sha256'],'formalAccepted':False}
        if f.exists():
            e.update(info(f)); e['shaMatches']=e['sha256']==c['sha256']; e['pixels']=list(Image.open(f).size)
        candidates.append(e)
    plans.append({'key':key,'plan':info(p),'displayNameHistorical':d['displayName'],'tileCount':256,'gridCoordinatesVerified':True,
                  'layout':{**info(layout),'pixels':list(Image.open(layout).size),'role':'layout/style only, not final HD'},
                  'historicalBatchCandidates':candidates})

all_png=[]; histogram=Counter(); raw_groups=defaultdict(list); larger_native_named=[]
for p in BASE.rglob('*.png'):
    if OUT in p.parents: continue
    with Image.open(p) as im: dims=list(im.size)
    histogram[f'{dims[0]}x{dims[1]}']+=1
    relative=p.relative_to(BASE).as_posix()
    entry={'file':str(p),'pixels':dims,'bytes':p.stat().st_size}
    all_png.append(entry)
    if p.parent.name=='native' and re.match(r'r\d{2}_c\d{2}(?:\..*)?\.png$',p.name):
        entry.update(info(p)); raw_groups[str(p.parent.parent)].append(entry)
    if ('native' in p.stem.lower() or p.parent.name=='native') and (dims[0]>1254 or dims[1]>1254):
        larger_native_named.append(entry)

dimension_records=[]; numeric_pairs=Counter(); requested_failures=[]
for p in BASE.rglob('*.json'):
    if OUT in p.parents or not (p.name.endswith('.record.json') or p.name.endswith('.generation.json') or p.name in ['record.json','generation.json']): continue
    try: d=read(p)
    except Exception: continue
    if not isinstance(d,dict): continue
    sizes={}
    for k in ['actualNativePixels','nativePixels','nativeSize','actualNativeSize','actualDimensions','outputDimensions','nativeDimensions']:
        value=d.get(k)
        if isinstance(value,list) and len(value)==2 and all(isinstance(x,(int,float)) for x in value): sizes[k]=value
    for a,b in [('nativeWidth','nativeHeight'),('actualWidth','actualHeight')]:
        if isinstance(d.get(a),(int,float)) and isinstance(d.get(b),(int,float)): sizes[a+'+'+b]=[d[a],d[b]]
    if d.get('tool')=='image_gen.imagegen' and not d.get('derivedFrom') and isinstance(d.get('width'),int) and isinstance(d.get('height'),int):
        sizes['width+height']=[d['width'],d['height']]
    if sizes:
        dimension_records.append({'file':str(p),'sizes':sizes,'role':d.get('role'), 'route':d.get('route')})
        for val in set(tuple(v) for v in sizes.values()):numeric_pairs[str(val)]+=1
    if d.get('nativeSizeRequestSatisfied') is False:
        requested_failures.append({**info(p),'requestedNativePixels':d.get('requestedNativePixels'),'actualNativePixels':d.get('actualNativePixels')})

groups=[]
for folder,files in raw_groups.items():
    ids=sorted({re.match(r'r\d{2}_c\d{2}',Path(f['file']).name).group() for f in files})
    groups.append({'directory':folder,'physicalRawFileCount':len(files),'distinctPatchCoordinates':ids,'coordinateCount':len(ids),
                   'hasAll16GridCoordinates':set(ids)>={f'r{r:02}_c{c:02}' for r in range(1,5) for c in range(1,5)},'files':files})

lanxian = PROD/'lanxian_day/r08_c09'
lp=read(lanxian/'plan.json')
readiness={'plan':info(lanxian/'plan.json'),'patches':[]}
for patch in lp['patches']:
    pid=patch['id'];guide=local(patch['guide']);f=lanxian/'native'/f'{pid}.png'
    record=lanxian/'native'/f'{pid}.record.json'
    item={'id':pid,'guideExists':guide.exists(),'guide':str(guide),'nativeExists':f.exists(),'native':str(f),'recordExists':record.exists()}
    if f.exists():
        item.update({'nativeSha256':sha(f),'nativePixels':list(Image.open(f).size)})
        if record.exists():item['nativeShaMatchesRecord']=item['nativeSha256']==read(record).get('outputSha256')
    readiness['patches'].append(item)
for k in ['motherSource','mother']:
    f=local(lp['guidePreparation'][k]);readiness[k]={'file':str(f),'exists':f.exists()}
neighbor=local(lp['leftNeighborBoundary']['file']);readiness['neighborExtended']={'file':str(neighbor),'exists':neighbor.exists()}
candidate=PROD/'lanxian_day/triple_r08_c06_c08/output_v2/r08_c08.png'
readiness['neighborCore']={**info(candidate),'pixels':list(Image.open(candidate).size),'canSupplyWestCore':True}

write(OUT/'inventory.json',{'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'scope':str(BASE),'sevenPlans':plans,
    'imageFileCount':len(all_png),'pngDimensionsHistogram':dict(histogram),'physicalNativePatchGroups':groups,
    'largerNativeNamedPhysicalImages':larger_native_named,'recordedNativeDimensionCounts':dict(numeric_pairs),
    'recordedLargerNativeDimensions':[x for x in dimension_records if any(a>1254 or b>1254 for a,b in x['sizes'].values())],
    'explicitSizeRequestFailures':requested_failures,'lanxianNextReadiness':readiness,
    'formalAccepted':False,'historicalMetadataDoesNotProveRetainedImage':True})
print(json.dumps({'pngFileCount':len(all_png),'physicalNativeGroups':[{k:g[k] for k in ['directory','coordinateCount','hasAll16GridCoordinates']} for g in groups],
    'recordedDimensions':dict(numeric_pairs),'largerNativeNamed':larger_native_named,'explicitSizeRequestFailures':requested_failures,
    'lanxianNextCount':sum(p['nativeExists'] for p in readiness['patches']),'lanxianGuidesPresent':sum(p['guideExists'] for p in readiness['patches'])},indent=2))
