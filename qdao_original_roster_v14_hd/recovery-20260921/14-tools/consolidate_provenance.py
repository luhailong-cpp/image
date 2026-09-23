"""Read-only source inventory; writes two reviewable JSON documents, deletes nothing."""
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime, timezone
import hashlib, json, re
from PIL import Image

ROOT = Path(r'D:\luyuan\wuxingqitan\image').resolve()
BASE = ROOT / 'qdao_original_roster_v14_hd/recovery-20260921'
OUT = BASE / '14-delivery-preview'
GEN = BASE / '14-generation'
HOST = Path(r'C:\Users\Administrator\.codex\generated_images').resolve()
CHAR = '14_short_hair_snow_summoner_girl'
TEXT_EXT = {'.json', '.md', '.txt', '.py'}
IMAGE_EXT = {'.png', '.jpg', '.jpeg', '.webp', '.gif'}
now = datetime.now(timezone.utc).isoformat()

def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()

def document(p):
    b = p.read_bytes()
    s = b.decode('utf-8')
    rec = {'path': str(p.resolve()), 'bytes': len(b), 'sha256': hashlib.sha256(b).hexdigest(), 'text': s}
    if p.suffix == '.json':
        rec['json'] = json.loads(s.lstrip('\ufeff'))
    return rec

def image_fact(p):
    p = p.resolve()
    rec = {'absolutePath': str(p), 'exists': p.is_file()}
    if p.is_file():
        rec.update(bytes=p.stat().st_size, sha256=sha(p))
        with Image.open(p) as im:
            rec.update(size=list(im.size), mode=im.mode, format=im.format)
    return rec

selection = defaultdict(list)
for sidecar in sorted((OUT / 'assets').rglob('*.png.generation.json')):
    meta = json.loads(sidecar.read_text(encoding='utf-8-sig'))
    selection[meta['sourceArchive']].append({
        'file': meta['file'], 'sidecarPath': str(sidecar.resolve()),
        'sourceSHA256': meta['derivedFrom']['sha256'],
        'nativeSize': meta['nativeSize'], 'operation': meta['operation'],
        'finalFileSHA256Authority': 'Read the current sidecar after final color cleanup; intentionally not frozen in this source inventory.'
    })

versions = []
plan = {}
host_candidates = defaultdict(list)
issues = []

def queue(p, purpose, evidence, raw_hash=None):
    p = p.resolve()
    key = str(p).casefold()
    if key not in plan:
        rec = image_fact(p)
        rec.update(purpose=purpose, evidence=[], expectedRawSHA256s=[])
        plan[key] = rec
    rec = plan[key]
    if evidence not in rec['evidence']:
        rec['evidence'].append(evidence)
    if raw_hash and raw_hash not in rec['expectedRawSHA256s']:
        rec['expectedRawSHA256s'].append(raw_hash)

def collect_host(obj, found):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('originalOutputPath', 'savedPath') and isinstance(v, str) and v.lower().endswith('.png'):
                found.add(v)
            elif k == 'output_hint' and isinstance(v, str):
                found.update(re.findall(r'(?<= as )[A-Z]:\\[^\r\n]+?\.png(?= by default)', v, re.I))
            collect_host(v, found)
    elif isinstance(obj, list):
        for v in obj:
            collect_host(v, found)

for folder in sorted(GEN.iterdir()):
    if not folder.is_dir():
        continue
    docs = {p.name: document(p) for p in sorted(folder.iterdir()) if p.is_file() and p.suffix in TEXT_EXT}
    raw = folder / 'raw.png'
    fact = image_fact(raw)
    slots = selection.get(folder.name, [])
    status = 'selected_final_source' if slots else ('unselected_generated_not_counted' if raw.exists() else 'prepared_only_no_workspace_raw')
    entry = {'archive': folder.name, 'directory': str(folder.resolve()), 'status': status,
             'selectedSlots': slots, 'documents': docs, 'rawFile': fact,
             'dispositionNote': 'Unselected is not automatically an explicit artistic rejection; it is excluded from the 136 final slots.'}
    req = docs.get('request.json', {}).get('json', {})
    meta = docs.get('raw.png.generation.json', {}).get('json', {})
    entry['requestedSlot'] = req.get('slot', meta.get('slot'))
    if 'prompt.txt' in docs:
        actual_prompt = req.get('actual_request', {}).get('prompt')
        entry['exactPromptMatchesRequest'] = actual_prompt == docs['prompt.txt']['text']
        entry['promptMatchesRequestAfterLineEndingNormalization'] = actual_prompt == docs['prompt.txt']['text'].replace('\r\n','\n')
        entry['promptTextFileCRLFCount'] = docs['prompt.txt']['text'].count('\r\n')
        if actual_prompt is not None and not entry['promptMatchesRequestAfterLineEndingNormalization']:
            issues.append({'archive':folder.name,'issue':'prompt.txt differs from actual_request.prompt; both exact originals are preserved'})
    if fact['exists']:
        recorded_hash = meta.get('sha256')
        entry['rawMatchesRecordedSHA256'] = fact['sha256'] == recorded_hash if recorded_hash else None
        if recorded_hash and recorded_hash != fact['sha256']:
            issues.append({'archive': folder.name, 'issue':'raw hash differs from metadata'})
        queue(raw, 'Temporary native source already represented by a selected final export or excluded variant.', folder.name, fact['sha256'])
    found = set()
    for doc in docs.values():
        if 'json' in doc:
            collect_host(doc['json'], found)
    entry['hostOriginalPaths'] = sorted(found)
    for path in found:
        p = Path(path).resolve()
        if not p.is_relative_to(HOST) or p.suffix.lower() != '.png':
            issues.append({'archive':folder.name, 'issue':'host output path outside expected generated_images root', 'path':str(p)})
            continue
        queue(p, 'Host-generated original belonging to this character version, evidenced by saved output metadata/receipt.', folder.name, fact.get('sha256'))
    versions.append(entry)

