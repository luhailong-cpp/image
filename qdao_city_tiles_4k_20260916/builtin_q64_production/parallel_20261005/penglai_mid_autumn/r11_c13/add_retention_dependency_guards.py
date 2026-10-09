from pathlib import Path
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn')
for tile in ['r09_c15','r11_c13']:
 p=R/tile/'prepare_retention.py';s=p.read_text()
 s=s.replace("plan=dict(preparedAt=", """external_sources=list(m.get('currentNeighbors',{}).values())
if 'sharedDayStructure' in read(T/'plan.json'):external_sources.append(read(T/'plan.json')['sharedDayStructure'])
for src in external_sources:assert sha(src['file'])==src['sha256']
northproof=None
if tile_check := read(T/'plan.json').get('northScopedFreeze'):
 from PIL import Image
 import numpy as np
 northproof=tile_check.copy()
 north=Path(read(T/'plan.json')['northCandidate']);frozen=Path(tile_check['file'])
 assert np.array_equal(np.asarray(Image.open(north).convert('RGB'))[3776:],np.asarray(Image.open(frozen).convert('RGB')))
 northproof['frozen320MatchesCurrentNorthPixels']=True
plan=dict(preparedAt=""")
 s=s.replace("keep=keepitems,remove=remove,historicalExternalReferenceExemptions=", "keep=keepitems,remove=remove,protectedExternalSources=external_sources,northFreezePixelProof=northproof,historicalExternalReferenceExemptions=")
 p.write_text(s)

