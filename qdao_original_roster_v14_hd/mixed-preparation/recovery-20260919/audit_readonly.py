"""Read-only recovery audit; writes only this recovery directory's report."""
from pathlib import Path
import hashlib
import json
import sys
from datetime import datetime, timezone

ROOT = Path('E:/work/image/qdao_original_roster_v14_hd')
V13 = ROOT.parent / 'qdao_original_roster_v13'
HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT / 'tools'))
import publish_mixed_roster as pub

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def resources(project):
    base = project / pub.CHARACTERS
    return {p.relative_to(base).as_posix(): sha(p) for p in sorted(base.rglob('*')) if p.is_file()}

def action_paths(directory):
    return {f'walk/{d}/{i:02d}.png' for d in pub.gate.DIRECTIONS for i in range(1, 17)
            if (directory / f'walk/{d}/{i:02d}.png').is_file()} | {
                f'idle/{d}.png' for d in pub.gate.DIRECTIONS if (directory / f'idle/{d}.png').is_file()}

all_actions = {f'walk/{d}/{i:02d}.png' for d in pub.gate.DIRECTIONS for i in range(1,17)} | {
    f'idle/{d}.png' for d in pub.gate.DIRECTIONS}
inventory = json.loads((V13 / 'inventory.json').read_text(encoding='utf-8-sig'))
ids = sorted(row['character_id'] for row in inventory['characters'])
rows = []
for character in ids:
    old = action_paths(V13 / 'candidate' / character)
    new = action_paths(ROOT / 'candidate' / character)
    rows.append({'character_id':character,'preserved_walk':sum(p.startswith('walk/') for p in old),
                 'preserved_idle':sum(p.startswith('idle/') for p in old),
                 'new_unique_walk':sum(p.startswith('walk/') for p in new-old),
                 'new_unique_idle':sum(p.startswith('idle/') for p in new-old),
                 'excluded_pilot_or_existing_slots':sorted(new&old),
                 'missing':sorted(all_actions-old-new)})
formal, isolated = pub.FORMAL, pub.ISOLATED
formal_files, isolated_files = resources(formal), resources(isolated)
bindings = []
for p in pub.BINDINGS:
    left, right = formal/p, isolated/p
    bindings.append({'path':p,'formal_sha256':sha(left),'isolated_sha256':sha(right),'equal':sha(left)==sha(right)})
locks = []
for project in (formal,isolated):
    try:
        pub.stage.editor_closed(project)
        closed = True
        error = None
    except Exception as exc:
        closed,error = False,str(exc)
    locks.append({'project':str(project),'lock_file_exists':(project/'Temp/UnityLockfile').exists(),
                  'exclusive_read_check_editor_closed':closed,'error':error})
report = {'schema':'qdao-roster-recovery-readonly-audit-v1','created_utc':datetime.now(timezone.utc).isoformat(),
    'scope':'File inventory and bound-input recovery check, not visual approval or generation attestation',
    'characters':rows,'missing_walk_total':sum(sum(p.startswith('walk/') for p in r['missing']) for r in rows),
    'missing_idle_total':sum(sum(p.startswith('idle/') for p in r['missing']) for r in rows),
    'formal_character_file_count':len(formal_files),'isolated_character_file_count':len(isolated_files),
    'formal_vs_isolated':{'only_formal':sorted(formal_files.keys()-isolated_files.keys()),
        'only_isolated':sorted(isolated_files.keys()-formal_files.keys()),
        'different':sorted(p for p in formal_files.keys()&isolated_files.keys() if formal_files[p]!=isolated_files[p])},
    'source_bindings':bindings,'editor_lock_checks':locks,
    'pipeline_files':{p.name:sha(p) for p in (ROOT/'tools').glob('*') if p.is_file()},
    'authoritative_handoff_is_stale_about_mixed_tools':True,
    'receipt_unavailable_is_not_accepted_by_existing_native_assembler':True}
output = HERE/'readonly-recovery-audit.json'
output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'report':str(output),'characters':len(rows),'missing_walk':report['missing_walk_total'],
 'missing_idle':report['missing_idle_total'],'formal_files':len(formal_files),'isolated_files':len(isolated_files),
 'resource_differences':{k:len(v) for k,v in report['formal_vs_isolated'].items()},
 'bound_sources':len(bindings),'bound_sources_equal':sum(b['equal'] for b in bindings),'locks':locks},ensure_ascii=False))
