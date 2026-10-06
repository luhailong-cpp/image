from PIL import Image, ImageDraw, ImageFilter
from pathlib import Path
import numpy as np, hashlib, json
from datetime import datetime, timezone

HERE=Path(__file__).resolve().parent
BASE=HERE.parent.parent
SOURCE=BASE/'selected/core4096.png'
EXPECTED='4c5410f54c977ac9122f2ce5237306d070e872171b7639ba4f3a67fae8db8e22'
BOX=(1900,1290,3154,2544)
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SOURCE)==EXPECTED
source=Image.open(SOURCE).convert('RGB')
target=source.crop(BOX)
generated=Image.open(HERE/'generated-1254.png').convert('RGB')
assert generated.size==target.size==(1254,1254)
polygons={
 'pillar':[(1062,729),(1146,750),(1185,764),(1193,790),(1193,868),(1178,878),(1132,876),(1070,861),(1030,848),(1036,827),(1063,810)],
 'leaf':[(131,1141),(155,1139),(180,1151),(211,1169),(229,1193),(230,1219),(203,1229),(164,1223),(131,1215)]
}
alpha=np.zeros((1254,1254),dtype=np.uint8)
mask_bounds={}
for name,points in polygons.items():
    mask=Image.new('L',(1254,1254),0)
    ImageDraw.Draw(mask).polygon(points,fill=255)
    layer=np.zeros((1254,1254),dtype=np.uint8)
    # Exactly five pixels of inward-only feather; mask never expands.
    for step in range(1,6):
        layer[np.array(mask)>0]=step*51
        mask=mask.filter(ImageFilter.MinFilter(3))
    alpha=np.maximum(alpha,layer)
    mask_bounds[name]=Image.fromarray(layer).getbbox()
mask=Image.fromarray(alpha)
composite=Image.composite(generated,target,mask)
repair=source.copy();repair.paste(composite,BOX[:2])
full_mask=Image.new('L',source.size,0);full_mask.paste(mask,BOX[:2])
repair.save(HERE/'repair-core4096.png')
full_mask.save(HERE/'alpha4096.png')
composite.save(HERE/'final-crop1254.png')
a=np.array(source);b=np.array(repair);m=np.array(full_mask)
changed=np.any(a!=b,axis=2)
assert not changed[m==0].any()
edge_checks={side:bool(np.array_equal(np.array(target)[s],np.array(composite)[s])) for side,s in {'top':(slice(0,16),slice(None)),'bottom':(slice(-16,None),slice(None)),'left':(slice(None),slice(0,16)),'right':(slice(None),slice(-16,None))}.items()}
assert all(edge_checks.values())
regions={'pillar':(995,700,1230,910),'leaf':(100,1110,265,1254)}
sheet=Image.new('RGB',(720,404),'#30343b');d=ImageDraw.Draw(sheet)
for idx,(name,box) in enumerate(regions.items()):
    y=26+idx*228
    d.text((8,y-18),name+' BEFORE / AFTER / MASK (native 1:1)',fill='white')
    for j,im in enumerate((target,composite,mask.convert('RGB'))):sheet.paste(im.crop(box),(8+j*240,y))
sheet.save(HERE/'qa-native.png')
for name,box in regions.items():composite.crop(box).save(HERE/('qa-'+name+'.png'))
now=datetime.now(timezone.utc).isoformat()
stats={'checkedAt':now,'sourceSha256':sha(SOURCE),'repairSha256':sha(HERE/'repair-core4096.png'),'alphaSha256':sha(HERE/'alpha4096.png'),'dimensions':[4096,4096],'cropBox':BOX,'generatedNativeSize':list(generated.size),'noResize':True,'noTranslation':True,'noRegistration':True,'outsideMaskChangedPixels':int(changed[m==0].sum()),'changedPixelCount':int(changed.sum()),'fullMaskBounds':full_mask.getbbox(),'cropMaskBounds':mask_bounds,'fourReturnBounds16pxUnchanged':edge_checks,'polygons':polygons,'feather':{'kind':'inward Chebyshev distance','widthPixels':5,'outwardExpansion':0,'imageBlur':False},'visualQA':'pending actual view of final native patches and four bounds'}
(HERE/'processing.json').write_text(json.dumps(stats,indent=2),encoding='utf-8')
print(json.dumps(stats))
