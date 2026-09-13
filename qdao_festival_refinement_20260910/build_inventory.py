"""Inventory image headers and delivery metadata; write only this task's inventory.json."""
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
    if p.startswith('tianyong_'): return 'world_map'
    if p.startswith('qdao_festival_scenes_20260910/'): return 'scene_illustrations'
    if p.startswith(('character_move_8dir/', 'qdao_chibi_roster_v11/')): return 'character_movement'
    if p.startswith(('q_daoist_character_pack_4096/', 'qdao_character_diversity_v9/')) or ('/' not in p and ('character' in p or 'hero' in p)): return 'characters'
    if p.startswith(('qdao_chibi_pets_v1/', 'qdao_ui_redesign_v5/pet/', 'qdao_asset_refresh_v6/pets/')): return 'pets'
    if p.startswith('qdao_asset_refresh_v6/icons/') or any(x in p for x in ('qstyle_redrawn_600x600', 'character_artifacts_redrawn_24_600x600', 'west_eight_immortals_redrawn_100_600x600')): return 'items_and_atlases'
    if p.startswith('client_ui_refresh_20260908/'): return 'client_exports'
    if p.startswith(('designs/attribute-panels/', 'designs/gameplay-ui/')): return 'attributes_and_new_pages'
    if p.startswith(('designs/', 'exact_qdao_slices/', 'qdao_ui_style_recut_v10/', 'qdao_gpt_image2_refresh_v7/ui/', 'q_daoist_login_ui_')) or any(x in p for x in ('/components/', '/hud/')): return 'ui_and_legacy_slices'
    if p.startswith(('qdao_ui_redesign_v5/', 'qdao_chibi_game_pack_v4/')) or '/' not in p: return 'scene_illustrations'
    return 'other_review'

def fallback_role(path):
    p = path.lower()
    parts = p.split('/')
    if p in ('qdao_battle_dim_overlay_2560x1080_v1.png', 'client_ui_refresh_20260908/prepared/ui/ugui/battle/overlays/qdao_battle_dim_overlay_2560x1080_v1.png'):
        return 'functional_uniform_alpha_overlay_preserve'
    if any(x in parts for x in ('.work', 'backups', 'staged', 'samples', 'contacts', 'thumbs', '__pycache__', 'rejected', 'history')) or p.startswith(('docs/style-audit-', 'qdao_exposure_refinement_v8/review/rebuilt/', 'qdao_chibi_roster_v11/24_crane_hermit/')):
        return 'supporting_history_or_work'
    if p.startswith('designs/attribute-panels/v10-preview/') or '/qa/' in p or 'screenshot' in p or '/processing/' in p or any(x in Path(p).stem for x in ('contact', 'visual-review', 'gif-decoded', 'before_after', 'layout-review', 'overlay')):
        return 'evidence_do_not_repaint'
    if p.startswith('docs/references/') or 'reference' in Path(p).name: return 'reference_do_not_repaint'
    if p.startswith(('tianyong_festival_gptimage2_20260910/', 'tianyong_festival_stylematch_20260910/')): return 'new_design_preview'
    if p.startswith('tianyong_festival_hd_20260910/'): return 'supporting_history_or_work'
    if '/source/' in p or '/sources/' in p: return 'source_review_pending'
    return 'asset_review_pending'

