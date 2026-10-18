from worker import *
t=B/'r12_c13';src=t/'qa'/'repair-candidate-v03.png';rp=t/'repairs'/'parasol-top-20261016-v01'/'native-v01.png';im=Image.open(src).convert('RGB');ri=Image.open(rp).convert('RGB');crop=[450,400,850,700];dest=[847,2333,1247,2633];im.paste(ri.crop(crop),tuple(dest[:2]));out=t/'qa'/'repair-candidate-v04.png';assert not out.exists();im.save(out)
write(t/'qa'/'repair-candidate-v04.json',{'path':str(out),'sha256':sha(out),'dimensions':[4096,4096],'base':str(src),'baseSha256':sha(src),'repair':str(rp),'repairSha256':sha(rp),'repairCrop':crop,'destinationBox':dest,'resized':False,'blended':False,'accepted':False,'status':'parasol geometry repair candidate; other seams pending'})
im.crop((797,2283,1297,2683)).save(t/'qa'/'parasol-v04-local.png')
