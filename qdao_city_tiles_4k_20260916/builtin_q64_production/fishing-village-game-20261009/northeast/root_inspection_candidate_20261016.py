import json
from pathlib import Path
import r06_c14_extension as b
import root_north_20261012 as n
Z=n.Z;t='r04_c12';d=json.loads((Z/'records'/f'{t}.working-selection.json').read_text());assert len(d)==15
d['r04_c12_p43']='r04_c12_p43-v5.png'
p=Z/'records/r04_c12.selection-inspection-v1.json';assert not p.exists()
n.atomic(p,{'schemaVersion':1,'tile':t,'createdAtUtc':b.now(),'status':'best_full16_inspection_candidate_with_known_unpassed_roof_join','formalAccepted':False,'usable':False,'workingSelectedCoreCount':15,'knownUnpassed':['r04_c12_p43-v5 right join to p44'], 'patches':{k:dict(b.ref(Z/'native'/v,'best available native for inspection'),reviewStatus='unpassed_right_join' if k.endswith('p43') else 'local_provisional_pass') for k,v in d.items()}})
print(str(p))

