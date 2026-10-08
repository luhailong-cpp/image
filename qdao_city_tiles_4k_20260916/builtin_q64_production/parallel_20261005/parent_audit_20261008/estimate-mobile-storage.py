from pathlib import Path
from statistics import mean,median
from datetime import datetime,timezone
import json,hashlib,math
R=Path(__file__).resolve().parent
source=R/'verified-current-index.json';d=json.loads(source.read_text(encoding='utf-8-sig'))
rows=[];per=[]
for a in d['appearances']:
 sizes=[]
 for e in a['entries']:
  p=Path(e['path']);size=p.stat().st_size;sizes.append(size)
  rows.append({'appearance':a['appearance'],'tile':e['tileId'],'file':str(p),'bytes':size,'expectedSha256':e['sha256'],'actualSha256':hashlib.sha256(p.read_bytes()).hexdigest()})
 per.append({'appearance':a['appearance'],'count':len(sizes),'bytes':sum(sizes),'averageBytes':mean(sizes),'minBytes':min(sizes),'maxBytes':max(sizes),'projected256Bytes':mean(sizes)*256})
sizes=[e['bytes'] for e in rows]
formats=[]
for name,b in [('RGB24_pixel_payload',4096**2*3),('RGBA32_GPU_payload',4096**2*4),('ASTC_4x4',math.ceil(4096/4)**2*16),('ASTC_6x6',math.ceil(4096/6)**2*16),('ASTC_8x8',math.ceil(4096/8)**2*16)]:
 formats.append({'format':name,'bytesPerTile':b,'bytesPer256':b*256,'bytesPer1792':b*1792,'resident9Bytes':b*9,'resident16Bytes':b*16,'resident25Bytes':b*25,'includesMipmaps':False})
report={'observedAtUtc':datetime.now(timezone.utc).isoformat(),'sourceIndex':str(source),'sourceIndexSha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sourceCount':len(rows),'allSourceShasMatch':all(e['expectedSha256']==e['actualSha256'] for e in rows),'PNG':{'measuredBytes':sum(sizes),'meanBytesPerTile':mean(sizes),'medianBytesPerTile':median(sizes),'minBytesPerTile':min(sizes),'maxBytesPerTile':max(sizes),'projected1792ByPooledMeanBytes':mean(sizes)*1792,'projected1792ByEqualAppearanceMeanBytes':sum(a['projected256Bytes'] for a in per),'rangeIfAllFilesEqualObservedMinOrMax':[min(sizes)*1792,max(sizes)*1792],'projectionLimitation':'Measured sample covers mostly central plazas/architecture; future textures and PNG entropy may differ. PNG file size is not the built mobile app size or GPU residency.'},'appearances':per,'theoreticalTexturePayloads':formats,'assumptions':['4096x4096 per tile;1792 total;256 per appearance','No mipmap payload, container/bundle overhead, patch duplicates or build compression included','ASTC formats are proposed alternatives, not currently implemented or quality-tested','Current Resources route includes all released resource assets in build; streaming reduces residency, not total offline storage','GPU fallback and real device peak memory require actual target builds'],'sources':rows,'references':['D:/work/mmorpg-client/Docs/CityTiles4K.md','https://docs.unity3d.com/6000.0/Documentation/Manual/texture-formats-reference.html','https://docs.unity3d.com/6000.0/Documentation/Manual/LoadingResourcesatRuntime.html','https://github.com/ARM-software/astc-encoder/blob/main/Docs/FormatOverview.md']}
(R/'mobile-storage-estimate.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:report[k] for k in ['sourceCount','allSourceShasMatch','PNG','appearances','theoreticalTexturePayloads']},ensure_ascii=False,indent=2))

