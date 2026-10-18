from pathlib import Path
import json,hashlib,sys
W=Path(__file__).resolve().parent
p=W/'receipts'/(sys.argv[1]+'.request.json');q=json.loads(p.read_text())
note=(W/'prompts'/(sys.argv[1]+'.local-note.txt')).read_text()
q['prompt']+='\n'+note
Path(q['promptFile']).write_text(q['prompt'],encoding='utf8')
q['promptSHA256']=hashlib.sha256(Path(q['promptFile']).read_bytes()).hexdigest()
p.write_text(json.dumps(q,indent=2),encoding='utf8')
print(json.dumps(q))

