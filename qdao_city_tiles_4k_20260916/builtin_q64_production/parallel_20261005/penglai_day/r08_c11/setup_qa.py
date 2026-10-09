from pathlib import Path
r=Path(__file__).resolve().parent
old=r.parent/'r08_c12'
(r/'repairs/internal').mkdir(parents=True,exist_ok=True)
for name in ['quilt.py','quilt_v2.py','diagnose_overlap.py']:
 dest=r/'repairs/internal'/name
 assert not dest.exists()
 dest.write_text((old/'repairs/internal'/name).read_text(encoding='utf8').replace('r08_c12','r08_c11'),encoding='utf8')
s=(old/'qa_native.py').read_text(encoding='utf8').replace('r08_c12','r08_c11').replace('region-v3/r09_c12','region-v6/r09_c11')
(r/'qa_native.py').write_text(s,encoding='utf8')

