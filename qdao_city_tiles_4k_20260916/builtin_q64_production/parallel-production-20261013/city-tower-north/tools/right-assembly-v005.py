from pathlib import Path
import json,sys
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel-production-20261013/city-tower-north');sys.path.insert(0,str(B/'tools'));import native_batch as n
s=n.read_json(B/'selections/right-r04c14-candidate-sixteen-v004.json');s['selectionVersion']='right-r04c14-candidate-sixteen-v005'
r=B/'versions/right-r04c14-p41-native-v002/r04_c14/native/p41.png.generation.json';d=n.read_json(r);s['patches']['p41']={'record':str(r),'recordSha256':n.sha(r),'sha256':d['sha256']}
s['knownBlocking'].append('p21 south paper duplicate corner unresolved after two dedicated repairsv004/v005;retainv002. p41v002 removes north duplicate course, east grout dead end and slight phase remain.')
s['notes'].append('All24 internal seams inspected at100pct; modifiedp41four edges reviewed. Reports qa/right-r04c14-horizontal-qa-v004.json and qa/right-r04c14-p41-after-v002.json. Formalaccepted0.')
f=B/'selections/right-r04c14-candidate-sixteen-v005.json';f.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8');a=n.assemble(f,n.Scope(),'right-r04c14-assembly-v005');print(json.dumps(a));print(n.sha(B/'versions/right-r04c14-assembly-v005/r04_c14/assembly/r04_c14-candidate.png'))

