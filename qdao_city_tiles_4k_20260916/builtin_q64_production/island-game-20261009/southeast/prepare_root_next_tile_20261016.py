from workflow import *
from PIL import Image
tid='r08_c14';refs=read(ROOT/'references.json');first=patch(tid+'_p11');last=patch(tid+'_p44');box=[first['coreGlobalBox'][0],first['coreGlobalBox'][1],last['coreGlobalBox'][2],last['coreGlobalBox'][3]]
q=ROOT/'qa/r08_c14-start-20261016';q.mkdir(exist_ok=True);ref=Image.open(refs[0]['file']).convert('RGB');crop=[v*1254/57344 for v in box];out=q/'layout-only-tile.png'
if not out.exists():ref.transform((1024,1024),Image.Transform.EXTENT,tuple(crop),Image.Resampling.BICUBIC).save(out)
write(q/'layout-only-tile.json',{'globalBox':box,'layoutReference':refs[0],'layoutCrop':crop,'usableAsFinalArt':False})
p=ROOT/f'progress-{tid}.json'
if not p.exists():write(p,{'tile':tid,'owner':'root','status':'preparing','workingVersions':{},'generatedNativeCount':0,'inFlight':False,'pendingRepair':{},'actualModel':None})
print(out)
