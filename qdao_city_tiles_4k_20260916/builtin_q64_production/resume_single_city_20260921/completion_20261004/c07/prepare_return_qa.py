"""Native-pixel QA for the complete bounded color correction and its returns."""
from pathlib import Path
import hashlib, json
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent
O = R / 'tone-candidate-v1'
rec = json.loads((O / 'assembly.json').read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
p = Path(rec['candidate']['file'])
s = Path(rec['source']['file'])
assert sha(p) == rec['candidate']['sha256']
assert sha(s) == rec['source']['sha256']
image = Image.open(p).convert('RGB')
a = np.asarray(Image.open(s).convert('RGB'))
b = np.asarray(image)
assert a.shape == b.shape == (4096,4096,3)
Q = O / 'qa-returns'
Q.mkdir(exist_ok=True)
items = []
for axis in ('x', 'y'):
    for at in (1024,2048,3072):
        for seg in range(4):
            box = (at-256,seg*1024,at+256,(seg+1)*1024) if axis == 'x' else (seg*1024,at-256,(seg+1)*1024,at+256)
            view = image.crop(box)
            if axis == 'x':
                view = view.transpose(Image.Transpose.ROTATE_90)
            name = f'{axis}{at}-seg{seg+1}.png'
            view.save(Q / name)
            items.append({'file':str(Q/name),'sha256':sha(Q/name),'axis':axis,'at':at,'segment':[seg*1024,(seg+1)*1024], 'cropLTRB':list(box),'displayPixels':[1024,512],'losslessRotate90':axis=='x','resized':False,'coverage':'entire +/-192 correction strip plus 64 original pixels on both sides; other crossing strips may overlap'})
yy,xx = np.mgrid[:4096,:4096]
inside = np.zeros((4096,4096),dtype=bool)
for at in (1024,2048,3072):
    inside |= ((xx>=at-192)&(xx<at+192))|((yy>=at-192)&(yy<at+192))
delta = b.astype(np.int16)-a.astype(np.int16)
result = {'candidate':rec['candidate'],'source':rec['source'],'outsideAllCorrectionBandsUnchanged':bool(np.array_equal(b[~inside],a[~inside])),'outerBoundaryPixelsUnchanged':bool(all(np.array_equal(b.take(i,axis=ax),a.take(i,axis=ax)) for ax in (0,1) for i in (0,4095))),'maxStoredChannelDifference':int(np.max(np.abs(delta))),'changedPixels':int(np.any(delta,axis=2).sum()),'items':items,'visualReviewStatus':'awaiting_actual_view'}
assert result['outsideAllCorrectionBandsUnchanged'] and result['outerBoundaryPixelsUnchanged']
(Q/'index.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k not in ('items',)},ensure_ascii=False))
