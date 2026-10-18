from pathlib import Path
import json,hashlib,subprocess,sys
from datetime import datetime,timezone
Z=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
qa=Z/'qa/assembly_r03_c01_candidate-v1_4096/qa_index.json'
items=json.loads(qa.read_text(encoding='utf-8-sig'))['seamAndJunctionCrops']
issues={
 'leaf_tip':dict(kind='geometry',atTile=[3070,2010],description='Yellow-green branch tips terminate unnaturally across the leaf/water/rock junction.',cropIndices=[5,19,29]),
 'cliff_edge':dict(kind='geometry',atTile=[2957,3300],description='Long ruler-straight cliff silhouette near x2957 should be checked and locally rounded without changing the coast layout.',cropIndices=[8,11,22,32]),
 'north_water':dict(kind='material',atTile=[2957,400],description='Visible vertical water tone boundary.',cropIndices=[2,26]),
 'upper_band':dict(kind='material',atTile=[1400,1139],description='Horizontal water texture/tone boundary around y1139 and a short vertical transition at x1933.',cropIndices=[3,4,12,13,14,24,25]),
 'mid_band':dict(kind='material',atTile=[1100,1933],description='Straight horizontal water tone boundary at y1933, strongest across left and middle ocean.',cropIndices=[6,7,16,17,18,27,28]),
 'south_water':dict(kind='material',atTile=[909,3600],description='Vertical water texture/tone discontinuity around x909.',cropIndices=[9,30])}
records=[]
for i,item in enumerate(items):
 p=Path(item['path']);assert sha(p)==item['sha256']
 ids=[k for k,v in issues.items() if i in v['cropIndices']]
 records.append(dict(index=i,**item,reviewedAtNativeScale=True,reviewer='root',geometry='REPAIR' if any(issues[k]['kind']=='geometry' for k in ids) else 'PASS',material='PENDING' if any(issues[k]['kind']=='material' for k in ids) else 'PASS',issueIds=ids,status='REPAIR' if ids else 'PASS'))
review=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),tileId='r03_c01',candidate=info(Z/'tiles/r03_c01_candidate-v1_4096.png'),assemblyRecord=info(Z/'tiles/r03_c01_candidate-v1_4096.assembly.json'),qaIndex=info(qa),nativeScaleCropsReviewed=33,reviewedCrops=records,issues=issues,internalClosurePassed=False,formalAccepted=False,operation='Human-visible model visual assessment; no generated pixel edits in this record')
dest=Z/'qa/r03_c01_v1_internal_review_20261016.json'
with dest.open('x',encoding='utf8') as f:json.dump(review,f,ensure_ascii=False,indent=2)
statepath=Z/'root-current-selection-20261012.json';state=json.loads(statepath.read_text(encoding='utf-8-sig'));entry=state['tiles']['r03_c01'];entry.update(internalReview=info(dest),internalClosurePassed=False,repairStatus='33/33 native crops reviewed; grouped foliage, cliff silhouette and water texture seams pending.');statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
jobs=[
 ('r03_c01_leaf_junction_20261016_a01',[2500,1400,3754,2654],'Repair ONLY the small foliage junction around local (570,610). The lower tips of the yellow-green branch currently end in an artificial rectangular/slashed edge over the water. Make these tips naturally terminate as separate pointed leaves and coherent fine stems connected into the existing bush. Preserve every surrounding rock, wall and blossom footprint, the water channel and perspective. Do not add a new trunk, branch mass or rock. Keep all other details unchanged.'),
 ('r03_c01_mid_water_left_20261016_a01',[0,1350,1254,2604],'Repair the water surface around the horizontal straight texture boundary at local y583 across the full width. Replace only the band local y370..790 with naturally continuous fine jade-teal waves matching both upper and lower existing water. Remove the straight rectangular stripe: no line, frame, fog, blur or smooth gradient band. Keep the overall water hue, current direction and native fine ripple detail. Keep top and bottom 250 pixels unchanged. No shore, objects, islands, sky, buildings or text.'),
 ('r03_c01_mid_water_center_20261016_a01',[1100,1350,2354,2604],'Repair the water surface around the horizontal straight texture boundary at local y583 across the full width. Replace only the band local y370..790 with naturally continuous fine jade-teal waves matching both upper and lower existing water. Remove the straight rectangular stripe: no line, frame, fog, blur or smooth gradient band. Preserve the existing few rocks at lower-right exactly, and their water reflection. Keep top and bottom 250 pixels unchanged. No added objects, islands, sky, buildings or text.'),
 ('r03_c01_south_water_20261016_a01',[350,2842,1604,4096],'Repair ONLY the vertical water texture/tone seam at local x559. Make the zone x360..760 a continuous finely hand-painted jade-teal sea matching the existing waves on both sides. Remove the ruler-straight vertical division without blur, a smooth overlay or a new stripe. Preserve any shoreline rocks at the right edge and their exact positions. Keep the outer left and right 250 pixels unchanged. No added objects, islands, sky, buildings or text.')]
for stem,box,task in jobs:
 subprocess.run([sys.executable,str(Z/'prepare_tile_repair_crop.py'),'--stem',stem,'--tile-id','r03_c01','--base',str(Z/'tiles/r03_c01_candidate-v1_4096.png'),'--base-record',str(Z/'tiles/r03_c01_candidate-v1_4096.assembly.json'),'--crop-box',*map(str,box),'--role','Primary edit target: exact unscaled 1254 native crop; keep its composition and coordinate alignment'],check=True,capture_output=True)
 prompt='Use case: precise-object-edit. Output exactly 1254 x 1254 pixels. Image 1 is the edit target at native scale. '+task+' Images 2 and 3 are layout/material references only; do not insert their buildings or landscape. Image 4 is Daoist Q hand-painted style only: never add UI, characters, writing or night lighting. Preserve bright daylight, the approved jade green and warm natural stone palette, all existing object scale and camera. No resize, crop, reframe, tilt, depth-of-field or soft-focus. Return only one complete full-frame edited bitmap.'
 (Z/'prompts'/f'{stem}.txt').write_text(prompt+'\n',encoding='utf8')
print(json.dumps(dict(review=info(dest),jobs=[x[0] for x in jobs])))
