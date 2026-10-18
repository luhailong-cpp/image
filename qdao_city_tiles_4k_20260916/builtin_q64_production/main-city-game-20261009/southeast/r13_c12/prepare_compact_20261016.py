import sys,json,importlib.util
from pathlib import Path
w=Path(__file__).resolve().parent.parent/'production_workflow_west_extension_20261016_v2.py'
s=importlib.util.spec_from_file_location('west',w);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
r=m.prepare('r13_c12',sys.argv[1],sys.argv[2] if len(sys.argv)>2 else None)
print(json.dumps({k:r[k] for k in ['tile','patch','version','request','target']},ensure_ascii=False))

