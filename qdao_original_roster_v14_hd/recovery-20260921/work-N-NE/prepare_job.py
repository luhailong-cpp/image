from pathlib import Path
import importlib.util,json,sys
here=Path(__file__).resolve().parent
module_path=here.parent/'06-tools/archive_generation.py'
spec=importlib.util.spec_from_file_location('archive06',module_path);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
jobs=json.loads((here/'plan.json').read_text(encoding='utf-8'))['jobs']
job=next(j for j in jobs if j['direction']==sys.argv[1] and j['frame']==int(sys.argv[2]))
batch=job['batch'] if len(sys.argv)<4 else sys.argv[3]
result=a.prepare(batch,Path(job['prompt_path']).read_text(encoding='utf-8'),job['references'])
print(json.dumps(result,ensure_ascii=False))
