from pathlib import Path
import sys
B=Path(__file__).resolve().parents[1]
src=(B/'pipeline-tools/adopt-finished-current-20261016-v01.py').read_text(encoding='utf-8')
start=src.index('items=');end=src.index('\ncatalog=',start)
items=[("r10_c02","pipeline/output/68ed540e96c6b98d/assembly.json","pipeline/output/68ed540e96c6b98d/left-worker-qa-resume20261016-v01/worker-review-and-repair-queue.json"),("r15_c05","pipeline/output/28e1055ea7823560/assembly.json","pipeline/qa/resume-20261016-v01/review.json")]
src=src[:start]+'items='+repr(items)+src[end:]
src=src.replace('current-slot-counts-20261016-v01.json','current-slot-counts-20261016-v02.json').replace('three new actual full candidates','two new actual full candidates').replace('activeCoordinate="r14_c06:p02_03"','activeCoordinate="r14_c06:p03_02"').replace('["r14_c06","r10_c02","r11_c08/r12_c08","r15_c05"]','["r14_c06","r10_c02/r10_c03","r11_c08/r12_c08","r13_c01"]')
out=B/'pipeline-tools/adopt-finished-current-20261016-v02.py';assert not out.exists();assert not (B/'pipeline-tools/current-slot-counts-20261016-v02.json').exists();out.write_text(src,encoding='utf-8')
print(out)

