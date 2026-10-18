from worker import *
t=B/'r12_c13'; d=t/'repairs'/'parasol-top-20261016-v01';d.mkdir(exist_ok=True);src=t/'qa'/'repair-candidate-v03.png';p=d/'input.png';assert not p.exists();Image.open(src).crop((397,1933,1651,3187)).save(p);write(d/'coordinates.json',{'source':str(src),'sourceSha256':sha(src),'crop':[397,1933,1651,3187],'input':str(p),'size':[1254,1254],'nativeRepairPending':True})
