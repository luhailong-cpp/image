from pathlib import Path
import json,sys
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');sys.path.insert(0,str(B/'tools'));import native_batch as n
s=n.read_json(B/'selections/right-r04c14-candidate-sixteen-v003.json');s['selectionVersion']='right-r04c14-candidate-sixteen-v004'
for p in ['p12','p22']:
 r=B/f'versions/right-r04c14-{p}-native-v002/r04_c14/native/{p}.png.generation.json';d=n.read_json(r);s['patches'][p]={'record':str(r),'recordSha256':n.sha(r),'sha256':d['sha256']}
s['knownBlocking'].append('p12v002/p22v002 jointly fix inconsistent roof flower-endcap versus gold rim; small row/texture phase remains. p22 south wood/gold edge local step remains.')
s['notes'].append('p12 and p22 joint native repair evaluated at100pct; adopted best candidate only. QA report qa/right-r04c14-p12-p22-joint-after-v002.json')
f=B/'selections/right-r04c14-candidate-sixteen-v004.json';f.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8');a=n.assemble(f,n.Scope(),'right-r04c14-assembly-v004');print(json.dumps(a));print(n.sha(B/'versions/right-r04c14-assembly-v004/r04_c14/assembly/r04_c14-candidate.png'))

