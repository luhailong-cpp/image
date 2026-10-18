from PIL import Image
from pathlib import Path
import root_north_20261012 as n
b=n.b;Z=n.Z;p='r04_c12_roof-right-bridge01-v1'
old=Z/'guides'/f'{p}.native-target.png';new=Z/'native'/f'{p}.png'
a=Image.open(old).convert('RGB');x=Image.open(new).convert('RGB');box=[377,270,877,1100];a.paste(x.crop(box),tuple(box[:2]))
q=Z/'qa'/p;q.mkdir(exist_ok=True);f=q/'contribution-test.png';assert not f.exists();a.save(f)
items=[]
for side,bo in [('left',[249,270,505,1100]),('right',[749,270,1005,1100]),('top',[377,142,877,398]),('bottom',[377,972,877,1228])]:
 f=q/(side+'.png');assert not f.exists();a.crop(bo).save(f);items.append(dict(b.ref(f,'native1:1 insertion QA'),cropBox=bo))
n.atomic(q/'manifest.json',{'candidateTest':b.ref(q/'contribution-test.png','exact native bridge insertion test'),'sources':[b.ref(old,'original guide target'),b.ref(new,'native generated bridge')],'operation':'integer crop and opaque paste only','contributionBox':box,'qa':items,'visualReview':'pending','formalAccepted':False})
print(str(q))

