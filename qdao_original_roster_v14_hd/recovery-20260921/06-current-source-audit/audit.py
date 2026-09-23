"""Read-only source inventory; writes reports only in this isolated directory."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, collections
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHAR = '06_thunder_caster_boy'
V14 = ROOT / 'qdao_original_roster_v14_hd'
OLD = ROOT / 'qdao_original_roster_v13' / 'candidate' / CHAR
LIVE = V14 / 'candidate' / CHAR
GEN = V14 / 'generation' / CHAR
ISOLATED = V14 / 'recovery-20260921' / '06-audit'
DIRS = ['N','NE','E','SE','S','SW','W','NW']

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def file_record(p):
    result = {'path': str(p), 'bytes': p.stat().st_size, 'sha256': sha(p)}
    if p.suffix.lower() == '.png':
        with Image.open(p) as im:
            result.update(size=list(im.size), mode=im.mode)
            im.verify()
        with Image.open(p) as im:
            im.load()
            result['pixel_sha256'] = hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest()
            if 'A' in im.getbands():
                result['alpha_range'] = list(im.getchannel('A').getextrema())
                result['alpha_bbox'] = im.getchannel('A').getbbox()
    return result

areas = {'v13_candidate': OLD, 'v14_candidate': LIVE, 'generation': GEN,
         'isolated_06_audit': ISOLATED}
inventory = {label:[file_record(p) for p in sorted(folder.rglob('*')) if p.is_file() and '__pycache__' not in p.parts]
             for label,folder in areas.items()}
index = {r['path']:r for rows in inventory.values() for r in rows}
manifest_checks = []
for folder in (OLD, LIVE, ISOLATED/'candidate'/CHAR):
    manifest=read(folder/'manifest.json')
    for row in manifest['files']:
        p=folder/row['path']
        manifest_checks.append({'path':str(p),'exists':p.exists(), 'expected_sha256':row['sha256'],
                                'actual_sha256':sha(p) if p.exists() else None,
                                'matches':p.exists() and sha(p)==row['sha256']})

baseline = [file_record(p) for p in sorted(OLD.rglob('*.png')) if p.parent.name == 'idle' or (p.parent.name == 'S' and p.stem.isdigit())]
raw_checks=[]
prior=read(ISOLATED/'source-audit.json')['images']
paused={r['batch']:r for r in read(GEN/'inventory-at-pause-20260919.json')['batches']}
for row in prior:
    p=Path(row['path']); cur=file_record(p)
    cur.update(batch=row['batch'],rejected=row['rejected'],
               matches_prior_audit=cur['sha256']==row['sha256'],
               matches_paused_inventory=cur['sha256']==paused[row['batch']]['raw_sha256'])
    cur['bound_files'] = [{'path':str(p.parent/name),'sha256':sha(p.parent/name),'matches_prior_audit':sha(p.parent/name)==row[key]} for name,key in [('prompt.txt','prompt_sha256'),('generation-receipt.json','receipt_sha256')]]
    raw_checks.append(cur)
known={r['path'] for r in raw_checks}
extra_raw=[str(p) for p in GEN.rglob('raw.png') if str(p) not in known]
live_frames={d:[int(p.stem) for p in sorted((LIVE/'walk'/d).glob('*.png')) if p.stem.isdigit()] for d in DIRS}
old_frames={d:[int(p.stem) for p in sorted((OLD/'walk'/d).glob('*.png')) if p.stem.isdigit()] for d in DIRS}
isolate_frames={d:[int(p.stem) for p in sorted((ISOLATED/'candidate'/CHAR/'walk'/d).glob('*.png')) if p.stem.isdigit()] for d in DIRS}
union_frames={d:sorted(set(live_frames[d])|set(old_frames[d])) for d in DIRS}
recovered_frames={d:sorted(set(union_frames[d])|set(isolate_frames[d])) for d in DIRS}
pending=[{'frame':f, 'raw':str(GEN/f'E{f:02d}-single-v1'/'raw.png'),
          'isolated_output':str(ISOLATED/'candidate'/CHAR/'walk'/'E'/f'{f:02d}.png'),
          'canonical_target':str(LIVE/'walk'/'E'/f'{f:02d}.png'),
          'target_exists':(LIVE/'walk'/'E'/f'{f:02d}.png').exists()} for f in [4,6,13]]
duplicate_groups={}
for label, rows in inventory.items():
    outputs=[r for r in rows if '/walk/' in r['path'].replace('\\','/') and Path(r['path']).stem.isdigit()]
    groups=collections.defaultdict(list)
    for r in outputs: groups[r['pixel_sha256']].append(r['path'])
    duplicate_groups[label]=[g for g in groups.values() if len(g)>1]
text_reconciliation=[]
for row in read(ISOLATED/'snapshot-text-reconciliation.json')['rows']:
    p=LIVE/row['path']; current=p.read_bytes(); restored=current.replace(b'\r\n',b'\n').replace(b'\n',b'\r\n')
    text_reconciliation.append({'path':str(p),'current_sha256':sha(p),
        'matches_prior_live':sha(p)==row['live_current_sha256'],
        'crlf_sha256':hashlib.sha256(restored).hexdigest(),
        'crlf_matches_historical':hashlib.sha256(restored).hexdigest()==row['historical_recorded_sha256'],
        'live_changed':False})
summary={'checked_at_utc':datetime.now(timezone.utc).isoformat(), 'read_only_source_audit':True,
         'live_frames':live_frames,'old_frames':old_frames,'isolated_frames':isolate_frames,
         'combined_current_walk_count':sum(map(len,union_frames.values())),
         'combined_with_recovered_walk_count':sum(map(len,recovered_frames.values())),
         'old_idle_count':len(list((OLD/'idle').glob('*.png'))),
         'missing_after_recovery':{d:[f for f in range(1,17) if f not in recovered_frames[d]] for d in DIRS},
         'remaining_walk_count_after_recovery':128-sum(map(len,recovered_frames.values())),
         'pending_recovered':pending,'unknown_generation_raw':extra_raw,
         'all_manifest_output_hashes_match':all(r['matches'] for r in manifest_checks),
         'all_9_raw_hashes_match_prior':all(r['matches_prior_audit'] and r['matches_paused_inventory'] for r in raw_checks),
         'exact_pixel_duplicate_groups_by_area':duplicate_groups,
         'visual_approval':False,'old_outputs_are_512':all(r['size']==[512,512] for r in baseline)}
for name, value in [('inventory.json',inventory),('old-byte-baseline.json',baseline),('manifest-checks.json',manifest_checks),
                    ('raw-checks.json',raw_checks),('text-byte-checks.json',text_reconciliation),('summary.json',summary)]:
    (HERE/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
