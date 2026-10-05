"""Register one completed builtin detail call from a prepared per-cell job."""
from pathlib import Path
from argparse import ArgumentParser, Namespace
import json
import production

p=ArgumentParser()
p.add_argument('--job',required=True)
p.add_argument('--result',required=True)
p.add_argument('--source',required=True)
p.add_argument('--generated-at',required=True)
a=p.parse_args()
job_path=Path(a.job).resolve(strict=True)
j=json.loads(job_path.read_text(encoding='utf-8-sig'))
tile=Path(j['tileDir']).resolve(strict=True)
assert tile.is_relative_to(production.ROOT)
e=tile/'jobs'/j['cell']
e.mkdir(exist_ok=True,parents=True)
refs=e/'references.json'
params=e/'submitted-parameters.json'
refs.write_text(json.dumps(j['references'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
params.write_text(json.dumps(j['submittedParameters'],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
production.record(Namespace(tile=tile.name,source=a.source,prompt_file=j['promptFile'],tool_result_json=a.result,references_json=str(refs),submitted_parameters_json=str(params),generated_at=a.generated_at,config=None,patch_id=j['cell']))
