from pathlib import Path
from PIL import Image
import hashlib,json
import numpy as np
P=Path(__file__).resolve().parent;T=P.parent/'tools';Q=P/'references/latest-left-r09_c09-v6';Q.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
core=T/'repairs/versions/r09_c09_repair_v6/r09_c09.png';base=T/'neighbor_join_v5/output/extended-context.png'
assert sha(core)=='5ce3e9099c4292a3c2d2b854bcc6d2cfd3b8858bb6960bc8e7966699ade4742c'
im=Image.open(base).convert('RGB');im.paste(Image.open(core).convert('RGB'),(115,115));out=Q/'extended-context.png';assert not out.exists();im.save(out)
bottom=P.parents[1]/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/row10-extended-context.png'
a=np.array(im.crop((4096,4096,4326,4326)),dtype=np.int16);b=np.array(Image.open(bottom).convert('RGB').crop((12288,0,12518,230)),dtype=np.int16)
r={'role':'Latest left neighbor geometry with preserved v5 halo','core':{'path':str(core),'sha256':sha(core)},'baseExtended':{'path':str(base),'sha256':sha(base)},'output':{'path':str(out),'sha256':sha(out)},'corePasteXY':[115,115],'leftConstraintBoxLTRB':[4096,0,4326,4326],'bottomConstraint':{'path':str(bottom),'sha256':sha(bottom),'boxLTRB':[12288,0,16614,230]},'cornerPixels':[230,230],'cornerExactEqual':bool(np.array_equal(a,b)),'cornerMeanAbsoluteDifference':float(np.abs(a-b).mean()),'cornerMaxDifference':int(np.abs(a-b).max()),'fixedNeighborJoinAllowed':bool(np.array_equal(a,b))}
(Q/'record.json').write_text(json.dumps(r,indent=2),encoding='utf-8');print(json.dumps(r,indent=2))
