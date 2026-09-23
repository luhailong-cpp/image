"""Record exact single-frame built-in inputs; never calls a generation API."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
H=Path(__file__).resolve().parent
G=H.parent/'05-generation'
R=H.parents[2]
p=argparse.ArgumentParser()
p.add_argument('--archive',required=True)
p.add_argument('--prompt',required=True)
p.add_argument('--refs',nargs='+',required=True)
a=p.parse_args()
d=G/a.archive
assert d.resolve().is_relative_to(G.resolve())
d.mkdir(exist_ok=True)
assert not (d/'request.json').exists()
refs=[str((R/r).resolve()).replace('\\','/') for r in a.refs]
assert all(Path(r).is_file() for r in refs)
doc={'schema':1,'tool':'built-in image_gen','actual_model':'host-managed-unverified','configSnapshot':json.loads((R/'config/image-generation.json').read_text(encoding='utf-8')),'actual_request':{'prompt':a.prompt,'referenced_image_paths':refs,'started_at':datetime.now(timezone.utc).isoformat()},'reference_bindings_at_start':[{'path':r,'sha256':hashlib.sha256(Path(r).read_bytes()).hexdigest()} for r in refs],'paid_api_calls':0,'status':'request_prepared_not_yet_submitted'}
(d/'prompt.txt').write_bytes(a.prompt.encode('utf-8'))
(d/'request.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'archive':str(d),'request':doc['actual_request']}))
