from pathlib import Path
from PIL import Image
import numpy as np
import json, datetime, hashlib

ROOT=Path('E:/work/image')
PACKAGE=ROOT/'qdao_ui_redesign_v5/fidelity-20261016/login-revision-20261017'
source=ROOT/'qdao_ui_redesign_v5/01_login_2560x1080.png'
runtime=ROOT/'docs/ui-fidelity-20261016/native/core/01-login_2560x1080.png'
shell=PACKAGE/'client/Assets/Resources/UI/Ugui/CoreFidelity20261016/login_shell.png'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
installation=json.loads((PACKAGE/'qa/install-result.json').read_text(encoding='utf-8-sig'))
installed_at=datetime.datetime.fromisoformat(installation['completedAtUtc'].replace('Z','+00:00')).timestamp()
assert runtime.exists() and runtime.stat().st_mtime>installed_at, 'Capture predates current login installation'
ref=np.array(Image.open(source).convert('RGB')).astype(np.int16)
asset=np.array(Image.open(shell).convert('RGB')).astype(np.int16)
mask=np.ones(ref.shape[:2], dtype=bool)
mask[564:630,286:756]=False
assert np.max(np.abs(ref[mask]-asset[mask]))==0, 'Immutable source pixels changed'
report={'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'approvedSource':str(source),'approvedSourceSha256':sha(source),
 'assetSha256':sha(shell),'immutableAssetPixelsExact':True,
 'scope':'Immutable original artwork, excluding real server name/status/dot and status feedback. Actual data-bound glyphs intentionally remain native.',
 'liveServerVerified':False,'nativeCapture':str(runtime),'nativeCaptureSha256':sha(runtime),
 'nativeCaptureAfterInstallation':True,'regions':[]}
if runtime.exists():
    native=np.array(Image.open(runtime).convert('RGB')).astype(np.int16)
    assert native.shape==ref.shape
    # Restrict immutable samples away from dynamic labels and the tiny tintable
    # target-image perimeter; no thumbnail scaling or reference substitution.
    for name,(x,y,w,h) in {
      'logo':(165,76,925,450),
      'hero':(1380,145,650,840),
      'static_enter_lettering':(392,695,493,127),
      'announcement':(2205,24,166,165),
      'settings':(2380,24,166,165),
      'landscape':(1100,12,1020,125),
      'switch_account':(539,870,190,51),
    }.items():
        diff=np.abs(native[y:y+h,x:x+w]-ref[y:y+h,x:x+w])
        report['regions'].append({'name':name,'xywh':[x,y,w,h],
          'meanAbsoluteRgbDifference':float(diff.mean()),'maximumRgbDifference':int(diff.max()),
          'meanThreshold':3.0,'passed':bool(diff.mean()<=3.0)})
    report['passed']=all(x['passed'] for x in report['regions'])
else: report['passed']=False
out=PACKAGE/'qa/original-pixel-checks.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':report['passed'],'regions':len(report['regions']),
                  'meanDifferences':[round(r['meanAbsoluteRgbDifference'],3) for r in report['regions']]}))
if not report['passed']: raise SystemExit(1)
