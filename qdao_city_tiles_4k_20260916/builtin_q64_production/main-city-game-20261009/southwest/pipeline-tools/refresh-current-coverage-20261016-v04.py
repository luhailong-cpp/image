from pathlib import Path
B=Path(__file__).resolve().parents[1]
src=(B/'pipeline-tools/adopt-finished-current-20261016-v01.py').read_text(encoding='utf-8')
pre=src[:src.index('items=')]
body=src[src.index('tiles=[]'):]
body=body.replace('current-slot-counts-20261016-v01.json','current-slot-counts-20261016-v04.json').replace('three new actual full candidates hashed and dimension checked','current candidate hashes and dimensions already verified at adoption; no duplicate image check or old version scan').replace('activeTile="r14_c06",activeCoordinate="r14_c06:p02_03"','activeTile="r15_c06",activeCoordinate="r15_c06:p01_04"').replace('["r14_c06","r10_c02","r11_c08/r12_c08","r15_c05"]','["r15_c06","r10_c03","r13_c08","r15_c05 rim repair / lower-left"]')
assert not (B/'pipeline-tools/current-slot-counts-20261016-v04.json').exists()
exec(compile(pre+'items=[]\ncatalog=read(B/"current-candidates.json")\n'+body,'<current-coverage-snapshot>','exec'))

