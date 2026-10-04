from pathlib import Path
import json,shutil,hashlib,os
root=Path(__file__).resolve().parent;src=root.parent/'generation'/'run-SW-07';out=root/'run-SW-15.png'
expected='76f2b08a8a3f22d3c8f0c4ee15124f30f06dbb426660165b3c7b33fc5a7bed60'
assert hashlib.sha256((src/'native.png').read_bytes()).hexdigest()==expected
shutil.copy2(src/'native.png',out)
rec=json.loads((src/'native.png.generation.json').read_text(encoding='utf8'))
for f in ['prompt.txt','request.json','receipt.json']:
 shutil.copy2(src/f,root/('run-SW-15.'+f))
rec.update(file=out.name,prompt='run-SW-15.prompt.txt',originalRequestedSlot='run-SW-07',selectedSlot='run-SW-15')
rec['evidence']['receipt']='run-SW-15.receipt.json';rec['review'].update(observedPhase='A(screen-left hip) bent-knee short flight, B(screen-right) trails; reassigned by actual pose',status='provisional static selection')
(root/'run-SW-15.png.generation.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2),encoding='utf8')
p=root/'run-SW-09.png';q=root/'run-SW-16.png';rp=Path(str(p)+'.generation.json')
r=json.loads(rp.read_text(encoding='utf8'));assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
r.update(file=q.name,originalRequestedSlot='run-SW-09',selectedSlot='run-SW-16');r['review'].update(observedPhase='Actual A forward reach/precontact, heel-leading upturned sole; B trails; reassigned from mismatched request',status='provisional static selection')
assert p.resolve().parent==root and q.resolve().parent==root
os.replace(p,q);Path(str(q)+'.generation.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');rp.unlink()
print(json.dumps({'run-SW-15':expected,'run-SW-16':r['sha256']}))
