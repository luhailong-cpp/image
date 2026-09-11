"""Create a read-only visual-file snapshot; never modify source images."""
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent
VISUAL = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.bmp', '.tif', '.tiff', '.svg'}

def read_json(path):
    f = ROOT / path
    return json.loads(f.read_text(encoding='utf-8-sig')) if f.exists() else {}

def family(path):
    p = path.lower()
    if p.startswith('tianyong_'):
        return 'world_map'
    if p.startswith(('character_move_8dir/', 'qdao_chibi_roster_v11/')):
        return 'character_movement'
    if p.startswith(('q_daoist_character_pack_4096/', 'qdao_character_diversity_v9/')) or ('/' not in p and ('character' in p or 'hero' in p)):
        return 'characters'
    if p.startswith(('qdao_chibi_pets_v1/', 'qdao_ui_redesign_v5/pet/', 'qdao_asset_refresh_v6/pets/')):
        return 'pets'
    if p.startswith('qdao_asset_refresh_v6/icons/') or any(x in p for x in ('qstyle_redrawn_600x600', 'character_artifacts_redrawn_24_600x600', 'west_eight_immortals_redrawn_100_600x600')):
        return 'items_and_atlases'
    if p.startswith('client_ui_refresh_20260908/'):
        return 'client_exports'
    if p.startswith(('designs/', 'exact_qdao_slices/', 'qdao_ui_style_recut_v10/', 'qdao_gpt_image2_refresh_v7/ui/', 'q_daoist_login_ui_')) or any(x in p for x in ('/components/', '/hud/')):
        return 'ui_and_slices'
    if p.startswith(('qdao_ui_redesign_v5/', 'qdao_chibi_game_pack_v4/')) or '/' not in p:
        return 'scene_illustrations'
    return 'other_review'

def role(path):
    p = path.lower()
    parts = p.split('/')
    if any(x in parts for x in ('.work', 'backups', 'staged', 'samples', 'contacts', 'thumbs', '__pycache__')) or p.startswith('docs/style-audit-'):
        return 'supporting_history_or_work'
    if '/qa/' in p or 'screenshot' in p:
        return 'evidence_do_not_repaint'
    if p.startswith('docs/references/') or 'reference' in Path(p).name:
        return 'reference_do_not_repaint'
    if p.startswith('tianyong_festival_'):
        return 'new_design_preview'
    if '/source/' in p or '/sources/' in p:
        return 'source_review_pending'
    return 'asset_review_pending'

exposure = {r['path']: r for r in read_json('qdao_exposure_refinement_v8/processing.json').get('records', [])}
audit = {r['path']: r for r in read_json('docs/style-audit-20260909/results.json').get('records', [])}
contracts = {r['path']: r for r in read_json('qdao_ui_style_recut_v10/contracts/current_files.json').get('files', [])}
cmd = ['rg', '--files', '--hidden', '-g', '!.git/**', '-g', '!node_modules/**', '-g', '!**/node_modules/**', '-g', '!.agents/**', '-g', '!.codex/**', '-g', '!qdao_festival_refinement_20260910/**']
listed = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, encoding='utf-8').stdout.splitlines()
records = []
errors = []
for rel in sorted({p.replace('\\', '/') for p in listed if Path(p).suffix.lower() in VISUAL}):
    f = ROOT / rel
    try:
        stat = f.stat()
        r = {'path': rel, 'family': family(rel), 'role': role(rel), 'bytes': stat.st_size, 'mtime_ns': stat.st_mtime_ns, 'review_status': 'not_visually_reviewed_in_this_pass', 'edit_status': 'not_started'}
        if f.suffix.lower() == '.svg':
            doc = ET.parse(f).getroot()
            r['svg_size'] = {k: doc.attrib[k] for k in ('width', 'height', 'viewBox') if k in doc.attrib}
        else:
            with Image.open(f) as im:
                r.update(size=list(im.size), mode=im.mode, frames=getattr(im, 'n_frames', 1), alpha_present='A' in im.getbands() or 'transparency' in im.info)
        after = f.stat()
        r['stable_during_header_read'] = (stat.st_size, stat.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
        if rel in exposure:
            e = exposure[rel]
            r['prior_exposure_record'] = {k: e[k] for k in ('output_sha256', 'canonical_path', 'expected_size', 'status', 'classification') if k in e}
            r['prior_exposure_record']['current_hash_reverified'] = False
        if rel in audit:
            a = audit[rel]
            r['historical_audit'] = {k: a[k] for k in ('sha256', 'verdict', 'reason', 'action', 'issue_tags') if k in a}
            r['historical_audit']['applies_to_current_pixels'] = 'unverified'
        if rel in contracts:
            c = contracts[rel]
            r['ui_contract'] = {k: c[k] for k in ('family', 'source_manifest', 'metadata', 'size', 'allowed_unchanged') if k in c}
        if r['role'] in ('supporting_history_or_work', 'evidence_do_not_repaint', 'reference_do_not_repaint'):
            r['planned_action'] = 'retain_as_supporting_material'
        else:
            r['planned_action'] = 'review_latest_delivery_after_global_prerequisites_complete'
        records.append(r)
    except Exception as exc:
        errors.append({'path': rel, 'error': str(exc)})

snapshot = {
    'schema_version': 1,
    'captured_at_utc': datetime.now(timezone.utc).isoformat(),
    'root': ROOT.as_posix(),
    'stage': 'preparation_only',
    'images_modified': 0,
    'completion_claim': False,
    'scope': 'All rg-visible visual files, including hidden task work, except git, agent configuration, dependencies and this preparation directory.',
    'limitations': ['This is a metadata snapshot during parallel production, not visual approval.', 'Existing audit and exposure hashes are provenance records, not freshly verified hashes.', 'Rebuild the snapshot and validate latest manifests before editing images.'],
    'summary': {'visual_paths_found': len(records) + len(errors), 'readable_headers': len(records), 'header_errors': len(errors), 'families': dict(Counter(r['family'] for r in records)), 'roles': dict(Counter(r['role'] for r in records)), 'ui_contracts_attached': sum('ui_contract' in r for r in records), 'exposure_records_attached': sum('prior_exposure_record' in r for r in records), 'historical_audits_attached': sum('historical_audit' in r for r in records), 'changed_during_read': sum(not r['stable_during_header_read'] for r in records)},
    'records': records, 'errors': errors,
}
(OUT / 'inventory.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(snapshot['summary'], ensure_ascii=True))