reference_docs = [document(p) for p in sorted((BASE / '14-reference').rglob('*')) if p.is_file() and p.suffix in TEXT_EXT]
working_docs = []
for name in ['14-work-E-SE', '14-work-NE', '14-work-W-NW']:
    for p in sorted((BASE / name).rglob('*')):
        if p.is_file() and p.suffix in TEXT_EXT:
            working_docs.append(document(p))
for name in ['14-work-S-SW.md', '14-HANDOFF-20260923.md']:
    p = BASE / name
    if p.exists():
        working_docs.append(document(p))

image_roots = [BASE / n for n in ['14-generation', '14-reference', '14-work-E-SE', '14-work-NE', '14-work-W-NW']]
image_roots.append(OUT / 'review-temp')
for scope in image_roots:
    assert scope.resolve().is_relative_to(BASE.resolve())
    if not scope.exists():
        continue
    for p in sorted(scope.rglob('*')):
        if p.is_file() and p.suffix.lower() in IMAGE_EXT:
            purpose = 'Temporary transport-only identity reference.' if scope.name == '14-reference' else ('Temporary contact sheet, enlarged leg review, or seam inspection image.' if scope.name != '14-generation' else 'Temporary native generation source.')
            queue(p, purpose, str(p.relative_to(BASE)))

entries = sorted(plan.values(), key=lambda x:x['absolutePath'].casefold())
for item in entries:
    p = Path(item['absolutePath'])
    item['scope'] = 'workspace' if p.is_relative_to(ROOT) else 'host_generated_images'
    item['proposedAction'] = 'delete_after_final_export_and_reference_verification' if item['exists'] else 'no_action_missing'
    if item['exists'] and item['expectedRawSHA256s']:
        item['matchesAtLeastOneArchivedRawSHA256'] = item['sha256'] in item['expectedRawSHA256s']
        if not item['matchesAtLeastOneArchivedRawSHA256']:
            issues.append({'path': item['absolutePath'], 'issue':'Output PNG does not match any associated archived raw hash; hold for review.'})
            item['proposedAction'] = 'hold_for_manual_review'

protected = [
    ROOT / 'q_daoist_character_pack_4096/14_short_hair_snow_summoner_girl_transparent_4096.png',
    ROOT / 'designs/jubaozhai-ui/02-characters.png', OUT / 'assets'
]
for item in entries:
    p = Path(item['absolutePath'])
    assert not any(p == q.resolve() or p.is_relative_to(q.resolve()) for q in protected), item['absolutePath']

summary = {'versionCount':len(versions), 'statusCounts':dict(Counter(v['status'] for v in versions)),
           'selectedArchives':len(selection), 'selectedSlots':sum(map(len,selection.values())),
           'cleanupImageEntries':len(entries), 'existingCleanupImages':sum(x['exists'] for x in entries),
           'existingWorkspaceImages':sum(x['exists'] and x['scope']=='workspace' for x in entries),
           'existingHostImages':sum(x['exists'] and x['scope']=='host_generated_images' for x in entries),
           'issues':issues}
provenance = {'schemaVersion':1, 'character':CHAR, 'createdAt':now, 'summary':summary,
              'retentionRule':'Keep final game assets and text evidence. Remove temporary images only after final verification. No file was deleted by this inventory.',
              'modelEvidenceRule':'Configuration target, submitted parameters, host receipts, and returned evidence are preserved separately. Unexposed actual model/quality remain unconfirmed.',
              'finalAssetAuthority':'Current assets/*.generation.json; mutable final PNG hashes intentionally omitted during final edge cleanup.',
              'versions':versions, 'referenceDerivationDocuments':reference_docs, 'supportingWorkDocuments':working_docs}
cleanup = {'schemaVersion':1, 'character':CHAR, 'createdAt':now, 'executed':False, 'summary':summary,
           'preconditions':['All 128 walk and 8 independent idle PNGs exist and are accepted.', 'Read current final sidecars after edge cleanup; verify final PNG SHA and all preview references.', 'Rehash every candidate immediately before deleting. Do not delete if path or SHA changed.', 'Preserve this consolidated exact text provenance before removal.'],
           'protectedNotCandidates':[str(p.resolve()) for p in protected],
           'explicitlyExcluded':'Shared original identity portrait, approved style reference, other characters, final PNGs, final preview, all text files, and any path not explicitly enumerated here.',
           'entries':entries}
for name, payload in [('provenance.json',provenance), ('source-cleanup-plan.json',cleanup)]:
    p=OUT/name
    p.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
