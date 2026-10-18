from native_work import *
a=ZONE/'native/r03_c09_p04_01.png';b=ZONE/'native/r03_c09_p04_01_v2.png'
base=Image.open(a).convert('RGB');new=Image.open(b).convert('RGB');box=[115,115,1139,550]
base.paste(new.crop(box),(115,115));d=ZONE/'qa/root-p0401-upper-crop-20261016';d.mkdir(exist_ok=False)
base.save(d/'trial-native.png');base.crop((115,450,1139,650)).save(d/'lower-perimeter-100pct.png')
write(d/'inspection.json',{'base':str(a),'baseSha256':sha(a),'source':str(b),'sourceSha256':sha(b),'crop':box,'nativePaste':[115,115],'tileLocalPaste':[0,3072],'left':'external neighbor unavailable','top':'see p03_01_v2__p04_01_v2 existing actual join','right':'see p04_01_v2__p04_02 top435px existing actual join','bottom':'pending new lower-perimeter100pct review','noResampling':True,'formalAccepted':False})
print(str(d))

