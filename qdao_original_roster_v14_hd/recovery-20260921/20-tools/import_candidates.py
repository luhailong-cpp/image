"""Import only real archived single-frame candidates, never fill missing slots."""
from pathlib import Path
import argparse,subprocess,sys,json
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
p=argparse.ArgumentParser();p.add_argument('direction',choices=['N','NE','E','SE','S','SW','W','NW']);a=p.parse_args()
choices={('W',1):'v2',('W',2):'v2',('W',12):'v2',('N',1):'v2',('N',2):'v2',('N',4):'v2',('E',1):'v2'}
out=ROOT/'20-work/export-v1/20_star_formation_master_girl'
done=[];missing=[]
for n in range(1,17):
    name=f'{a.direction}-{n:02d}-{choices.get((a.direction,n),"v1")}'
    attempt=ROOT/'20-generation'/name
    slot=f'walk/{a.direction}/{n:02d}.png'
    if (out/slot).exists():continue
    if not (attempt/'raw.png.generation.json').exists() or not (attempt/'raw.png').exists():missing.append(slot);continue
    subprocess.run([sys.executable,'-X','utf8','-B',str(HERE/'import_frame.py'),'--attempt',str(attempt),'--slot',slot],check=True)
    done.append(slot)
print(json.dumps({'direction':a.direction,'importedCandidates':done,'stillMissing':missing,'visualApproval':False}))
