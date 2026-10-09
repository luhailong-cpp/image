from pathlib import Path
import json,hashlib
D=Path(__file__).parent;F=D/'final-v4';p=F/'joined.png.generation.json';g=json.loads(p.read_text(encoding='utf-8'));a=json.loads((F/'assembly.json').read_text(encoding='utf-8'))
g['derivedFrom'] += [dict(a['jointRepairNative'],generationRecord=a['jointRepairNative']['file']+'.generation.json'),a['priorComposite']]
g['repairMask']=a['repairWeight'];g['registrationFields']=a['registrationFields'];g['registrationControls']=a['registrationControls']
p.write_text(json.dumps(g,ensure_ascii=False,indent=2),encoding='utf-8')
