"""Import explicitly chosen real whole-frame sources; never synthesize animation."""
from pathlib import Path
import json,sys,subprocess,hashlib
R=Path(__file__).resolve().parent.parent
O=R/'20-work/export-v1/20_star_formation_master_girl'
choice=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
rows=choice if isinstance(choice,list) else choice.get('candidates',[])
done=[];failed=[]
for c in rows:
    slot=c['slot'];attempt=c['attempt'];raw=R/'20-generation'/attempt/'raw.png'
    sidecar=O/(slot+'.generation.json')
    if not raw.is_file():failed.append({'slot':slot,'attempt':attempt,'error':'raw missing'});continue
    digest=hashlib.sha256(raw.read_bytes()).hexdigest()
    if sidecar.exists() and (O/slot).exists() and json.loads(sidecar.read_text(encoding='utf8'))['derivedFrom']['sha256']==digest:continue
    cmd=[sys.executable,'-X','utf8','-B',str(R/'20-tools/import_frame.py'),'--attempt',str(raw.parent),'--slot',slot]
    if (O/slot).exists():cmd.append('--replace')
    run=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8')
    if run.returncode:failed.append({'slot':slot,'attempt':attempt,'error':run.stderr or run.stdout})
    else:done.append({'slot':slot,'attempt':attempt})
print(json.dumps({'imported':done,'failed':failed},ensure_ascii=False))
if failed:sys.exit(1)
