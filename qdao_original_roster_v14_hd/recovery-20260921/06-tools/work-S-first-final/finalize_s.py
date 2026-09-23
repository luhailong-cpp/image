from pathlib import Path
import json,re,sys,subprocess
from prepare_s import arc,HERE,TOOLS
for n in [int(v) for v in sys.argv[1:]]:
    batch=f'S{n:02d}-edge-final-v1'
    result=json.loads((HERE/f'S{n:02d}-result.json').read_text())
    original=re.search(r' as (.+?\.png) by default',result['output_hint']).group(1)
    print(json.dumps(arc.finalize(batch,original,result)))
    p=subprocess.run([sys.executable,'-B',str(TOOLS/'import_frame.py'),'--archive',str(TOOLS.parent/'06-generation'/batch),'--batch-id',batch,'--direction','S','--frame',str(n),'--staging-root',str(HERE)],capture_output=True,text=True,encoding='utf-8')
    if p.returncode:print(p.stdout,p.stderr);raise SystemExit(p.returncode)
    print(f'S{n:02d} imported with independent reconstruction verification.')
