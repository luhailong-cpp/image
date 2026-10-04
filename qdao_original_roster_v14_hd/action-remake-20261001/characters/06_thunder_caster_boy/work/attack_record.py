import argparse, hashlib, json, subprocess, sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
ap=argparse.ArgumentParser()
ap.add_argument('source'); ap.add_argument('direction'); ap.add_argument('frame', type=int); ap.add_argument('at')
ap.add_argument('--ref', action='append', default=[])
ap.add_argument('--version',default='v1')
ap.add_argument('--review', default='静态身份与手脚可读；完整动态、跨帧比例和根锚点待验收')
a=ap.parse_args()
stem=f'attack_{a.direction}_{a.frame:02d}_{a.version}'
subprocess.run([sys.executable,'-B',str(root/'tools/record_frame.py'),a.source,stem,f'prompts/{stem}.txt','--action','attack','--direction',a.direction,'--frame',str(a.frame),'--review',a.review,'--generated-at',a.at],check=True)
p=root/'work'/f'{stem}.png.generation.json'
d=json.loads(p.read_text(encoding='utf-8'))
for ref in a.ref:
 q=Path(ref)
 d['references'].append({'path':str(q).replace('\\','/'),'role':'new attack contact scale/costume continuity reference','sha256':hashlib.sha256(q.read_bytes()).hexdigest()})
d['submittedParameters']['referenced_image_paths']=[r['path'] for r in d['references']]
d['generationTimeEvidence']='Exact start timestamp recorded immediately before builtin call, UTC'
p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
