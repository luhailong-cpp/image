from pathlib import Path
from PIL import Image
import json,hashlib,datetime
R=Path(__file__).resolve().parents[1]
q=R/'qa'/'repair-checkpoint-20261016';q.mkdir(exist_ok=True)
for tile,version,checked in [('r03_c05','v3',['vertical-1-1','vertical-2-1','horizontal-1-2','horizontal-3-2','horizontal-3-3','vertical-1-4','vertical-2-4','vertical-3-4']),('r04_c05','v2',['vertical-1-4','vertical-2-3','vertical-2-4','vertical-3-3','vertical-3-4','horizontal-2-3','horizontal-3-2','horizontal-3-3'])]:
 p=R/'tiles'/f'{tile}_candidate-{version}_4096.png';d=json.loads(p.with_suffix('.json').read_text());old=json.loads((R/'tiles'/f'{tile}_candidate-v1_4096.json').read_text())
 changed=[s for s,o in zip(d['sources'],old['sources']) if s['sha256']!=o['sha256']]
 report={'tile':tile,'candidate':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'dimensions':list(Image.open(p).size),'changedSources':changed,'reviewedInternalEdges':checked,'formalAccepted':False,'internalStatus':'pending_surface_texture_transitions','unchangedSourceHashQA':'Prior QA remains applicable only to edges with both source hashes unchanged.','remainingIssues':('horizontal-3-2 pigment transition; horizontal-3-3 newly denser top texture; vertical-1-4/2-4 scale changes' if tile=='r03_c05' else 'vertical-1-4 and vertical-2-3 paving texture changes; lantern slight brightness change; horizontal-3-2 and vertical-3-4 texture'),'actualModel':'not_returned'}
 (q/f'{tile}.json').write_text(json.dumps(report,indent=2))
a=Image.open(R/'tiles/r03_c05_candidate-v3_4096.png');b=Image.open(R/'tiles/r04_c05_candidate-v2_4096.png')
for n in [2,3]:
 out=Image.new('RGB',(1024,256));out.paste(a.crop(((n-1)*1024,3968,n*1024,4096)),(0,0));out.paste(b.crop(((n-1)*1024,0,n*1024,128)),(0,128));out.save(q/f'external-r03-r04-{n}.png')
p=R/'progress.json';d=json.loads(p.read_text(encoding='utf-8-sig'));d.update(versionCount=len(list((R/'native').glob('*.png'))),currentPatch=None,updatedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),qaRecord=str(q),status='native_coverage_complete_candidates_pending_surface_repairs_and_remaining_external_edges');p.write_text(json.dumps(d,indent=2));print(d)
