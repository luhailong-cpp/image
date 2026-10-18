from worker import *
t=B/'r12_c14';src=t/'qa'/'repair-candidate-v03.png';rp=t/'repairs'/'lantern-middle-20261016-v01'/'native-v01.png';im=Image.open(src).convert('RGB');ri=Image.open(rp).convert('RGB');crop=[115,115,1139,1139];dest=[2560,2135,3584,3159];im.paste(ri.crop(crop),tuple(dest[:2]));out=t/'qa'/'repair-candidate-v04.png';assert not out.exists();im.save(out)
write(t/'qa'/'repair-candidate-v04.json',{'path':str(out),'sha256':sha(out),'dimensions':[4096,4096],'base':str(src),'baseSha256':sha(src),'repair':str(rp),'repairSha256':sha(rp),'repairCrop':crop,'destinationBox':dest,'resized':False,'blended':False,'accepted':False,'status':'lantern repair candidate; perimeter and other seams pending'})
im.crop((2500,2080,3650,3220)).save(t/'qa'/'lantern-v04-local.png')
