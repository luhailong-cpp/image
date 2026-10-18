from pathlib import Path
from PIL import Image,ImageChops
import json,hashlib
T=Path(__file__).resolve().parent;Q=T/'qa/banner-boundary-20261016'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=T/'candidates/r02_c14.banner-boundary-v7-20261016.png';assert sha(base)=='32f1273098e45159fdccd8f818f4df79ebb4e1cea05457f13316049080b5abf8'
src=T/'native/repairs/banner-boundary-v20261016-fix1.png';assert sha(src)=='67625264a2334674ab77bdfd26c79a61bff396e077a2257b29a6a8f17f1e8ea0'
bi=Image.open(base).convert('RGB');si=Image.open(src).convert('RGB');out=bi.copy();sr=[32,627,1222,1210];dr=[941,0,2131,583];out.paste(si.crop(sr),dr[:2])
dest=T/'candidates/r02_c14.banner-boundary-v8-20261016.png';assert not dest.exists();out.save(dest)
diff=ImageChops.difference(bi,out);diff.paste((0,0,0),dr);assert diff.getbbox() is None
for name,box in [('bottom',(877,455,2195,711)),('left',(813,0,1069,647)),('right',(2003,0,2259,647))]:out.crop(box).save(Q/('v8-'+name+'.png'))
north=Image.new('RGB',(1254,384));ni=Image.open(T.parent/'r01_c14/native/p42-v20261016.png').convert('RGB');north.paste(ni.crop((0,947,1254,1139)),(0,0));north.paste(out.crop((909,0,2163,192)),(0,192));north.save(Q/'v8-north-join.png')
meta={'base':str(base),'baseSha256':sha(base),'source':str(src),'sourceSha256':sha(src),'sourceROI':sr,'destinationROI':dr,'candidate':str(dest),'candidateSha256':sha(dest),'outsideROIIdentical':True,'operation':'integer native crop-paste only; no resampling blending or painting','nativeEditAttempt':1,'status':'awaiting_boundary_review'}
(Q/'composition-v8.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))

