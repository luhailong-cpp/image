from pathlib import Path
import json
b=Path(__file__).resolve().parents[2]
p=Path(__file__).resolve().parent/'candidate-review-20261004.json'
review=json.loads(p.read_text(encoding='utf-8'))
for item in review['candidates']:
    dest=b/(item['file']+'.generation.json')
    rec=json.loads(dest.read_text(encoding='utf-8'))
    rec['review']={'status':item['recommendation'],'actualObservation':item['targetObservation'],'sideEffect':item['sideEffect'],'otherDrift':item['otherDrift'],'formalAcceptance':False,'reviewFile':'review/axis-N-NW/candidate-review-20261004.json'}
    dest.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Candidate review metadata saved; runtime unchanged')
