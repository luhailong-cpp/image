from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parents[1];Q=T/'qa';Q.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
entries=[]
for cell in ['r04_c03','r04_c04']:
    p=T/'native'/f'{cell}.png';r=Path(str(p)+'.generation.json');d=read(r);s=read(T/'jobs'/f'{cell}.row04.source.json')
    d['sharedDayGeometrySource']=s;d['generationTimestampEvidence']='generatedAt is host tool completion timestamp; tool did not return its own clock.'
    d['officialVerification']={'checkedOn':'2026-10-05','source':'https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','finding':'most capable official image model; max quality listed; host selector unavailable'}
    d['formalAccepted']=False;d['crossAppearanceGeometryAccepted']=False;d['newComplete4KTiles']=0
    write(r,d)
    im=Image.open(p).convert('RGB');day=Image.open(s['daySource']).convert('RGB')
    arr=np.asarray(im).astype(np.int16);old=np.asarray(day).astype(np.int16);diff=np.abs(arr-old)
    roi=(0,0,600,450) if cell=='r04_c03' else (740,0,1254,175)
    x0,y0,x1,y1=roi;area=diff[y0:y1,x0:x1]
    entries.append({'cell':cell,'file':str(p),'sha256':sha(p),'generationRecord':str(r),'daySource':s['daySource'],'daySourceSha256':s['daySourceSha256'],
        'pixels':list(im.size),'changeMetricsDiagnosticOnly':{'fullMeanAbsRgb':float(diff.mean()),'groundRoiLTRB':list(roi),'groundMeanAbsRgb':float(area.mean()),'groundExactPixelFraction':float(np.all(area==0,axis=2).mean())},'acceptedAsFullTile':False})
a=Image.open(T/'native/r04_c03.png').convert('RGB');b=Image.open(T/'native/r04_c04.png').convert('RGB')
board=Image.new('RGB',(640,1254));board.paste(a.crop((819,0,1139,1254)),(0,0));board.paste(b.crop((115,0,435,1254)),(320,0))
f=Q/'row04-c03-c04-core-seam-native.png';board.save(f)
overlap=Image.new('RGB',(460,1254));overlap.paste(a.crop((1024,0,1254,1254)),(0,0));overlap.paste(b.crop((0,0,230,1254)),(230,0))
g=Q/'row04-c03-c04-overlap-side-by-side-native.png';overlap.save(g)
write(Q/'row04-review.json',{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'two native spring appearance edit candidates; no full tile or runtime acceptance',
    'entries':entries,'derivedQA':[{'file':str(f),'sha256':sha(f),'pixels':[640,1254],'operation':'crop/paste only','leftSourceCropLTRB':[819,0,1139,1254],'rightSourceCropLTRB':[115,0,435,1254],'seamAtX':320,'resized':False},
    {'file':str(g),'sha256':sha(g),'pixels':[460,1254],'operation':'side-by-side native overlap samples only, not a stitched image','leftSourceCropLTRB':[1024,0,1254,1254],'rightSourceCropLTRB':[0,0,230,1254],'resized':False}],
    'visualInspectionStatus':'pending','formalAccepted':False,'crossAppearanceGeometryAccepted':False,'fullTileCount':0})
print(json.dumps({'qa':str(Q/'row04-review.json'),'metrics':[e['changeMetricsDiagnosticOnly'] for e in entries]},indent=2))
