from pathlib import Path
Z=Path(__file__).resolve().parents[1]
src=(Z/'refresh_live_progress_v2_20261016.py').read_text(encoding='utf-8-sig')
mark='# Current connected projections override older per-owner candidates only by explicit hash-bound manifest.'
block='''# Adopt only explicitly selected, hash-verified cores of the already active coast tile.
coast_state=Z/'connected-coast-current-selection-20261016.json'
if coast_state.exists():
 cc=read(coast_state);tile_id=cc['tileId'];assert tile_id=='r02_c01' and tile_id not in reserved
 cells=[];coords=set()
 for x in cc.get('selectedNative',[]):
  coord=(x['row'],x['col']);assert coord not in coords;coords.add(coord)
  assert 1<=coord[0]<=4 and 1<=coord[1]<=4
  im=pinned({'path':x['path'],'sha256':x['sha256']})
  gen=pinned({'path':x['generationRecord'],'sha256':x['generationSha256']})
  receipt=rec(Path(x['receipt']))
  review=pinned(x['quickReview']) if x.get('quickReview') else None
  cells.append({**x,'image':im,'generationRecord':gen,'receipt':receipt,'quickReview':review})
 assert len(cells)==cc.get('selectedCoreCount',len(cells))
 entry={**cc,'selectedCount':len(cells),'requiredCount':16,'cells':cells,'assembled4k':bool(cc.get('assembled4k',False)),'internalClosurePassed':bool(cc.get('internalClosurePassed',False))}
 d['partialTiles'][tile_id]=entry
 if entry.get('candidate') and entry.get('record') and entry['assembled4k']:adopt_owner_tile(tile_id,entry,coast_state)
'''
assert mark in src
src=src.replace(mark,block+'\n'+mark)
src=src.replace("active_root='r03_c01'","active_root='r02_c01'")
src=src.replace("latest4kCandidate=d['partialTiles'][active_root]['candidate']['path']","latest4kCandidate=d['partialTiles'].get(active_root,{}).get('candidate',d['partialTiles']['r03_c01']['candidate'])['path']")
old="Finish r03c01 coastline local repairs; continue r07c02 and r05c05 missing native cores. r07c04 v6 and r06c02 v2 internal geometry passed, material pending. Cross v7 internal131/132 and shared17/17 geometry passed; one r6c4 point deferred after two attempts. Whole zone incomplete."
new="r03c01 v11 internal33 and native replay passed. Continue only already active r02c01 native cores and r05c05 local repairs; r07c02 and r07c04 geometry/material updates follow explicit owner selections. r06c02 material pending. Cross v7 internal131/132 and shared17/17 geometry passed; one r6c4 point deferred after two attempts. No new production coordinates allocated in this continuation. Whole zone incomplete."
assert old in src
src=src.replace(old,new)
dst=Z/'refresh_live_progress_v3_20261016.py';assert not dst.exists()
dst.write_text(src,encoding='utf-8')
print(dst)
