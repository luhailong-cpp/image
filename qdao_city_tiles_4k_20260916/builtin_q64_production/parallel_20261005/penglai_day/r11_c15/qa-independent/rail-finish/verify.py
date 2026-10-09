from pathlib import Path
import json,hashlib,datetime
from PIL import Image
import numpy as np
O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
qa=O.parent
r=json.loads((qa/'qa-crops-source.json').read_text(encoding='utf8'))
src=Path(r['source']);assert sha(src)==r['sourceSHA256']
for crop in r['crops']:
 p=Path(crop['path']);im=Image.open(p)
 d={'file':str(p),'sha256':sha(p),'generatedAt':datetime.datetime.fromtimestamp(p.stat().st_mtime,datetime.timezone.utc).isoformat(),'width':im.width,'height':im.height,'format':im.format,'derivedFrom':[{'file':str(src),'sha256':sha(src),'generationRecord':str(src)+'.generation.json'}],'operation':{'method':'native integer QA crop','bbox':crop['bbox'],'resampling':False}}
 Path(str(p)+'.generation.json').write_text(json.dumps(d,indent=2),encoding='utf8')
m=json.loads((O/'merge-manifest-v1.json').read_text(encoding='utf8'))
assert sha(m['base'])==m['baseSHA256']
a=np.array(Image.open(O/'input.png'),np.float32);b=np.array(Image.open(m['replacement']),np.float32);alpha=np.array(Image.open(m['mask']),np.float32)/255;c=np.array(Image.open(m['composite']))
assert np.array_equal(c,np.rint(b*alpha[:,:,None]+a*(1-alpha[:,:,None])).astype('uint8'))
assert np.array_equal(c[alpha==0],a.astype('uint8')[alpha==0])
assert np.array_equal(a,np.array(Image.open(m['base']).crop((1600,2200,2854,3454))))
for p in O.glob('*.png'):
 rec=Path(str(p)+'.generation.json');assert rec.is_file(),p
 d=json.loads(rec.read_text(encoding='utf8'));assert d['sha256']==sha(p),(p,'sha')
 for ref in d.get('derivedFrom',d.get('references',[])):assert sha(ref['file'])==ref['sha256'],ref
 im=Image.open(p);d.update(width=im.width,height=im.height,format=im.format);rec.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
report={'verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'baseUnchanged':True,'exactCompositeReplay':True,'outsideMaskIdentical':True,'sourceCropMatchesBase':True,'localPngRecordsAndSHA':'all verified','previewOnly':False,'formalAccepted':False}
(O/'validation.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(report))

