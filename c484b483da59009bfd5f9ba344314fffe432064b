import json,subprocess,sys
from pathlib import Path
root=Path(r'E:/work/image/qdao_original_roster_v13')
for x in json.loads((root/'review/04_mountain_guardian_boy/import-S59-jobs.json').read_text(encoding='utf-8-sig')):
 d=root/'generation/04_mountain_guardian_boy'/x['batch']
 args=[sys.executable,'-B',str(root/'tools/pipeline.py'),'import-walk','--character','04_mountain_guardian_boy','--direction','S','--source',str(d/'raw.png'),'--prompt',str(d/'prompt.txt'),'--receipt',str(d/'receipt.json'),'--batch-id',x['batch'],'--rows',str(x['rows']),'--cols',str(x['cols']),'--output-frames',','.join(map(str,x['map'])),'--common-scale','.84']
 if x.get('select'):args+=['--source-cell-indices',','.join(map(str,x['select']))]
 subprocess.run(args,check=True)
