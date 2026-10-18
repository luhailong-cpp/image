from pathlib import Path
import json,hashlib
B=Path(__file__).resolve().parents[1];T=B/'r12_c06';d=T/'repairs-resume-20261012/right-ground-inlay-20261016-v01'
assert not (d/'tool-result.json').exists()
for p in [d/'aligned-layout-guidance.derivation.json',d/'request.json']:
    s=p.read_text(encoding='utf-8')
    if s.endswith(chr(92)+'n'):s=s[:-2]+'\n'
    json.loads(s);p.write_text(s,encoding='utf-8')
p=d/'prompt.txt';s=p.read_text(encoding='utf-8').replace(chr(92)+'n','\n');p.write_text(s,encoding='utf-8')
r=json.loads((d/'request.json').read_text(encoding='utf-8'));r['prompt']=s;r['promptSha256']=hashlib.sha256(p.read_bytes()).hexdigest();(d/'request.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(d/'request.json'),'normalizedBeforeSubmission':True,'prompt':s}))

