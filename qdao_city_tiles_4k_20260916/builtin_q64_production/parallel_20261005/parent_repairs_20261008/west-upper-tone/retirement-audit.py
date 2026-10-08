from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, sys

T = Path(__file__).resolve().parent
A = T.parent.parent / 'parent_audit_20261008'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p, data): Path(p).write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def ref(p): return {'path':Path(p).as_posix(),'sha256':sha(p),'bytes':Path(p).stat().st_size}
def now(): return datetime.now(timezone.utc).isoformat()
record = T / 'retirement.json'
keep = ['context.png','final-joined.png','mask.png','trim-mask.png']
keep += [f'final-output/{x}.png' for x in ['r08_c07','r08_c08']]
keep += [f'final-qa/{x}.png' for x in ['bottom-return','bottom-trim','diagonal-trim','gray-lower','gray-upper','left-return','right-return','upper-relief']]
retire = ['joined.png','native.png','output/r08_c07.png','output/r08_c08.png']
retire += [f'qa/{x}.png' for x in ['bottom-return','bottom-trim','diagonal-trim','gray-lower','gray-upper','left-return','right-return','upper-relief']]
retire += ['trim-gap/context.png','trim-gap/native.png','trim-repair/native.png','trim-repair/notch-qa.png']

def verify_current():
    manifest = read(T/'final-manifest.json')
    index = read(A/'verified-current-index.json')
    tian = next(x for x in index['appearances'] if x['appearance']=='tianyong_festival')
    overlay = read(A/'parent-repair-current-overlay.json')
    for o in manifest['outputs']:
        assert sha(o['file']) == o['sha256']
        tile = o['source']['tile']
        parent = next(e for e in tian['entries'] if e['tileId']==tile)['parentRepairCandidate']
        selection = next(e for e in overlay['candidates'] if e.get('tile')==tile)
        assert Path(parent['path']).resolve() == Path(o['file']).resolve() == Path(selection['file']).resolve()
        assert parent['sha256'] == selection['sha256'] == o['sha256']
        assert sha(o['source']['file']) == o['source']['sha256']
    assert sha(T/'final-review.json')=='b42c8eb1a85401ee8bb18cc374c77e6e6f9f98ba4367bb38352e62e012945e78'
    assert sha(T/'final-manifest.json')=='6b78680e6923f17dbb8a17e898d72e28b70d431a1e99c34f91bdc4683352ca47'
    return manifest

if sys.argv[1] == 'prepare':
    assert not record.exists(), 'Already planned; do not resnapshot history.'
    manifest = verify_current()
    actual = {p.relative_to(T).as_posix() for p in T.rglob('*.png')}
    assert actual == set(keep+retire), (actual-set(keep+retire),set(keep+retire)-actual)
    for name in keep+retire:
        p=T/name
        assert p.resolve().is_relative_to(T) and not p.is_symlink()
    protected = [A/'verified-current-index.json',A/'parent-repair-current-overlay.json',A/'west-upper-tone-independent-review.json']
    protected += [Path(o['source']['file']) for o in manifest['outputs']]
    protected += list((T.parent/'current').glob('*.json'))
    originals = [ref(p) for p in T.rglob('*') if p.is_file() and p.suffix.lower()!='.png' and p.name!='retirement-audit.py']
    data = {'createdAtUtc':now(),'status':'verified_ready_for_scoped_retirement','scope':T.as_posix(),
        'policy':'User-authorized removal of unused originals, rejected attempts and intermediate PNG after final output and active parent references are verified. No backup. All existing text remains byte-identical.',
        'keptPng':[dict(ref(T/n),relativePath=n,available=True,role=('final output' if n.startswith('final-output/') else 'current source-bound QA' if n.startswith('final-qa/') else 'migration context or mask' if n!='final-joined.png' else 'current assembled reference and inspection image')) for n in keep],
        'retiredPng':[dict(ref(T/n),relativePath=n,available=True,plannedAvailability=False,runtimeDependency=False,reason='Superseded source or intermediate; retained text provenance describes historical identity. Final two PNGs contain accepted scoped composite pixels.') for n in retire],
        'preexistingText':originals,'protectedExternalFiles':[ref(p) for p in protected],
        'externalReferenceAudit':{'scanRoots':['D:/work/image','D:/work/mmorpg-client'],'method':'rg -l --hidden -F west-upper-tone across JSON/Markdown/Python/TOML/PowerShell/TS/JS/CS. All non-branch matches manually classified.',
            'activeDelivery':'Parent index, overlay, current status, READMEs and scoped review point to retained final-output/final-joined/final-qa or metadata.',
            'historicalReferences':'Old outputs/native entries nested in base candidate histories, generation records, prompts and audits are evidence, not current pixel inputs.',
            'scripts':'assemble.py, prepare_trim_gap.py, finalize_review.py, trim-repair/crop.py are retired construction/review scripts; do not rerun. REP/prepare_tone.py is historical setup and is not run.',
            'gitSyncQueue':'Observed pending batch references. Read-only consumer audit confirms pending() filters missing untracked files; each batch intersects fresh pending paths; to_stage checks exists or tracked deletion, and missing-path races retry. Queue references do not require source PNG retention. No .git files changed.',
            'clientReferences':'No west-upper-tone reference found in D:/work/mmorpg-client.'},
        'futureMigration':'Use final-output, original context, mask and trim-mask with the retained source windows and SHA metadata; do not rebuild from retired native PNG paths.',
        'formalAccepted':False}
    dump(record,data)
    print(json.dumps({'prepared':True,'keep':len(keep),'retire':len(retire),'retireBytes':sum(x['bytes'] for x in data['retiredPng']),'existingText':len(originals),'indexSha':sha(A/'verified-current-index.json')}))
elif sys.argv[1] == 'finalize':
    data=read(record)
    verify_current()
    for r in data['keptPng']+data['preexistingText']+data['protectedExternalFiles']:
        assert sha(r['path'])==r['sha256'],r['path']
    for r in data['retiredPng']:
        assert not Path(r['path']).exists(),r['path']
        r.update(available=False,retiredAtUtc=now())
    assert {p.relative_to(T).as_posix() for p in T.rglob('*.png')}==set(keep)
    data.update(status='complete',completedAtUtc=now(),deletedCount=len(retire),deletedBytes=sum(x['bytes'] for x in data['retiredPng']))
    dump(record,data)
    verification={'verifiedAtUtc':now(),'status':'pass','retirement':ref(record),'keptPngCount':len(keep),'retiredPngCount':len(retire),'deletedBytes':data['deletedBytes'],'allRetainedPngUnchanged':True,'allPreexistingTextUnchanged':True,'protectedExternalFilesUnchanged':True,'parentIndexOutputHashesMatch':True,'formalAccepted':False}
    dump(T/'post-retirement-verification.json',verification)
    print(json.dumps(verification))
else:
    raise ValueError('Use prepare or finalize; deletion is intentionally performed only with native PowerShell LiteralPath.')
