import os
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
f=ROOT/'native'/'r10_c10_ov_h32_v01.png';m=read(ROOT/'prompts'/'r10_c10_ov_h32_v01.overlay.json');src=Path(m['candidate']);im=Image.open(src).convert('RGB');ni=Image.open(f).convert('RGB')
crop=[115,230,1139,1000];x0,y0=m['candidateCrop'][:2];dst=[x0+crop[0],y0+crop[1],x0+crop[2],y0+crop[3]];x,y,x1,y1=dst;im.paste(ni.crop(crop),(x,y));q=ROOT/'qa'/'wall-oct17'/'r10_c10_h32_roi';q.mkdir();entries=[]
for label,b in [('center',dst),('left',[x-180,y,x+180,y1]),('right',[x1-180,y,x1+180,y1]),('top',[x,y-180,x1,y+180]),('bottom',[x,y1-180,x1,y1+180])]:
 out=q/f'{label}.png';im.crop(b).save(out);entries.append({'kind':label,'file':str(out),'sha256':sha(out),'box':b,'status':'pending_visual_review'})
write(q/'review.json',{'source':str(f),'sourceSha256':sha(f),'candidate':str(src),'candidateSha256':sha(src),'sourceCrop':crop,'destinationBox':dst,'entries':entries,'operation':'exact unaltered native RGB rectangular subset, wholly within allowed core; no filtering or blending','formalAccepted':False,'status':'pending_visual_review'});print(q)
