from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
import numpy as np
from PIL import Image

D = Path(__file__).resolve().parent
B = D.parent.parent

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def rec(p):
    return {'path': Path(p).as_posix(), 'sha256': sha(p)}

def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def check(r):
    assert sha(r['path']) == r['sha256'], r['path']
    return Path(r['path'])

def arr(p):
    return np.asarray(Image.open(p).convert('RGB'))

def crop(a, box):
    x0, y0, x1, y1 = box
    return a[y0:y1, x0:x1]

def difference(a, b):
    assert a.shape == b.shape
    m = np.any(a != b, axis=2)
    y, x = np.nonzero(m)
    return {'differentPixels': int(m.sum()), 'comparedPixels': int(m.size),
            'differenceBBoxLocal': [int(x.min()), int(y.min()), int(x.max()+1), int(y.max()+1)] if x.size else None}

def write(name, obj):
    p = D / name
    assert not p.exists(), p
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    return rec(p)

def main():
    fixed_path = B / 'qa/r12c07-resume2-r19-v1/context-native.png'
    fixed = arr(fixed_path)
    merged = arr(D / 'context-native.png')
    assert fixed.shape == merged.shape == (4326, 4326, 3)
    assert np.array_equal(arr(D/'candidate-native-4096.png'), merged[115:4211,115:4211])
    inputs = []
    layers = []
    qa = []
    pending = []
    source_ids = np.zeros((4326,4326), np.uint8)
    replay = fixed.copy()
    for seg in ('W02','W04'):
        mp = B / f'repairs/r12c07-west-{seg}-20261016-v1/delivery-manifest-v1.json'
        m = load(mp)
        for key in ('context','candidate4096','assembly','review','replayPlan','sourceIds','fixedBase','westAnchorReadonly'):
            check(m[key])
        reviewed = arr(m['context']['path'])
        assert m['fixedBase']['path'] == fixed_path.as_posix()
        rr = load(m['review']['path'])
        inputs.append({'segment':seg,'manifest':rec(mp),'review':m['review'],'assembly':m['assembly'],
                       'context':m['context'],'actualModel':None,'historicalModelEvidence':m['actualModel']})
        pending.extend(m['pending'])
        for layer in m['layers']:
            native = arr(check(layer['source']))
            mask = np.load(check(layer['mask'])).astype(bool)
            assert not source_ids[mask].any()
            yy,xx = np.nonzero(mask)
            ox,oy = layer['originInContext']
            native_pixels = native[yy-oy,xx-ox]
            assert np.array_equal(native_pixels, reviewed[yy,xx])
            replay[yy,xx] = native_pixels
            new_id = len(layers)+1
            source_ids[yy,xx] = new_id
            layers.append(dict(layer, mergedSourceId=new_id, segment=seg, selectedPixels=int(mask.sum())))
        checks = rr.get('nativeFourEdgesCenterAndJunctions',rr.get('nativeFourEdgesAndCenter',[]))
        checks += [rr['actualCoreJoin']]
        for q in checks:
            if 'before' in q.get('label',''):
                continue
            if 'contextBox' in q:
                box = q['contextBox']
            elif 'eastContextBox' in q:
                box = q['eastContextBox']
            else:
                continue
            same = difference(crop(merged,box),crop(reviewed,box))
            assert same['differentPixels'] == 0, (seg,q.get('label','actualCoreJoin'),same)
            qa.append({'segment':seg,'label':q.get('label','actualCoreJoin'),'contextBox':box,
                       'inheritedStatus':q.get('status'), 'finding':q.get('finding'),
                       'review':m['review'],'reviewedNativeView':rec(q['path']),
                       'pixelIdentityToReviewedContext':same,
                       'qaReusedBecausePixelsUnchanged':True})
    assert np.array_equal(replay,merged)
    np.save(D/'source-layer-ids-uint8.npy',source_ids)
    south = []
    for name,box in [('south-context-x0-1254',[0,4096,1254,4326]),
                     ('south-core-x0-1254',[115,4096,1369,4211]),
                     ('south-context-x1254-4326',[1254,4096,4326,4326])]:
        result = difference(crop(merged,box),crop(fixed,box))
        result.update(name=name,contextBox=box)
        if name == 'south-context-x0-1254':
            p=D/'south-context-x0-1254-native.png'
            assert not p.exists()
            Image.fromarray(crop(merged,box)).save(p)
            result['nativeCrop']=rec(p)
        south.append(result)
    unchanged_w01 = difference(merged[:1024],fixed[:1024])
    unchanged_w03_mid = difference(merged[2278:3072],fixed[2278:3072])
    assert unchanged_w01['differentPixels'] == unchanged_w03_mid['differentPixels'] == 0
    proof = {'fullContextReplayDifferentPixels':0,'nativeIntegerSourceSelection':True,
             'noResize':True,'noBlend':True,'noBlur':True,'maskOverlapPixels':0,
             'changedPixelsToR19':difference(merged,fixed),
             'w01Y0To1024Unchanged':unchanged_w01,'w03Y2278To3072Unchanged':unchanged_w03_mid,
             'southDependency':south,'sourceIds':rec(D/'source-layer-ids-uint8.npy'),
             'actual4096CoreCropIdentityDifferentPixels':0}
    review = write('review-inherited-v1.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),
        'status':'W02_and_W04_core_local_pass_inherited_W01_W03_pending','formalAccepted':False,
        'newVisualQAClaimed':False,'qaReuse':qa,'pending':pending,'proof':proof})
    delivery = {'createdAtUtc':datetime.now(timezone.utc).isoformat(),
        'status':'frozen_local_candidate_W02_W04_merged_W01_W03_pending','formalAccepted':False,
        'tile':'r12_c07','context':rec(D/'context-native.png'),'candidate4096':rec(D/'candidate-native-4096.png'),
        'assembly':rec(D/'assembly.json'),'review':review,'fixedBase':rec(fixed_path),
        'baseAssembly':rec(B/'qa/r12c07-resume2-r19-v1/assembly.json'),
        'inputs':inputs,'layers':layers,'proof':proof,'pending':pending,
        'deferred':[{'id':'W01','attempts':2,'status':'pending_no_third_repeat',
            'evidence':rec(B/'qa/r12c07-west-pair-20261016-v1/W01b-v1/review-v1.json')},
            {'id':'W03','attempts':2,'status':'pending_no_third_repeat',
             'evidence':rec(B/'qa/r12c07-west-pair-20261016-v1/old-r05-input-audit-v1.json')}],
        'newGenerationCount':0,'actualModel':None,'method':'Exact native source selection from previously generated and reviewed W02/W04. No newly generated image.',
        'replayScript':rec(B/'repairs/r12c07-west-W02-20261016-v1/replay.py'),
        'auditScript':rec(Path(__file__))}
    manifest = write('delivery-manifest-v1.json',delivery)
    print(json.dumps({'manifest':manifest,'context':delivery['context'],'candidate4096':delivery['candidate4096'],
        'assembly':delivery['assembly'],'southDependency':south,'reusedQACount':len(qa)},ensure_ascii=False))

if __name__ == '__main__':
    main()