def build_delivery_index():
    index, documents, issues = {}, [], []
    def document(path):
        documents.append({'path': path, 'present': (ROOT / path).is_file()})
        return read_json(path)
    def register(path, base, asset_role, authority, declared_hash=None, source=None, note=None):
        if not isinstance(path, str) or Path(path).suffix.lower() not in VISUAL: return
        candidate = Path(path)
        candidate = candidate if candidate.is_absolute() else ROOT / base / candidate
        try: rel = candidate.resolve().relative_to(ROOT).as_posix()
        except ValueError: return  # External generation caches are not repository assets.
        item = index.setdefault(rel, {'role': asset_role, 'authorities': []})
        if authority not in item['authorities']: item['authorities'].append(authority)
        if declared_hash: item.setdefault('declared_hashes', {})[authority] = declared_hash
        if source: item['source_path'] = source
        if note: item['note'] = note
        if not candidate.is_file(): issues.append({'path': rel, 'authority': authority, 'issue': 'declared_current_visual_missing'})

    doc = 'tianyong_festival_hd_20260910/manifest.json'
    data = document(doc); base = str(Path(doc).parent)
    for e in data.get('refinements', []): register(e.get('file'), base, 'accepted_source_art', doc, e.get('nativeSha256'))
    for e in [data.get('master', {}), data.get('preview', {}), *data.get('tiles', [])]:
        register(e.get('file'), base, 'accepted_derived_export', doc, e.get('sha256'), note='Rebuild from native refined patches; preserve seams and tile coordinates.')

    doc = 'qdao_festival_scenes_20260910/manifest.json'
    data = document(doc); base = str(Path(doc).parent)
    for e in data.get('outputs', []):
        source = (Path(base) / e['nativeSource']).as_posix()
        register(e['nativeSource'], base, 'accepted_source_art', doc)
        register(e['file'], base, 'accepted_derived_export', doc, e.get('sha256'), source=source)

    doc = 'qdao_festival_scenes_20260910/runtime/runtime-manifest.json'
    data = document(doc)
    for e in data.get('outputs', []):
        register(e['runtimeFile'], 'qdao_festival_scenes_20260910/runtime', 'accepted_derived_export', doc, e.get('runtimeSha256'), source='qdao_festival_scenes_20260910/' + e['source'], note='2560x1080 runtime adaptation; preserve source crop and uniform resampling. Engine validation remains separate.')

    doc = 'qdao_chibi_roster_v11/manifest.json'
    data = document(doc)
    for overview in ('roster-overview.jpg', 'movement-overview.gif'):
        register(overview, 'qdao_chibi_roster_v11', 'accepted_preview_derivative', doc, note='Regenerate overview from current accepted character outputs.')
    roster = [e['slug'] for e in data.get('characters', [])]
    for slug in roster:
        base = 'qdao_chibi_roster_v11/' + slug; authority = base + '/manifest.json'
        manifest = document(authority)
        for e in manifest.get('files', []): register(e['path'], base, 'accepted_derived_export', authority, e.get('sha256'))
        for e in manifest.get('directional_original_sources', {}).values():
            if isinstance(e, dict): register(e.get('file') or e.get('path'), base, 'accepted_source_art', authority, e.get('sha256'))
        for key, e in manifest.get('sources', {}).items():
            if isinstance(e, dict):
                assembled = key in ('cardinal', 'diagonal') or e.get('assembled', False) or 'deterministic layout' in e.get('source', '')
                register(e.get('path') or e.get('file'), base, 'accepted_processing_input' if assembled else 'accepted_source_art', authority, e.get('sha256'), note='Assembled direction inputs are layouts, not native generated paintings.' if assembled else None)
                for original in e.get('generation_lineage', {}).get('raw_artifacts', []):
                    register(original.get('path'), base, 'accepted_source_art', authority, original.get('sha256'), note='Only accepted cells recorded in generation_lineage feed the direction assembly; preserve the unused cells as history.')

    doc = 'qdao_character_diversity_v9/manifest.json'
    data = document(doc)
    for e in data.get('assets', []):
        register(e['path'], data.get('asset_root', 'q_daoist_character_pack_4096'), 'accepted_source_art', doc, e.get('sha256'), note='4096 compatibility source; native resolution is recorded separately.')
    doc = 'qdao_character_diversity_v9/prepared_sync.json'
    for e in document(doc).get('records', []): register(e['output'], '', 'accepted_derived_export', doc, e.get('output_sha256'), source=e.get('source'))

    publication_doc = 'qdao_ui_style_recut_v10/publication.json'
    publication = {e['path']: e for e in document(publication_doc).get('files', [])}
    doc = 'qdao_ui_style_recut_v10/contracts/current_files.json'
    for e in document(doc).get('files', []):
        register(e['path'], '', 'accepted_derived_export', publication_doc, publication.get(e['path'], {}).get('published_sha256'), note='Keep current UI PNG contracts and paired SVG/atlas dependencies.')

    doc = 'designs/attribute-panels/v10-preview/asset-manifest.json'
    data = document(doc); base = str(Path(doc).parent)
    for e in data.get('assets', []):
        register(e['file'], base, 'accepted_preview_derivative', doc, e.get('sha256'), source=e.get('source'), note='Copy from formal sprite source, then rerender browser evidence.')
    doc = 'designs/gameplay-ui/manifest.json'
    for e in document(doc).get('records', []): register(e['path'], str(Path(doc).parent), 'accepted_source_art', doc, e.get('sha256'))
    audit_doc = 'qdao_festival_refinement_20260910/decision-classification-audit.json'
    for e in read_json(audit_doc).get('corrections', []):
        role = {'retain_source_record':'accepted_source_art', 'retain_derived':'accepted_processing_input', 'retain_current_preview_evidence':'current_preview_evidence', 'retain_current_evidence':'current_acceptance_evidence'}.get(e['decision'])
        if role: register(e['path'], '', role, audit_doc, e.get('sha256'), note=e['reason'])
    return index, documents, issues, roster

