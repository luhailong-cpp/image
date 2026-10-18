from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
from datetime import datetime,timezone
Z=Path(r"D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/northwest");stem='r03_c01_middle_cliff_connected_20261016_a01'
def pin(p):
 p=Path(p);return dict(path=p.as_posix(),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
d=Z/'qa'/f'{stem}_mask_v1';m=json.loads((d/'mask_selection.json').read_text());ip=Z/'guides'/f'{stem}.input.json';inp=json.loads(ip.read_text())
native=Z/'native'/f'{stem}.png';gp=native.with_suffix('.png.generation.json');g=json.loads(gp.read_text())
base=Z/'tiles/r03_c01_candidate-v6_4096.png';rp=base.with_suffix('.native-repair.json')
assert pin(base)['sha256']=='0fad4d4bc608ad65dbbe8ca644e1649a470e48a5d0c9a190bbfe3b7d51514dbb'
assert pin(rp)['sha256']=='8004ae7308c53c8b69614ee91960310e10f573b942a42e28038bb318cee5b5cf'
l,t,r,b=inp['tileCropBox'];target=np.asarray(Image.open(m['target']['path']).convert('RGB'));raw=np.asarray(Image.open(native).convert('RGB'));combined=np.asarray(Image.open(m['combinedCrop']['path']).convert('RGB'));mask=np.asarray(Image.open(m['mask']['path']))
assert target.shape==raw.shape==combined.shape==(1254,1254,3)
assert np.array_equal(target,np.asarray(Image.open(base).convert('RGB'))[t:b,l:r])
assert set(np.unique(mask))=={0,255};sel=mask==255
assert np.array_equal(combined[sel],raw[sel]) and np.array_equal(combined[~sel],target[~sel])
yy,xx=np.nonzero(sel);local=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)];tile=[local[0]+l,local[1]+t,local[2]+l,local[3]+t]
assert tile[2]<=2275 and min(tile[:2])>=115 and max(tile[2:])<=4096-115
assert g['sha256']==pin(native)['sha256'] and g['actualModel'] is None and g['resizedAfterGeneration'] is False
report=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='/root/connected_continuation',operation='Exact native middle cliff local repair handoff; not applied to root tile',stem=stem,base=pin(base),baseRecord=pin(rp),input=pin(ip),cropDerivation=pin(inp['editTarget']['derivationRecord']['path']),raw=pin(native),generation=pin(gp),receipt=pin(g['evidence']['receipt']),prompt=pin(g['prompt']),mask=pin(m['mask']['path']),maskRecord=pin(d/'mask_selection.json'),combined=pin(m['combinedCrop']['path']),nativeDimensions=[1254,1254],cropBox=[l,t,r,b],selectionPixelCount=int(sel.sum()),selectionLocalBoxHalfOpen=local,selectionTileBoxHalfOpen=tile,sourcePixelReplay=True,editTargetEqualsPinnedBaseCrop=True,changesBeyondMask=False,rightMaskLimitTileX=2275,rightMaskLimitHonored=True,allOuter115Preserved=True,rootStateModified=False,appliedTo4096=False,ownerNativeVisualReview=dict(viewDetail='original',fullCombined1254Viewed=True,geometry='LOCAL_PASS',notes=['The former relatively straight blue strip on the middle cliff edge now has continuous sloping facets and a less rigid silhouette.','Upper coastline direction, lower rock ledge and adjacent vegetation remain in place; no new gap or abrupt edge at the mask boundary is visible.','Water, isolated rocks and main landmass outside the mask are retained exactly.']),independentReviewStatus='PENDING_ROOT_REVIEW',materialStatus='LOCAL_IMPROVED_NOT_FULL_TILE_ACCEPTANCE',formalAccepted=False,attemptNumber=1,actualModel=None)
p=d/'connected_owner_handoff.json';assert not p.exists();p.write_text(json.dumps(report,ensure_ascii=False,indent=2))
print(json.dumps({'handoff':pin(p),'raw':pin(native),'mask':pin(m['mask']['path']),'combined':pin(m['combinedCrop']['path']),'selectionTileBox':tile,'pixels':int(sel.sum())}))

