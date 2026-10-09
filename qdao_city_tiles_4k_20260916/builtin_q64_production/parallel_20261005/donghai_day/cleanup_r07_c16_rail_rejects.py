"""Remove only confirmed rail reject raster intermediates after final commit."""
from pathlib import Path
import assembly_r07_c16 as a
R=a.ROOT.resolve();T=a.TILE;P=T/'repairs';D=P/'final-rail-v2'
expected='de2ffe83eff08483741521f59e81bbc1ea62927024a86229cb6890eb55477ad0'
assert a.sha(a.ART)==expected
for name in ['review.json','independent-review.json']:
 v=a.load_json(D/name);assert v['candidateSha256']==expected and v['result']=='pass'
reject=P/'final-rail-v1';files=list(reject.rglob('*.png'))
q=P/'final-rail-insertion';files+=list(q.glob('*.png'));files+=list((q/'south-boundary').glob('*.png'))
entries=[]
for f in files:
 p=f.resolve();assert p.is_relative_to(T.resolve()) and p.is_relative_to(R)
 entries.append(dict(file=str(p),sha256=a.sha(p),bytes=p.stat().st_size,status='rejected-or-diagnostic-raster-after-final-commit'))
assert all('halo-stitch' not in x['file'] for x in entries)
a.save_json(D/'rejected-raster-cleanup.json',dict(createdAtUtc=a.utc_now(),finalOutputSha256=expected,reason='User retains final art and required active inputs only. These rail attempts and diagnostic probes were not accepted into the final processing chain; generation and source text records are retained.',files=entries))
for e in entries:Path(e['file']).unlink()
for d in [reject,q,q/'south-boundary']:
 a.save_json(d/'rejected-raster-disposition.json',dict(finalOutputSha256=expected,status='Superseded rejected raster removed after reviewed final output landed; text provenance retained.',rasterCleanupRecord=str(D/'rejected-raster-cleanup.json')))
print(dict(deletedRasterFiles=len(entries),deletedBytes=sum(e['bytes'] for e in entries)))
