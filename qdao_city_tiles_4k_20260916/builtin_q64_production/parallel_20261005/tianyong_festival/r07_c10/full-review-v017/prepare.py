from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(__file__).parent;T=D.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
cp=T/'source-checkpoint.json'
assert sha(cp)=='dee70ba07d307895b9dae299c4437dc46a1e481541898ece20075b143cee4de1'
c=json.loads(cp.read_text(encoding='utf-8'));s=c['fragment']
assert s['tile']=='r07_c10' and sha(s['file'])==s['sha256']
im=Image.open(s['file']).convert('RGBA');a=np.array(im)
assert im.size==(4096,4096) and np.all(a[:,:,3]==255)
(D/'source-checkpoint.json').write_bytes(cp.read_bytes())
index=[];covered=np.zeros((4096,4096),bool)
for r,y in enumerate([0,1280,2560],1):
 for col,x in enumerate([0,1280,2560],1):
  b=[x,y,x+1536,y+1536];p=D/f'full-r{r}-c{col}.png'
  im.crop(b).save(p);covered[y:y+1536,x:x+1536]=True
  index.append({'id':f'full-r{r}-c{col}','image':info(p),'tileLocalLTRB':b,'nativeScale':1,'pixels':[1536,1536]})
assert covered.all()
nr=T/'r07_c10/review-lower-two-rows-v1/visual-review.json';n=json.loads(nr.read_text(encoding='utf-8'))
old=np.array(Image.open(n['sourceImage']['file']).convert('RGBA'))
bottom=np.array(Image.open(c['bottom']['file']).convert('RGBA'))
assert np.array_equal(old[3712:],a[3712:])
assert hashlib.sha256(bottom.tobytes()).hexdigest()==n['derivedSouthPixelSha256']
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceCheckpoint':info(D/'source-checkpoint.json'),'source':s,'nativeScale':1,'everyPixelIncluded':True,'coveragePixels':int(covered.sum()),'opaquePixels':int((a[:,:,3]==255).sum()),'images':index,'standardSeams':[1024,2048,3072],'actualPlacementSeams':[909,1085,1139,1933,2109,2163,2957,3133,3187],'southBorderPriorQa':info(nr),'southBorderSource':c['bottom'],'southBorderCurrentTop384EqualPreviouslyReviewedR07':True,'southBorderCurrentBottomRgbaEqualsReviewedDerivedR08':True,'scalePolicy':'Nine exact1536x1536 source crops with256px overlaps; both axes begin0,1280,2560 and fully cover4096.'}
(D/'review-image-index.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'source':s,'coveragePixels':int(covered.sum()),'crops':9,'south384PriorExact':True,'r08SouthExact':True}))
