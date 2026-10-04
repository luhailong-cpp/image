"""Finalize reviewed 20261004 revisions; preserve textual evidence when cleaning sources."""
import argparse
from pathlib import Path
from revise_feet_20261003 import ROOT, read, save, sha, now, scoped
from build_preview import main as build_html

REVISIONS = ['direction-alignment-20261004', 'direction-combat-20261004', 'run-grounding-20261004']
REV = ROOT / 'review' / REVISIONS[-1]

def phases():
    m = read(ROOT / 'manifest.json')
    assert len(read(REV / 'replacement-ledger.json')['replacements']) == len(read(REV / 'selection.json')['selected'])
    plans = {p['direction']: p for p in read(REV / 'plan.json')['directions']}
    labels = ['contact', 'absorb', 'support', 'support', 'drive', 'drive', 'toe_off', 'toe_off']
    positions = ['front_landing', 'under_body', 'rear_drive', 'final_forefoot']
    evidence = {}
    for f in m['frames']:
        if f['action'] != 'run': continue
        i = f['index']; half = 'A' if i < 8 else 'B'; phase = labels[i % 8] + '_' + half
        f['phase'] = phase
        f['events'] = ['contact_' + half] if i in (0,8) else ['toe_off_' + half] if i in (7,15) else []
        f['support'] = {'halfCycle': half, 'foot': plans[f['direction']]['support' + half],
                        'position': positions[(i % 8) // 2], 'pairNumber': i // 2 + 1,
                        'scope': 'drawn support phase only; no collision or automatic foot locking'}
        evidence.setdefault(f['direction'], []).append({'frame': i+1, 'phase': phase,
            'support': f['support'], 'sha256': f['sha256']})
    save(ROOT / 'manifest.json', m)
    save(ROOT / 'review/run-phase-review.json', {'updatedAt': now(), 'frameNumbering': '1-based filenames; index in manifest is 0-based',
        'basis': 'Actual native edits and full per-direction sequence review; support persists through four pairs, with perspective retained.',
        'pattern': '01-02 front landing;03-04 under body;05-06 rear drive;07-08 final forefoot.09-16 opposite foot repeats.',
        'sourceReview': 'review/run-grounding-20261004/plan.json', 'directions': evidence,
        'clientTested': False, 'scope': 'offline visual phase labels; not physics or collision events'})
    assert build_html() == 0
    print('Updated actual-frame support labels and landing/toe-off markers.')

def prompt_indexes():
    for name in REVISIONS:
        rev = ROOT / 'review' / name; stage = ROOT / 'staging' / name
        chosen = {scoped(p) for p in read(rev / 'selection.json')['selected'].values()}
        records = []
        for p in sorted(stage.rglob('*.png.generation.json')):
            native = Path(str(p).removesuffix('.generation.json'))
            stem = str(native).removesuffix('.png')
            request, receipt = Path(stem+'.request.json'), Path(stem+'.receipt.json')
            assert request.is_file() and receipt.is_file(), str(p)
            nr = read(p)
            records.append({'candidate': native.relative_to(stage).as_posix(),
                'request': request.relative_to(ROOT).as_posix(), 'receipt': receipt.relative_to(ROOT).as_posix(),
                'nativeRecord': p.relative_to(ROOT).as_posix(), 'nativeSHA256': nr['sha256'],
                'selectedAtRevision': native in chosen})
        save(rev / 'prompt-index.json', {'route':'builtin image_gen.imagegen', 'actualModel':None, 'actualQuality':None,
             'configuredBatch':'20261001 continuing batch; see per-image snapshots; actual version/quality not exposed', 'candidates':records})

def accept():
    m = read(ROOT / 'manifest.json'); review = read(REV / 'final-review.json')
    assert review['passed'] is True and review['scope'] == 'offline'
    assert review['frameSHA256'] == {f['id']: f['sha256'] for f in m['frames']}
    assert read(REV / 'timing-verification.json')['passed']
    assert read(REV / 'browser-check.json')['passed']
    assert read(ROOT / 'review/direction-combat-20261004/browser-check.json')['passed']
    for f in m['frames']:
        f['visualApproved'] = True
        f['visualReviewScope'] = 'Current direction and support sequence review; native edits, final contact sheets and browser state checks; offline only. See run-grounding final-review.json.'
        rec = read(ROOT / f['sourceRecord']); rec['visualApproved'] = True; save(ROOT / f['sourceRecord'], rec)
    revisions = {n: sorted(read(ROOT/'review'/n/'selection.json')['selected']) for n in REVISIONS}
    m.update({'formalAccepted':True, 'updatedAt':now(),
        'currentReview':{'status':'offline_complete','record':'review/run-grounding-20261004/final-review.json',
            'revisions':revisions,'referenceCharacter':'09_bamboo_archer_girl','client':'not_tested'},
        'note':f"196 independent frames; direction-axis and combat corrections plus{len(revisions[REVISIONS[-1]])} run-support edits; normal run1200ms/16x75ms; offline acceptance only."})
    save(ROOT / 'manifest.json', m)
    save(ROOT / 'review/final-visual-review.json', {'reviewedAt':now(),'offlineAccepted':True,'scope':review['method'],
        'acceptedSHA256':review['frameSHA256'],'revisionReview':'review/run-grounding-20261004/final-review.json','clientTested':False})
    save(ROOT / 'preview/progress.json', {'frames':196,'offlineAccepted':196,'clientIntegrated':0})
    prompt_indexes()
    assert build_html() == 0
    print('Current196-frame offline review accepted. Client remains untested.')

def cleanup():
    from verify_manifest import verify
    m = read(ROOT / 'manifest.json'); assert m['formalAccepted']
    pre = verify(m, True); assert pre['passed'], pre['errors']
    archive = REV / 'before-cleanup-structure-report.json'
    assert not archive.exists(), 'Cleanup already started; inspect before retry.'
    removed = []
    candidates = []
    for name in REVISIONS:
        stage = scoped('staging/'+name)
        candidates.extend(stage.rglob('*.png'))
        candidates.extend(scoped('review/'+name).glob('candidate-*-contact.jpg'))
        candidates.extend(scoped('review/'+name).glob('*-candidate-contact.png'))
    for p in sorted(set(candidates)):
        p = scoped(p)
        assert p.is_file() and (p.is_relative_to(ROOT/'staging') or (p.parent.parent==ROOT/'review' and (p.name.startswith('candidate-') or p.name.endswith('-candidate-contact.png'))))
        removed.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,
                        'reason':'verified final export retained; temporary native/rejected edit or QA contact sheet','at':now()})
    save(archive, read(ROOT/'review/pre-cleanup-structure-report.json'))
    save(ROOT/'review/pre-cleanup-structure-report.json', pre)
    ledger = read(ROOT/'review/cleanup-ledger.json')
    prior = {x['path'] for x in ledger['removed']}
    assert not prior.intersection(x['path'] for x in removed)
    ledger['removed'].extend(removed); ledger['lastRevisionCleanupAt']=now()
    ledger['verificationReports']=list(dict.fromkeys(ledger.get('verificationReports',[])+[archive.relative_to(ROOT).as_posix(),'review/pre-cleanup-structure-report.json']))
    save(ROOT/'review/cleanup-ledger.json',ledger)
    # A filename can have several historical contents. Match both path and SHA.
    historical = {}
    key = lambda p,d: (str(Path(p).resolve()).replace('\\','/').lower(), d)
    for name in REVISIONS:
        for x in read(ROOT/'review'/name/'replacement-ledger.json')['replacements']:
            historical[key(ROOT/x['path'],x['previousSHA256'])] = str(ROOT/x['previousSourceRecord'])
    for x in removed:
        p=ROOT/x['path']; rec=Path(str(p)+'.generation.json')
        historical[key(p,x['sha256'])] = str(rec) if rec.exists() else None
    def patch_history(obj):
        if isinstance(obj,list):
            for item in obj: patch_history(item)
        elif isinstance(obj,dict):
            if 'path' in obj and 'sha256' in obj:
                pair=key(obj['path'] if Path(obj['path']).is_absolute() else ROOT/obj['path'],obj['sha256'])
                if pair in historical:
                    obj['historicalPath']=obj.pop('path'); obj['historicalSource']=True
                    obj['disposition']='source replaced or removed after verified export; SHA and text retained'
                    if historical[pair]: obj['generationRecord']=historical[pair]
            for value in obj.values(): patch_history(value)
    texts = set(ROOT.rglob('*.png.generation.json'))
    for name in REVISIONS: texts.update((ROOT/'review'/name/'superseded-records').glob('*.json'))
    removed_paths = {x['path'] for x in removed}
    for p in texts:
        nr=read(p)
        native=Path(str(p).removesuffix('.generation.json'))
        if native.relative_to(ROOT).as_posix() in removed_paths:
            nr['assetDisposition']='source_removed_after_verified_export'; nr['cleanupLedger']='review/cleanup-ledger.json'
        patch_history(nr); save(p,nr)
    for f in m['frames']:
        native=f['nativeProvenance']
        if native['historicalPath'] in removed_paths:
            native['disposition']='removed_after_verified_export'; native['verifiedBeforeCleanup']=True
    save(ROOT/'manifest.json',m)
    for x in removed:
        p=scoped(x['path']); assert sha(p)==x['sha256']; p.unlink()
    report=verify(m,True); save(ROOT/'preview/structure-report.json',report); assert report['passed'],report['errors']
    assert build_html()==0
    save(REV/'cleanup-result.json',{'at':now(),'removedImages':len(removed),'totalLedgerEntries':len(ledger['removed']),'structurePassed':True})
    print(f'Cleaned{len(removed)} temporary images; all final frames and textual provenance retained.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['phases','accept','cleanup','prompt_indexes'])
    globals()[p.parse_args().mode]()
