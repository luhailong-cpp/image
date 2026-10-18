from pathlib import Path
import json,hashlib,subprocess,sys
from PIL import Image
import numpy as np
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
di=Z/'qa/r03_c01_v5_internal_review/delta_index.json';d=json.loads(di.read_text())
for item in d['crops']:
 if item['unchanged']:
  item.update(geometry=item['prior']['geometry'],material=item['prior']['material'],issueIds=item['prior']['issueIds'],reviewMethod='same-hash previous native review')
 else:
  ids=[k for k in item['prior']['issueIds'] if k in ['upper_band','cliff_edge','north_water']]
  name=Path(item['path']).name
  if name=='left-right_r04_c01-c02_100pct.png':ids.append('south_water_lower_tail')
  if name=='left-right_r03_c02-c03_100pct.png':ids.append('middle_cliff_vertical_edge')
  item.update(status='REPAIR' if ids else 'PASS',geometry='REPAIR' if any(k in ['cliff_edge','middle_cliff_vertical_edge'] for k in ids) else 'PASS',material='PENDING' if any(k in ['upper_band','north_water','south_water_lower_tail'] for k in ids) else 'PASS',issueIds=ids,reviewMethod='root original-size full changed crop view')
review=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='root',candidate=d['base'],record=d['record'],deltaIndex=info(di),nativeCropCount=33,newlyViewed=17,sameHashReuse=16,crops=d['crops'],internalClosurePassed=False,formalAccepted=False,notes=['Leaf junction and middle horizontal water band locally resolved.','South water lower tail at x909 remains below first mask and can reuse existing raw source.','Long cliff silhouette edge at x2957 plus shorter edge at x1933 require native inspection/repair.','Upper water y1139 horizontal and x1933 vertical transition remain.'])
rp=Z/'qa/r03_c01_v5_internal_review/root_review.json'
with rp.open('x',encoding='utf8') as f:json.dump(review,f,indent=2)
# New mask selects only additional unmodified ancestor pixels; never overwrites the first adopted repair.
s='r03_c01_south_water_20261016_a01';out=Z/'qa'/f'{s}_mask_v2'
new=np.array(Image.open(out/'source_selection_mask.png'))==255;old=np.array(Image.open(Z/'qa'/f'{s}_mask_v1/source_selection_mask.png'))==255;extra=new&~old
mp=out/'additional_only_mask.png';Image.fromarray(extra.astype('uint8')*255).save(mp)
base=np.array(Image.open(Z/'tiles/r03_c01_candidate-v5_4096.png').convert('RGB'))[2842:4096,350:1604].copy();raw=np.array(Image.open(Z/'native'/f'{s}.png').convert('RGB'));base[extra]=raw[extra]
combined=out/'combined_current_v5_plus_extra_native_crop.png';Image.fromarray(base).save(combined)
(out/'additional_derivation.json').write_text(json.dumps(dict(operation='Additional binary mask = larger native source selection minus prior selected mask; unchanged same-coordinate pixels only',largerMask=info(out/'source_selection_mask.png'),priorMask=info(Z/'qa'/f'{s}_mask_v1/source_selection_mask.png'),additionalMask=info(mp),combinedCrop=info(combined),selectedPixelCount=int(extra.sum()),isAiGeneration=False,resizing=False,feathering=False,colorCorrection=False),indent=2)+'\n')
jobs=[
 ('r03_c01_upper_water_left_20261016_a01',[0,550,1254,1804],'Repair only the horizontal straight water texture boundary at local y589 across the full width. Replace the band y370..790 with naturally continuous finely drawn cyan-blue waves matching the existing tones on both sides. Remove the straight rectangular stripe, retain crisp fine ripples and light patterns. Keep top/bottom 250 pixels unchanged. No additional objects.'),
 ('r03_c01_upper_water_center_20261016_a01',[1100,550,2354,1804],'Repair the artificial rectangular water texture boundaries: horizontal at local y589 and vertical at local x833 beneath it. Make the water locally continuous in the horizontal band y370..790 and in a narrow vertical strip x700..970,y590..1200. Preserve the existing rocky shoreline at right exactly. Keep cyan-blue sea hue, fine crisp ripples, scale and lighting. No added rocks, objects or plants.'),
 ('r03_c01_north_water_20261016_a01',[2350,0,3604,1254],'Repair only the straight vertical water texture division at local x607 in the upper water. Make the narrow zone x430..770,y0..900 continuous naturally painted cyan-blue sea, with existing small ripples matching both sides. Preserve all rocks, plants, coastline and foam placement. Do not move any object or add new detail unrelated to the water seam.'),
 ('r03_c01_lower_cliff_edge_20261016_a01',[2350,2750,3604,4004],'Repair only the unnatural ruler-straight vertical cliff silhouette around local x607. The existing water channel and adjoining rock face are cut along a straight image boundary. Give the cliff edge a subtle natural irregular rounded outline and connect the existing nearby rock facets and water foam. Keep the channel open, same width and location, preserve large boulders, wall/rail posts, plants and all building geometry. Confine silhouette change to within 70 pixels of the present edge; no broad landscape changes. Keep the outer 115-pixel margin unchanged.')]
for stem,box,task in jobs:
 subprocess.run([sys.executable,str(Z/'prepare_tile_repair_crop.py'),'--stem',stem,'--tile-id','r03_c01','--base',str(Z/'tiles/r03_c01_candidate-v5_4096.png'),'--base-record',str(Z/'tiles/r03_c01_candidate-v5_4096.native-repair.json'),'--crop-box',*map(str,box),'--role','Primary native edit target: exact unscaled crop, preserve coordinate alignment'],check=True,capture_output=True)
 prompt='Use case: precise-object-edit. Output exactly 1254 x 1254 pixels. Image 1 is the edit target. '+task+' Images 2 and 3 are layout/material references only; do not insert their architecture or scene. Image 4 is Daoist Q hand-painted style only, never include UI, words, people or night lighting. Preserve bright daylight, palette, camera, frame, object scale and native crisp drawing. No resizing, reframe, blur, soft focus or depth of field. Return one complete edited bitmap.'
 (Z/'prompts'/f'{stem}.txt').write_text(prompt+'\n',encoding='utf8')
print(json.dumps(dict(review=info(rp),extraMask=info(mp),combined=info(combined),jobs=[x[0] for x in jobs])))
