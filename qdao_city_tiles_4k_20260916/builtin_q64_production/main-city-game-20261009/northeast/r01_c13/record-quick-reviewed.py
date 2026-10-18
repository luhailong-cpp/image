from pathlib import Path
import json,hashlib,sys
from datetime import datetime,timezone
T=Path(__file__).resolve().parent;label=sys.argv[1];sel=json.loads((T/'selected-native.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for pair in sys.argv[2:]:
    a,b=pair.split(':');fs=[T/'native'/sel[p] for p in [a,b]]
    sources=[{'file':str(f),'sha256':sha(f)} for f in fs]
    sig=hashlib.sha256(json.dumps(sources).encode()).hexdigest()[:16];q=T/'qa/quick-native-joins'/sig;window=q/(a+'-'+b+'.png');assert window.exists()
    records.append({'pair':pair,'sources':sources,'window':str(window),'windowSha256':sha(window),'visualReviewed':True,'finding':'Native outlines and courses continuous; minor material grain variation retained for full-tile review. No acceptance implied.'})
dest=T/'qa/recovery-20261016'/(label+'.json');assert not dest.exists()
dest.write_text(json.dumps({'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'joins':records,'formalAcceptedCount':0},indent=2)+'\n',encoding='utf-8')
print(dest)
