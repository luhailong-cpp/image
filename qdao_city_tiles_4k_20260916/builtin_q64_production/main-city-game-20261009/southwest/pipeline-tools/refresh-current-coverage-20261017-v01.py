from pathlib import Path
B=Path(__file__).resolve().parents[1]
src=(B/'pipeline-tools/adopt-finished-current-20261016-v01.py').read_text(encoding='utf-8')
pre=src[:src.index('items=')]
body=src[src.index('tiles=[]'):]
body=body.replace('current-slot-counts-20261016-v01.json','current-slot-counts-20261017-v01.json').replace('three new actual full candidates hashed and dimension checked','current candidate hashes and dimensions verified at adoption; current selection metadata only, no duplicate image or historical scan').replace('activeTile="r14_c06",activeCoordinate="r14_c06:p02_03"','activeTile="r15_c06",activeCoordinate="r15_c06:p01_01"').replace('["r14_c06","r10_c02","r11_c08/r12_c08","r15_c05"]','["r15_c06","r10_c04","r11_c08/r14_c08","r13_c01"]').replace('["root","sw_left_resume_20261016","sw_right_resume_20261016","sw_col5_resume_20261016"]','["root","sw_left_restart_20261016","sw_right_restart_20261016","sw_col5_restart_20261016"]')
assert not (B/'pipeline-tools/current-slot-counts-20261017-v01.json').exists()
exec(compile(pre+'items=[]\ncatalog=read(B/"current-candidates.json")\n'+body,'<current-coverage-snapshot>','exec'))

