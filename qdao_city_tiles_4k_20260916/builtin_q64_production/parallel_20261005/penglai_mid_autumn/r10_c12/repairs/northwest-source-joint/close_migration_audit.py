from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=D/'migration-journal.json';snap=D/'text-history/migration-journal-before-after-audit.json';assert not snap.exists();snap.write_bytes(p.read_bytes());j=json.loads(p.read_text(encoding='utf-8'));j['result']['sha256']=sha(D/'migration-applied.json');j['afterAudit']={'file':str(D/'migration-after-audit.json'),'sha256':sha(D/'migration-after-audit.json')};j['priorJournal']={'file':str(snap),'sha256':sha(snap)};p.write_bytes((json.dumps(j,ensure_ascii=False,indent=2)+'\n').encode());print('Journal final result and after-audit hashes synchronized')
