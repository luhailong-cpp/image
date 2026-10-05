from pathlib import Path
from datetime import datetime,timezone
import json,sys
from workflow import ingest
root=Path(__file__).resolve().parents[1]
cell=sys.argv[1];jf=root/'r08_c09/jobs'/f'{cell}.json'
receipt=root/'r08_c09/jobs'/f'{cell}-result.json'
j=json.loads(jf.read_text(encoding='utf-8'));r=json.loads(receipt.read_text(encoding='utf-8'))
j.update(sourceOutputPath=r['sourceOutputPath'],prompt=r['prompt'],references=r['references'],generatedAt=datetime.now(timezone.utc).isoformat(),toolResultPath=str(receipt))
j['submittedParameters'].update(referenced_image_paths=[x['path'] for x in r['references']],prompt=r['prompt'])
jf.write_text(json.dumps(j,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(ingest(jf)))
