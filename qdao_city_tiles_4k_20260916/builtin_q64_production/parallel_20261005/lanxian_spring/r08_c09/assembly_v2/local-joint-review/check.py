from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image,ImageDraw,ImageFont
Q=Path(__file__).resolve().parent;OUT=Q.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
EXPECTED='a24f141b631eeefab13439339af7df0e1834a857d3c89c382b15380a603bb8a4'
candidate=OUT/'candidate_4096.png';assert sha(candidate)==EXPECTED
assembly=json.loads((OUT/'assembly.json').read_text());core=np.array(Image.open(candidate).convert('RGB'))
steps={s['patchId']:s for s in assembly['steps']};sources={s['patchId']:s for s in assembly['sources']}
box=(1126,1020,1146,1060);context=(1076,980,1196,1100);columns=[1125,1126,1130,1133,1138,1139,1145,1146]
panels=[('current',core[context[1]:context[3],context[0]:context[2]])];traces={};evidence=[]
for patch in ['r01_c01','r01_c02','r02_c01','r02_c02']:
    source=sources[patch];step=steps[patch];assert sha(source['file'])==source['sha256']
    raw=np.array(Image.open(source['file']).convert('RGB'))
    with np.load(step['actualRGBField']['file']) as z:field=z['rgbDelta'].astype(np.int16)
    l,t,r,b=step['sourceCrop'];corrected=np.clip(raw[t:b,l:r].astype(np.int16)+field,0,255).astype(np.uint8)
    x0,y0,x1,y1=step['canvasBox'];origin=(x0-115,y0-115)
    panel=np.full((120,120,3),80,np.uint8)
    for py in range(120):
        for px in range(120):
            sx=context[0]+px-origin[0];sy=context[1]+py-origin[1]
            if 0<=sx<corrected.shape[1] and 0<=sy<corrected.shape[0]:panel[py,px]=corrected[sy,sx]
    panels.append((patch,panel));trace={}
    for x in columns:
        sx=x-origin[0];top=box[1]-origin[1];bottom=box[3]-origin[1]
        trace[x]=int(np.argmin(corrected[top:bottom,sx].astype(np.float32).mean(axis=1))+box[1]) if 0<=sx<corrected.shape[1] else None
    traces[patch]=trace
    evidence.append({'patchId':patch,'native':source,'field':step['actualRGBField'],'actualOriginXY':step['actualOriginXY'],'coreCoverageX':[origin[0],origin[0]+corrected.shape[1]],'darkEdgeValleyYByCoreX':trace})
sheet=Image.new('RGB',(648,152),'#eeeeee');draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',15)
for index,(name,panel) in enumerate(panels):sheet.paste(Image.fromarray(panel),(index*132,32));draw.text((index*132+3,7),name,fill='black',font=font)
contact=Q/'source-comparison_1to1.png';sheet.save(contact)
current=Q/'current-region_1to1.png';Image.fromarray(core).crop((1039,940,1239,1140)).save(current)
step=steps['r02_c01'];alpha=np.array(Image.open(step['incomingAlpha']['file']))
x0,y0,_,_=step['canvasBox'];samples={x:int(alpha[1040+115-y0,x+115-x0]) for x in range(1133,1139)}
edges={name:hashlib.sha256(data.tobytes()).hexdigest() for name,data in {'westColumn':core[:,:1],'eastColumn':core[:,-1:],'west160Columns':core[:,:160],'east160Columns':core[:,-160:]}.items()}
result={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'candidateBeforeSha256':EXPECTED,'candidateAfterSha256':sha(candidate),
    'allowedCoreBoxLTRB':box,'actualChangedPixels':0,'applied':False,'status':'not_feasible_under_current_small_box_and_unwarped_source_constraints',
    'reason':'The left r02_c01 bevel is 4-5px below the right r01_c02 bevel, and r02_c01 ends at core x1139. Selecting r01_c02 throughout the allowed box relocates the break to x1126; the other two sources do not satisfy both boundaries. No new edge, smoothing, warp, resizing or widened edit was applied.',
    'maskParameters':{'requestedBox':box,'selectedSource':None,'appliedMask':None,'appliedAlpha':0,'maximumAllowedTransitionPixels':6,'rejectedActions':['move the discontinuity to the left box edge','blend 4-5px geometric disparity into a softened double edge','expand beyond the requested box']},
    'existingTerminationAlphaAtCoreY1040':samples,'currentEdgePixelHashes':edges,'nativeEvidence':evidence,
    'qa':[{'file':str(contact),'sha256':sha(contact),'resized':False},{'file':str(current),'sha256':sha(current),'resized':False}],
    'script':{'file':str(Path(__file__)),'sha256':sha(__file__)},'acceptedAsFixed':False}
(Q/'diagnosis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'traces':traces,'alpha':samples,'shaUnchanged':sha(candidate)==EXPECTED},indent=2))
