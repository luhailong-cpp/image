import json,hashlib,statistics
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
# Manually chosen sole-column windows from visual inspection, used only as diagnostic observations, never alignment.
regions={'00':[605,690,900,970],'01':[610,700,900,975],'02':[665,750,900,975],'08':[555,680,895,980],'09':[575,690,900,985],'10':[555,665,890,975],'03':[305,350,920,980],'11':[285,325,920,985]}
items=[]
for n,(x1,x2,y1,y2) in regions.items():
 p=ROOT/'runtime/run/E'/f'{n}.png';a=Image.open(p).getchannel('A');vals=[]
 for x in range(x1,x2):
  occupied=[y for y in range(y1,y2) if a.getpixel((x,y))>=128]
  if occupied:vals.append(max(occupied))
 items.append({'frame':int(n),'file':p.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'manualSoleDiagnosticWindow':[x1,y1,x2,y2],'alphaThreshold':128,'sampledColumns':len(vals),'soleLowerEnvelopeY':{'min':min(vals) if vals else None,'median':statistics.median(vals) if vals else None,'max':max(vals) if vals else None},'use':'diagnostic only; does not move or fit image','phase':'toe-push candidate' if n in ['03','11'] else 'contact/weight-bearing candidate'})
data={'date':'2026-10-03','method':'Manual image inspection selects boot sole window, then read alpha>=128 lower contour to quantify it. These are not automatic global min pixels and never set individual registration. Median reference is still not contact proof.','commonRootTrial':[511.5,941.6875],'cameraMatrixAllEFrames':[[901/1024,0,61],[0,901/1024,97],[0,0,1]],'landmarks':items,'conclusion':'Observed support soles/toe tips lie near the common line but vary by pose/perspective. No individual frame translation or bbox rescale applied. Global root remains provisional; dynamic and client checks pending.'}
(ROOT/'review/run_E_ground_landmarks_20261003.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps([(x['frame'],x['soleLowerEnvelopeY']) for x in items]))

