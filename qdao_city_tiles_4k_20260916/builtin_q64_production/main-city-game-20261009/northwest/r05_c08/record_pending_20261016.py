from pathlib import Path
import sys
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import workflow_20261016 as w
p=w.p
for identifier in ['s04_02_native01','s04_02_fix01']:
 D=T/'qa/source-review'/identifier;m=p.read(D/'manifest.json')
 reviews=[dict(file=c['file'],sha256=c['sha256'],status=('needs_revision' if c['name']=='south-seam' else ('passed' if identifier.endswith('native01') else 'not_viewed'))) for c in m['crops']]
 p.write_json(D/'review.json',{'source':m['source'],'actuallyViewed':True,'cropReviews':reviews,'status':'needs_revision','finding':'Southern actual core seam y20480 has mismatched tile column count/width and scalloped lip phase. Native01 other four crops passed. Two repair attempts fail to align southern columns. Original retained as best pending; do not propagate this source as fixed anchor.','formalAccepted':False},replace=False)
p.write_json(T/'deferred-s04_02-20261016.json',{'patch':'s04_02','bestCandidate':str(T/'native/s04_02_native01.png'),'bestSha256':p.sha(T/'native/s04_02_native01.png'),'attempts':['s04_02_native01','s04_02_fix01','s04_02_fix02'],'status':'needs_revision_deferred_after_two_fixes','selected':False,'problem':'Southern tile-column width and phase mismatch at world y20480; north/west/NW/SW of native01 passed. No propagation as anchor.'},replace=False)
print('Saved pending, not selected; continuing independent core.')

