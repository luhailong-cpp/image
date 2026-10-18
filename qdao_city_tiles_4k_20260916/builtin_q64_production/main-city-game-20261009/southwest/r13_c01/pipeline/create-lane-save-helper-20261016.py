from pathlib import Path
import hashlib,json
B=Path(__file__).resolve().parents[2]
s=B/'pipeline-tools/col5-save-return-20261012b.py';o=Path(__file__).with_name('lane-save-return-20261016.py')
assert not o.exists()
text=s.read_text(encoding='utf-8-sig')
assert 'B = Path(__file__).resolve().parents[1]' in text
assert "assert tile in {f'r{r:02d}_c05' for r in range(9,17)}" in text
text=text.replace('B = Path(__file__).resolve().parents[1]','B = Path(__file__).resolve().parents[2]')
text=text.replace("assert tile in {f'r{r:02d}_c05' for r in range(9,17)}", "assert tile in {f'r{r:02d}_c{c:02d}' for r in range(13,17) for c in range(1,5)}")
o.write_text(text,encoding='utf-8')
d={'source':str(s),'sourceSha256':hashlib.sha256(s.read_bytes()).hexdigest(),'file':str(o),'sha256':hashlib.sha256(o.read_bytes()).hexdigest(),'scope':'only newly allocated r13-r16 c01-c04','changes':['base path adjusted to southwest','scope asserted to newly allocated16'],'allocationEvidence':str(B/'pipeline-tools/internal-lower-left-allocation-20261016-v01.json')}
Path(str(o)+'.derivation.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
print(json.dumps(d))
