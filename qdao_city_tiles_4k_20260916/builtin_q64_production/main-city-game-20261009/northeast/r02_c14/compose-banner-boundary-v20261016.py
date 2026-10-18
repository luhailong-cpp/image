from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
Z=Path(__file__).resolve().parents[1];T=Z/'r02_c14';Q=T/'qa/banner-boundary-20261016';Q.mkdir(parents=True,exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=T/'candidates/r02_c14.local-repairs-v6-20261013.png';assert sha(base)=='ed97e9039fee126b238f1dbf45fea5d60f9c41a44db9714f2a50a006be054dcd'
src=Z/'r01_c14/native/p42-v20261016.png';assert sha(src)=='b3528fd18cd0fb7e85a407e7ff9f3494966daa907e56066b4ff3e14449bd5106'
bi=Image.open(base).convert('RGB');si=Image.open(src).convert('RGB');out=bi.copy()
sourceROI=[115,1139,1139,1254];destinationROI=[1024,0,2048,115]
out.paste(si.crop(sourceROI),(1024,0))
dest=T/'candidates/r02_c14.banner-boundary-v7-20261016.png';assert not dest.exists();out.save(dest)
outside=ImageChops.difference(bi,out);outside.paste((0,0,0),destinationROI);assert outside.getbbox() is None
north=Image.new('RGB',(1024,384));north.paste(si.crop((115,947,1139,1139)),(0,0));north.paste(out.crop((1024,0,2048,192)),(0,192));north.save(Q/'north-banner-join-v7.png')
out.crop((864,0,2208,307)).save(Q/'new-strip-left-right-bottom-v7.png')
bi.crop((864,0,2208,307)).save(Q/'prior-strip-left-right-bottom-v6.png')
meta={'base':str(base),'baseSha256':sha(base),'source':str(src),'sourceSha256':sha(src),'sourceROI':sourceROI,'destinationROI':destinationROI,'candidate':str(dest),'candidateSha256':sha(dest),'operation':'exact integer native halo crop and paste; no resampling blending or painting','outsideROIIdentical':True,'status':'awaiting_visual_boundary_review','internalPassed4kCount':0,'formalAcceptedCount':0}
(Q/'composition-v7.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta))

