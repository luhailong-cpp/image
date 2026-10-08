from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
import numpy as np
R=Path(__file__).resolve().parent;T=R/'r08_c16';D=T/'repairs/integrated-v1';F=T/'repairs/integrated-v5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(D/'candidate.png')=='019617ff62ad49c348bb9f8113800cf90c3516dd5295e96b09544c4fc519622a'
assert sha(F/'candidate.png')=='3e4a1a64a96d894531f6f1f7189287276b401e58f6805a9e6242c422e22b96de'
old=np.asarray(Image.open(D/'candidate.png'));new=np.asarray(Image.open(F/'candidate.png'))
rects={'west128':[0,0,128,4096],'nw':[0,0,512,512],'ne':[3584,0,4096,512],'sw':[0,3584,512,4096],'se':[3584,3584,4096,4096]}
ident=[]
for key,(x0,y0,x1,y1)in rects.items():
    x=old[y0:y1,x0:x1];y=new[y0:y1,x0:x1];assert np.array_equal(x,y)
    ident.append({'region':key,'rectXYXY':[x0,y0,x1,y1],'exactPixelIdentity':True,'rawRGBSha256':hashlib.sha256(y.tobytes()).hexdigest()})
names=['overview-preview-1024','corner-nw','corner-ne','corner-sw','corner-se','west-c15-c16-common-edge-full']
rec={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','actualVisualInspection':True,'viewedCandidateSha256':sha(D/'candidate.png'),'finalCandidateSha256':sha(F/'candidate.png'),'result':'pass for unchanged four corners and full west common edge','observations':['Blue canopy, connecting timber and hull edges continue across the complete west common edge.','Four native corners preserve clean materials without new edge truncations.','Initial integrated overview was viewed; its interior insertion-step issue was separately repaired in v5 and is outside this unchanged-region approval.'],'viewedSheets':[{'file':str(D/'qa/assembly'/f'{n}.png'),'sha256':sha(D/'qa/assembly'/f'{n}.png'),'nativePixelQA':not n.startswith('overview')} for n in names],'inheritanceBasis':ident,'southwestAndNorthwestIncludeFull512Square':True,'formalAccepted':False,'limitations':['Interior and insertion boundaries are reviewed separately.','No whole-city/client acceptance.']}
(F/'root-external-review.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Final external QA inherited only via verified exact pixels.')
