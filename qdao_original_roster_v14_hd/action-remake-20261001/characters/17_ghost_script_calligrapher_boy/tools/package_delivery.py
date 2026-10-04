"""Bundle validated final runtime assets and portable preview, without source images."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib, json
B=Path(__file__).resolve().parents[1]
M=json.loads((B/'manifest.json').read_text(encoding='utf-8'))
assert M['status']=='passed' and M['counts']['exportedRuntimeSlots']==196
assert json.loads((B/'review/final-package-verification.json').read_text(encoding='utf-8'))['status']=='passed'
assert json.loads((B/'cleanup-report.json').read_text(encoding='utf-8-sig'))['status']=='completed'
files=list((B/'runtime').rglob('*'))
files=[p for p in files if p.is_file()]
files += [B/p for p in ['manifest.json','acceptance.json','DELIVERY.md','STATUS.md',
    'cleanup-report.json','preview/delivery.html','preview/delivery-data.json',
    'preview/run-current-1200ms.webp','preview/run-current-1200ms.json',
    'review/final-package-verification.json','review/final-sequence-review.json',
    'review/contact-pairs-current-20261004.json','preview/manifest-preview.json']]
assert all(p.is_file() and p.resolve().is_relative_to(B.resolve()) for p in files)
for s in M['sequences']:
    for f in s['frames']:
        assert hashlib.sha256((B/f['file']).read_bytes()).hexdigest()==f['sha256']
out=B/'17-spirit-scribe-actions.zip'
with ZipFile(out,'w',ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(files): z.write(p,p.relative_to(B).as_posix())
with ZipFile(out) as z:
    assert z.testzip() is None
    assert sum(p.endswith('.png') for p in z.namelist())==196
result={'file':out.name,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),
        'bytes':out.stat().st_size,'entries':len(files),'runtimePngs':196,
        'clientIntegrated':False,'zipIntegrity':'passed'}
(B/'package.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
