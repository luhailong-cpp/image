from pathlib import Path
import json,sys,hashlib,os
root=Path(__file__).resolve().parent
stem,slot=sys.argv[1:3];p=root/(stem+'.png');q=root/(slot+'.png');rp=Path(str(p)+'.generation.json');r=json.loads(rp.read_text(encoding='utf8'))
assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];assert p.resolve().parent==root and q.resolve().parent==root and not q.exists()
r['file']=q.name;r['sourceVariant']=stem;os.replace(p,q);Path(str(q)+'.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');rp.unlink()
print(q.name+' '+r['sha256'])