def main():
    index, documents, mapping_issues, roster = build_delivery_index()
    exposure = {r['path']: r for r in read_json('qdao_exposure_refinement_v8/processing.json').get('records', [])}
    audit = {r['path']: r for r in read_json('docs/style-audit-20260909/results.json').get('records', [])}
    contracts = {r['path']: r for r in read_json('qdao_ui_style_recut_v10/contracts/current_files.json').get('files', [])}
    cleanup_doc = 'docs/STORAGE_DUPLICATES_20260912.json'
    aliases = [{'removed_path': e['path'], 'keep_path': e['keep_path'], 'bytes': e.get('bytes'), 'sha256': e.get('sha256'), 'status': e.get('status')} for e in read_json(cleanup_doc).get('files', [])]
    cmd = ['rg', '--files', '--hidden', '-g', '!.git/**', '-g', '!node_modules/**', '-g', '!**/node_modules/**', '-g', '!.agents/**', '-g', '!.codex/**', '-g', '!qdao_festival_refinement_20260910/**']
    listed = subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, encoding='utf-8').stdout.splitlines()
    records, errors = [], []
    for rel in sorted({p.replace('\\', '/') for p in listed if Path(p).suffix.lower() in VISUAL}):
        f = ROOT / rel
        try:
            stat = f.stat(); mapping = index.get(rel)
            r = {'path': rel, 'family': family(rel), 'role': mapping['role'] if mapping else fallback_role(rel), 'bytes': stat.st_size, 'mtime_ns': stat.st_mtime_ns, 'review_status': 'not_visually_reviewed_in_this_pass', 'edit_status': 'not_started'}
            if mapping: r['accepted_delivery'] = {**mapping, 'current_hash_reverified': False, 'approval_scope': 'Producer delivery provenance; this inventory does not perform visual approval.'}
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
            elif r['role'] in ('accepted_derived_export', 'accepted_preview_derivative', 'accepted_processing_input'):
                r['planned_action'] = 'review_source_family_then_rebuild_dependencies_if_source_changes'
            else:
                r['planned_action'] = 'review_current_art_against_daoist_chibi_festival_direction'
            records.append(r)
        except Exception as exc: errors.append({'path': rel, 'error': str(exc)})
    snapshot = {
        'schema_version': 2, 'captured_at_utc': datetime.now(timezone.utc).isoformat(), 'root': ROOT.as_posix(),
        'stage': 'metadata_inventory_after_prerequisite_acceptance', 'images_modified': 0, 'completion_claim': False,
        'scope': 'All rg-visible visual files including visible hidden work, excluding git, agent configuration, dependencies and this task directory.',
        'limitations': ['Metadata inventory only, not visual refinement or approval.', 'Declared delivery, audit and exposure hashes are provenance, not freshly verified hashes.', 'Rebuild derivatives after source changes; do not repaint assembled inputs or browser evidence independently.'],
        'summary': {'visual_paths_found': len(records) + len(errors), 'readable_headers': len(records), 'header_errors': len(errors),
                    'families': dict(Counter(r['family'] for r in records)), 'roles': dict(Counter(r['role'] for r in records)),
                    'accepted_delivery_paths': sum('accepted_delivery' in r for r in records), 'mapping_issues': len(mapping_issues),
                    'ui_contracts_attached': sum('ui_contract' in r for r in records), 'exposure_records_attached': sum('prior_exposure_record' in r for r in records),
                    'historical_audits_attached': sum('historical_audit' in r for r in records), 'changed_during_read': sum(not r['stable_during_header_read'] for r in records)},
        'current_roster': roster, 'delivery_documents': documents, 'mapping_issues': mapping_issues,
        'deleted_duplicate_aliases': {'source': cleanup_doc, 'count': len(aliases), 'unique_keep_paths': len({e['keep_path'] for e in aliases}), 'records': aliases, 'hashes_reverified_by_this_script': False},
        'records': records, 'errors': errors,
    }
    # Sole write boundary: never save an image, other delivery file, or monitor-state.
    (OUT / 'inventory.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(snapshot['summary'], ensure_ascii=True))

if __name__ == '__main__':
    main()
