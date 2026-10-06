from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tools/deps'))
import cv2,numpy as np
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def arr(p):return np.array(Image.open(p).convert('RGB'))
def grey(a):return cv2.cvtColor(a,cv2.COLOR_RGB2GRAY)
def stats(v):return dict(min=float(np.min(v)),p10=float(np.percentile(v,10)),median=float(np.median(v)),p90=float(np.percentile(v,90)),max=float(np.max(v)))
h=json.loads((ROOT/'handoff.json').read_text(encoding='utf-8-sig'))
oldfile=Path(h['baselineCandidates'][2]['file']);rawfile=ROOT/'repairs/west/west4.png';targetfile=ROOT/'repairs/west/west4-target.png';currentfile=ROOT/'output/r09_c13/r09_c13.png'
old=arr(oldfile);raw=arr(rawfile);target=arr(targetfile);current=arr(currentfile)
left=old[2842:4096,3469:4096];leftsrc=raw[:,:627]
# Same Farneback settings as production, but only genuine old-left support is visible.
lf=cv2.calcOpticalFlowFarneback(grey(left),grey(leftsrc),None,.5,4,51,5,7,1.5,0)
lf=cv2.GaussianBlur(lf,(0,0),5)
prod=np.load(ROOT/'output/r09_c13/west4.flow.npy')
rows={}
for name,(y0,y1) in {'roof-endpoint':(934,1254),'roof-ridge':(934,1094),'roof-bottom':(1094,1254),'whole':(0,1254)}.items():
    rows[name]=dict(leftSupportFlowX=stats(lf[y0:y1,570:615,0]),leftSupportFlowY=stats(lf[y0:y1,570:615,1]),productionNewFirst8X=stats(prod[y0:y1,115:123,0]),productionNewFirst8Y=stats(prod[y0:y1,115:123,1]))
# Gradient NCC on small blocks entirely on the genuine old side; scan translations.
def grad(a):
    g=grey(a).astype(np.float32)
    return cv2.Sobel(g,cv2.CV_32F,1,0,ksize=3),cv2.Sobel(g,cv2.CV_32F,0,1,ksize=3)
rx,ry=grad(left);sx,sy=grad(raw)
matches=[]
for y0,y1 in [(930,1030),(1000,1100),(1075,1175),(1135,1235)]:
    x0,x1=492,600
    ra=np.stack([rx[y0:y1,x0:x1],ry[y0:y1,x0:x1]],axis=-1).ravel();ra=ra-ra.mean()
    scored=[]
    for dy in range(-16,17):
        for dx in range(-16,17):
            sb=np.stack([sx[y0+dy:y1+dy,x0+dx:x1+dx],sy[y0+dy:y1+dy,x0+dx:x1+dx]],axis=-1).ravel();sb=sb-sb.mean()
            score=float(np.dot(ra,sb)/(np.linalg.norm(ra)*np.linalg.norm(sb)+1e-9));scored.append((score,dx,dy))
    scored.sort(reverse=True)
    matches.append(dict(referenceBoxLTRB=[x0,y0,x1,y1],bestGradientNCC=scored[0][0],sampleOffsetDx=scored[0][1],sampleOffsetDy=scored[0][2],noShiftNCC=next(s[0]for s in scored if s[1:]==(0,0)),top5=scored[:5]))
# Native comparison crops, no resampling.
box=(427,934,827,1254)
pair=np.concatenate([left,current[2842:4096,:627]],axis=1)
for name,a in [('old-target',target),('raw-repair',raw),('current-merged',pair)]:
    p=OUT/f'{name}-endpoint.png';Image.fromarray(a).crop(box).save(p)
    (OUT/f'{name}-endpoint.png.generation.json').write_text(json.dumps(dict(file=str(p),sha256=sha(p),operation='native crop no resizing',cropLTRB=list(box),sourceGlobalOriginXY=[48525,35610],role='diagnostic_only_not_production'),indent=2)+'\n',encoding='utf-8')
np.save(OUT/'old-left-only.flow.npy',lf)
result=dict(createdAt=datetime.now(timezone.utc).isoformat(),sources=[dict(file=str(p),sha256=sha(p))for p in [oldfile,rawfile,targetfile,currentfile]],coordinateConvention='flow=(source sampling dx,dy): aligned(x,y)=raw(x+dx,y+dy); +dy samples lower source, shifting visible art up',oldSupportGlobalRectXYWH=[48525,35610,627,1254],productionFlowOriginInRawX=512,productionSharedEdgeX=115,rawSharedEdgeX=627,flowStats=rows,gradientNCC=matches,productionFilesModified=False)
(OUT/'measurement.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))
