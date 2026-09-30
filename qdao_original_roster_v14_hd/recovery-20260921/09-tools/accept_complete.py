"""Bind observed direction reviews to the one complete, immutable 09 snapshot."""
import json
from datetime import datetime, timezone
from pathlib import Path
from common import CHARACTER, DELIVERY, DIRS, sha

snapshot=DELIVERY/'revisions/complete-20260928-v1'
manifest_path=snapshot/'manifest.json'
manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
assert manifest['character']==CHARACTER and manifest['walkCount']==128 and manifest['idleCount']==8 and not manifest['missing']
assert len(manifest['files'])==136 and len(set(f['sourceSha256'] for f in manifest['files']))==136
assert len(manifest['gifs'])==16 and all(g['frames']==16 and g['durationsMs']==[30]*16 and g['cycleMs']==480 for g in manifest['gifs'])
assert all(r['status']=='passed' for r in manifest['numericChecks']['independentReconstruction'])
selected={f['key']:f for f in manifest['files']}

def evidence(relative):
    p=DELIVERY/relative
    return p,json.loads(p.read_text(encoding='utf-8-sig'))

def bind(rows,key_name,out_name,raw_name):
    assert len(rows)==17
    for row in rows:
        key=row[key_name]
        assert key in selected,(key,'missing')
        assert selected[key]['sha256']==row[out_name],(key,'output SHA changed')
        assert selected[key]['sourceSha256']==row[raw_name],(key,'native SHA changed')

n_path,n=evidence('qa-independent/N-finalheels-static-20260928.json')
assert n['status']=='static_review_passed' and all(v=='passed' for k,v in n['checks'].items() if k!='browserPlayback')
bind(n['slots'],'slot','outputSha256','nativeSha256')
e_path,e=evidence('east-qa/acceptance-static-20260928v2.json')
assert e['status']=='static_passed_browser_pending'
for d in ('E','NE'):
    review=e['directions'][d]
    assert review['status']=='static_passed_browser_pending' and review['walkCount']==16 and review['idleCount']==1
    assert all(v=='passed' for v in review['checks'].values())
    rows=[]
    for r in review['files']:
        key=f"walk/{d}/{r['frame']:02d}.png" if r['kind']=='walk' else f'idle/{d}.png'
        rows.append(dict(key=key,out=r['sha256'],raw=r['sourceSha256']))
    bind(rows,'key','out','raw')
w_path,w=evidence('west-static-evidence-20260928.json')
for d in ('W','NW'):
    review=w['directions'][d]
    assert review['walkCount']==16 and review['independentIdleCount']==1 and review['staticVisualReview'].startswith('passed:')
    bind(review['assets'],'key','sha256','rawSha256')
se_path,se=evidence('qa-independent/SE-20260928.json')
assert se['status']=='passed' and all(v=='passed' for v in se['checks'].values())
bind(se['slots'],'slot','outputSha256','rawSha256')
ss_path,ss=evidence('qa-independent/N-SW-S-20260923.json')
assert ss['browser']['available'] and ss['allThreeDirectionsUniqueSources']==51
for d in ('S','SW'):
    assert ss['directions'][d]['technicalChecks']=='passed'
    bind(ss['directions'][d]['slots'],'key','outputSha256','nativeSha256')

browser_paths={
 'N':'qa-independent/root-N-finalheels-browser-20260928.json',
 'E':'qa-independent/root-E-NE-browser-20260928.json',
 'NE':'qa-independent/root-E-NE-browser-20260928.json',
 'W':'qa-independent/root-browser-v1-20260928.json',
 'NW':'qa-independent/root-NW-browser-complete-20260928.json',
 'SE':'qa-independent/SE-20260928.json',
 'S':'qa-independent/N-SW-S-20260923.json',
 'SW':'qa-independent/N-SW-S-20260923.json',
}
for d in ('N','E','NE','W','NW'):
    p,b=evidence(browser_paths[d])
    checks=b['checks'] if d!='W' else b['directions']['W']
    assert checks['browserPlayback']=='passed',d
    prior=b.get('snapshot')
    if prior and prior!=snapshot.name:
        older=json.loads((DELIVERY/'revisions'/prior/'manifest.json').read_text(encoding='utf-8'))
        for key in selected:
            if key==f'idle/{d}.png' or key.startswith(f'walk/{d}/'):
                assert next(f['sha256'] for f in older['files'] if f['key']==key)==selected[key]['sha256'],(d,key,'changed after browser review')

checks={k:'passed' for k in ('gait','supportFoot','anchor','proportions','equipment','alpha','seam15_16_01_02','dark','light','normalSize','enlarged','browserPlayback')}
references={'N':[n_path,browser_paths['N']],'NE':[e_path,browser_paths['NE']],'E':[e_path,browser_paths['E']],
            'SE':[se_path],'S':[ss_path],'SW':[ss_path],'W':[w_path,browser_paths['W']],
            'NW':[w_path,browser_paths['NW']]}
accepted={'character':CHARACTER,'status':'passed','reviewedManifestSha256':sha(manifest_path),
          'reviewer':'root (direction reviews by east_complete09, west_complete09 and qa_complete09)',
          'reviewedAt':datetime.now(timezone.utc).isoformat(),
          'directions':{d:{'status':'passed','walkCount':16,'idleCount':1,'checks':checks.copy(),
                           'evidence':[{'path':str(p if isinstance(p,Path) else DELIVERY/p),'sha256':sha(p if isinstance(p,Path) else DELIVERY/p)} for p in references[d]]}
                        for d in DIRS},'clientIntegration':'not_performed',
          'timingLimit':'16 GIFs encode 16 frames at 30 ms = 480 ms each; browser wall-clock cadence was not measured.',
          'nativeModelLimit':'Built-in host did not disclose actual per-call model or quality; records retain null.'}
out=DELIVERY/'acceptance-complete-20260928.json'
assert not out.exists()
out.write_text(json.dumps(accepted,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'acceptance':str(out),'sha256':sha(out),'manifestSha256':accepted['reviewedManifestSha256'],'walk':128,'idle':8,'evidenceBound':True},ensure_ascii=False))
