"""Archive and import a real SE result. No generation or selection."""
from pathlib import Path
import sys,json,subprocess
H=Path(__file__).resolve().parent
d=sys.argv[1]; frame=int(sys.argv[2]); a=H.parent/'05-generation'/d
r=json.loads((a/'tool-result.json').read_text(encoding='utf-8'))
import re
original=re.search(r'as (C:\\[^\n]+?\.png) by default',r['output_hint']).group(1)
def run(name,*args):
 subprocess.run([sys.executable,str(H/name),*map(str,args)],check=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
run('archive_builtin_result.py','--archive',a,'--original',original,'--tool-result',a/'tool-result.json')
run('import_frame.py','--archive',a,'--batch-id',d,'--direction','SE','--frame',frame,'--staging-root',a/'staging')
run('archive_metadata.py','--archive',a)
print(json.dumps({'archive':str(a),'frame':frame,'status':'imported_reconstructed_pending_visual'}))
