"""Read-only gates and post-cleanup evidence; this helper never deletes or edits art."""
import argparse
import hashlib
import json
import re
import stat
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

T = Path(__file__).resolve().parent.parent
EXPECTED = Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/lanxian_day/r09_c08').resolve()
assert T == EXPECTED
S = T / 'selected'

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8-sig'))

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def walk(v):
    yield v
    if isinstance(v, dict):
        for x in v.values():
            yield from walk(x)
    elif isinstance(v, list):
        for x in v:
            yield from walk(x)

def check_no_reparse(p):
    p = Path(p).absolute()
    for q in [p, *p.parents]:
        assert not (q.lstat().st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT), f'Reparse path: {q}'

def validate():
    dp = S / 'delivery.manifest.json'
    d = read(dp)
    assert d['tile'] == 'r09_c08' and d['qualifiedComplete4KCandidate'] is True
    verified = []
    images = {}
    for name, dims in [('core',(4096,4096)), ('extended',(4326,4326)), ('preview',(1024,1024))]:
        e = d['outputs'][name]
        p = Path(e['file']).resolve()
        check_no_reparse(p)
        assert p.parent == S and sha(p) == e['sha256']
        assert list(dims) == e['pixels']
        im = Image.open(p).convert('RGB')
        assert im.size == dims
        images[name] = im
        verified.append({'role':name,'file':str(p),'sha256':e['sha256'],'pixels':list(dims)})
    assert images['extended'].crop((115,115,4211,4211)).tobytes() == images['core'].tobytes()
    qp = T / 'qa/root-final-review.json'
    q = read(qp)
    assert q['requiresRepair'] is False
    cov = q['coverage']
    # Partial north has no inner native halo: 53 base + 28 real transitions
    # + four true north and four true east joins, all independently reviewed.
    assert cov['exportedTotal'] == cov['coveredScopes'] == 89
    assert cov.get('allExportedScopesCoveredByActualViewsAndByteIdentity', q.get('allExportedScopesCoveredByActualViewsAndByteIdentity')) is True
    source_entries = [x for x in walk(q) if isinstance(x, dict) and x.get('sha256') == d['outputs']['core']['sha256'] and any(str(x.get(k,'')).replace('\\','/').endswith('/core4096.png') for k in ['file','path'])]
    assert source_entries, 'Root QA does not bind to selected core hash'
    report_hashes = []
    for e in q['reports']:
        p = Path(e['file'])
        assert p.resolve().is_relative_to(T) and p.suffix.lower() == '.json'
        assert sha(p) == e['sha256']
        report_hashes.append({'file':str(p),'sha256':e['sha256']})
    proof = d['selectionProof']
    assert sha(proof['file']) == proof['sha256']
    pr = read(proof['file'])
    assert pr['coreExactlyCenterCrop'] and pr['selectedCopyByteIdenticalToCandidate']
    # Derived cells require explicit current support files. Rejected masks are
    # historical intermediates, not automatically protected by their filename.
    assert isinstance(d.get('technicalArtifacts'), list) and d['technicalArtifacts']
    technical = []
    for e in d['technicalArtifacts']:
        p = Path(e['file']).resolve()
        assert p.is_relative_to(T) and p.is_file() and sha(p) == e['sha256']
        assert e.get('role'), 'Selected technical support needs a purpose'
        check_no_reparse(p)
        technical.append({'file': str(p), 'sha256': e['sha256'], 'role': e['role']})
    # Only current production inputs of unfinished sibling tiles can hold live PNG
    # dependencies. Completed delivery/QA/provenance history is not a live consumer.
    consumers = {}
    scanned = []
    for sibling in T.parent.iterdir():
        if sibling == T or not sibling.is_dir() or not re.fullmatch(r'r\d\d_c\d\d', sibling.name):
            continue
        check_no_reparse(sibling)
        manifest = sibling / 'selected/delivery.manifest.json'
        if manifest.exists() and read(manifest).get('qualifiedComplete4KCandidate') is True:
            continue
        records = list(sibling.glob('regional/context.json'))
        records += [p for p in sibling.glob('jobs/*.json') if not any(s in p.name for s in ['receipt','generation','attempt'])]
        for rp in records:
            check_no_reparse(rp)
            scanned.append({'file':str(rp),'sha256':sha(rp)})
            for v in walk(read(rp)):
                if not isinstance(v,str) or not v.lower().endswith('.png'):
                    continue
                p = Path(v)
                if not p.is_absolute() or not p.resolve().is_relative_to(T):
                    continue
                assert p.exists(), f'Current consumer references missing file: {p}'
                check_no_reparse(p)
                key = str(p.resolve())
                consumers.setdefault(key, {'file':key,'sha256':sha(p),'consumerRecords':[]})['consumerRecords'].append(str(rp))
    return {'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'delivery':{'file':str(dp),'sha256':sha(dp)},'outputs':verified,'technicalArtifacts':technical,'coreExactlyCenterCrop':True,'rootQa':{'file':str(qp),'sha256':sha(qp),'scopes':89},'teamReports':report_hashes,'activeReferences':list(consumers.values()),'scannedCurrentConsumerRecords':scanned,'consumerPolicy':'Unfinished sibling regional context and live job specifications only; completed sibling historical source/QA records are not current consumers. Future neighbors must use selected outputs only.'}

def post(audit):
    assert audit['state'] == 'completed'
    for e in audit['retainedPngFiles'] + audit['preservedNonPngFiles']:
        p = Path(e['file'])
        assert p.is_file() and sha(p) == e['sha256'], f'Protected file changed: {p}'
    for e in audit['deletedFiles']:
        assert not Path(e['file']).exists(), f'Retired PNG still present: {e["file"]}'
    retained = {str(Path(x['file']).resolve()) for x in audit['retainedPngFiles']}
    remaining = {str(p.resolve()) for p in T.rglob('*') if p.is_file() and p.suffix.lower() == '.png'}
    assert remaining == retained
    gate = validate()
    assert gate['delivery']['sha256'] == audit['preflight']['delivery']['sha256']
    existing_sources = []
    for p in sorted((T/'native').glob('*.png.generation.json')):
        existing_sources.append({'file':str(p),'sha256':sha(p)})
    assert len(existing_sources) == 16
    return {'schemaVersion':1,'verifiedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r09_c08','allProtectedHashesUnchanged':True,'allPlannedPngRetired':True,'selectedOutputsVerified':gate['outputs'],'selectedCoreExactlyCenterCrop':True,'retainedPngCount':len(remaining),'preservedNonPngCount':len(audit['preservedNonPngFiles']),'deletedPngCount':len(audit['deletedFiles']),'nativeGenerationTextRecords':existing_sources,'historicalPathPolicy':'Deleted image paths in immutable delivery/source/QA records are historical provenance, not claims of currently existing files. Original paths and hashes are preserved in cleanup.manifest.json and retired-source-paths.json. No original record is rewritten to simulate existence.','deliveryManifestPreservedUnchanged':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--stage', choices=['preflight','post'], required=True)
    args = ap.parse_args()
    result = validate() if args.stage == 'preflight' else post(read(S/'cleanup.manifest.json'))
    print(json.dumps(result, ensure_ascii=False))
