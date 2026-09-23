import json, hashlib, base64, subprocess, sys
from pathlib import Path
log=Path(r'C:/Users/Administrator/.codex/sessions/2026/09/23/rollout-2026-09-23T02-47-55-01a0cd05-5a72-7812-8032-8c808a8b66a5.jsonl')
td=Path(__file__).resolve().parent
gen=td.parent/'17-generation'
for line in log.open(encoding='utf8'):
    o=json.loads(line); item=o.get('payload',{}).get('item',{})
    if o.get('timestamp','')<'2026-09-23T09:15' or item.get('kind')!='image_gen.generation': continue
    for frame in (8,10):
        arc=gen/f'walk-N-{frame:02d}-v2'
        req=json.loads((arc/'request.json').read_text())
        if item.get('revisedPrompt')!=req['actual_request']['prompt']: continue
        meta={k:v for k,v in item.items() if k!='result'}
        p=Path(meta['savedPath']); assert p.is_file(); assert p.read_bytes()==base64.b64decode(item['result'])
        evidence={'timestamp':o['timestamp'],'eventOrdinal':o['ordinal'],'recoveredFrom':str(log),'promptExactMatch':True,'output_hint':None,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'savedPathBytesMatchEventResult':True,'note':'Actual image generation completion event recovered; tool output hint not reconstructed.'}
        for name,val in [('tool-result.json',meta),('recovery-evidence.json',evidence)]:
            dst=arc/name; assert not dst.exists(); dst.write_text(json.dumps(val,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
        proc=subprocess.run([sys.executable,'-B',str(td/'archive_builtin_result.py'),'--archive',str(arc),'--local-result-path',str(p),'--tool-result',str(arc/'tool-result.json'),'--completed-at',o['timestamp']],capture_output=True,text=True)
        print(proc.returncode,proc.stdout,proc.stderr); assert proc.returncode==0
        proc=subprocess.run([sys.executable,'-B',str(td/'import_frame.py'),'--archive',str(arc)],capture_output=True,text=True)
        print('IMPORT',frame,proc.returncode,proc.stderr); assert proc.returncode==0
