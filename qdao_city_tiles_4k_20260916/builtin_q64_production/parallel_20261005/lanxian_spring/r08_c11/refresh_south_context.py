"""Prepare exact south context and inspect shared southwest guide ownership."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image

OUT=Path(__file__).resolve().parent
BASE=OUT.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,obj):
    p=Path(p);assert p.resolve().is_relative_to(OUT)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p,role=None):
    p=Path(p);obj={'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
    if role:obj['role']=role
    if p.suffix.lower()=='.png':obj['pixels']=list(Image.open(p).size)
    return obj
NOW=datetime.now(timezone.utc).isoformat()
prep=read(OUT/'preparation.json')
west_manifest=BASE/'r08_c10/selected-v2/delivery.manifest.json'
south_manifest=BASE/'r09_c11/selected/delivery.manifest.json'
wm=read(west_manifest);sm=read(south_manifest)
assert sm['qualifiedComplete4KCandidate'] and sm['tile']=='r09_c11'
assert sha(south_manifest)=='098734aab55fc12d0bbfe96be06155b0755be16261dcf9f923cb19ab9cbcaf26'
ws=wm['outputs']['extended4326.png'];ss=sm['outputs']['extended']
assert sha(ws['file'])==ws['sha256'] and sha(ss['file'])==ss['sha256']
west=Image.open(ws['file']).convert('RGB');south=Image.open(ss['file']).convert('RGB')
assert west.size==south.size==(4326,4326)
strip=south.crop((0,0,4326,230))
strip_path=OUT/'guides/south-r09_c11-exact4326x230.png';strip.save(strip_path)
strip_rec={**info(strip_path,'Native south boundary context; exact crop, not final r08_c11 art'),'createdAtUtc':NOW,'newAIGeneration':False,'actualModel':None,'actualQuality':None,'derivedFrom':[info(ss['file'],'Selected r09_c11 native extended image'),info(south_manifest,'Current selected delivery manifest after cleanup')],'operation':'Exact crop without resampling','sourceCropLTRB':[0,0,4326,230],'targetExtendedLTRB':[0,4096,4326,4326],'wholeCityExtentLTRB':[40845,32653,45171,32883],'nativePixelContext':True,'productionPixelsAllowed':False,'neighborCoreInsideStripLTRB':[115,115,4211,230],'provisionalNeighborHaloInsideStripLTRB':[0,0,4326,115],'formalAccepted':False}
write(str(strip_path)+'.derivation.json',strip_rec)
wa=np.asarray(west.crop((4096,4096,4326,4326)))
sa=np.asarray(strip.crop((0,0,230,230)))
def metrics(a,b):
    d=np.abs(a.astype(np.int16)-b.astype(np.int16))
    return {'pixelsCompared':int(a.shape[0]*a.shape[1]),'equalPixels':int(np.all(d==0,axis=2).sum()),'meanAbsRGB':d.mean(axis=(0,1)).tolist(),'maxAbsRGB':d.max(axis=(0,1)).tolist()}
choice=sa.copy();choice[:115]=wa[:115]
paths={}
for name,arr in [('from_west',wa),('from_south',sa),('owner_split_at_target_y4211',choice)]:
    p=OUT/'qa'/f'southwest_corner_{name}_230.png';Image.fromarray(arr).save(p);paths[name]=info(p)
sheet=Image.new('RGB',(690,230))
for i,arr in enumerate((wa,sa,choice)):sheet.paste(Image.fromarray(arr),(i*230,0))
p=OUT/'qa/southwest-corner-comparison-native.png';sheet.save(p)
segments=Image.new('RGB',(1082,920))
for i in range(4):segments.paste(strip.crop((i*1082,0,min(4326,(i+1)*1082),230)),(0,i*230))
sp=OUT/'qa/south-context-four-unscaled-segments.png';segments.save(sp)
data={'createdAtUtc':NOW,'westSource':info(ws['file']),'southSource':info(ss['file']),'southManifest':info(south_manifest),'whole230Square':metrics(wa,sa),'quadrants':{},'nativeCornerImages':paths,'comparisonSheet':{**info(p),'layout':'left: west source; middle: south source; right: proposed ownership west upper115, south lower115','resized':False},'southNativeSegments':{**info(sp),'layout':'top to bottom = left to right four consecutive1082px segments; last2px black padding','resized':False},'actuallyViewed':False,'formalAccepted':False}
for name,box in [('west_core_upper_left',(0,0,115,115)),('two_neighbor_halos_upper_right',(115,0,230,115)),('southwest_diagonal_core_lower_left',(0,115,115,230)),('south_core_lower_right',(115,115,230,230))]:
    x0,y0,x1,y1=box;data['quadrants'][name]={'cornerLTRB':list(box),**metrics(wa[y0:y1,x0:x1],sa[y0:y1,x0:x1])}
write(OUT/'qa/southwest-corner-comparison.json',data)
write(OUT/'source-evidence/south-delivery.snapshot.json',sm)
print(json.dumps({'whole230Square':data['whole230Square'],'quadrants':data['quadrants'],'comparison':str(p)},ensure_ascii=False))
