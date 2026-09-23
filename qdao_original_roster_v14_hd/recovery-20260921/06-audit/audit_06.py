"""Read real 06 evidence and reconstruct pending raw frames into an isolated audit only."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util, json, hashlib, shutil
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CHAR = '06_thunder_caster_boy'
SOURCE = ROOT / 'generation' / CHAR
LIVE = ROOT / 'candidate' / CHAR
AUDIT = HERE / 'candidate' / CHAR

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def fingerprint(path):
    return {p.relative_to(path).as_posix(): sha(p) for p in sorted(path.rglob('*')) if p.is_file()}

def main():
    before = fingerprint(LIVE)
    source_before = fingerprint(SOURCE)
    tools_before = fingerprint(ROOT / 'tools')
    inspector = module('audit06_provenance', ROOT / 'tools/inspect_image_provenance.py')
    paused = {r['batch']: r for r in read(SOURCE / 'inventory-at-pause-20260919.json')['batches']}
    inventory = []
    for batch, old in paused.items():
        folder = SOURCE / batch
        info = inspector.inspect_image(folder / 'raw.png')
        provenance = read(folder / 'provenance.json')
        receipt = read(folder / 'generation-receipt.json')
        prompt = (folder / 'prompt.txt').read_text(encoding='utf-8-sig')
        exact_prompt = prompt.rstrip('\r\n') == receipt['request']['prompt'].rstrip('\r\n')
        mapped = []
        for original in receipt['request'].get('referenced_image_paths', []):
            normalized = original.replace('\\', '/')
            local = Path(normalized.replace('E:/work/image/', str(ROOT.parent).replace('\\', '/') + '/', 1))
            mapping_basis = 'verified_project_root_mapping'
            if not local.is_file():
                matches = [p.parent/'raw.png' for p in SOURCE.glob('*/generation-receipt.json') if normalized in read(p).get('actual_tool_output',{}).get('output_hint','').replace('\\','/')]
                if len(matches) == 1:
                    local = matches[0]
                    mapping_basis = 'exact_historical_tool_output_hint_to_archived_raw'
            mapped.append({'historical': original, 'local': str(local), 'exists': local.is_file(), 'sha256': sha(local) if local.is_file() else None, 'mapping_basis': mapping_basis})
        inventory.append({**info, 'batch': batch, 'sha_matches_paused_inventory': info['sha256'] == old['raw_sha256'], 'sha_matches_archived_provenance': info['sha256'] == provenance['sha256'], 'exact_prompt_matches_receipt': exact_prompt, 'receipt_sha256': sha(folder / 'generation-receipt.json'), 'prompt_sha256': sha(folder / 'prompt.txt'), 'actual_model': receipt.get('model_actual'), 'real_output_hint_retained': bool(receipt.get('actual_tool_output', {}).get('output_hint')), 'mapped_references': mapped, 'rejected': old['rejected']})
        assert info['sha256'] == old['raw_sha256'] == provenance['sha256']
        assert exact_prompt and info['native_size'] == [1254, 1254]
        assert all(row['exists'] for row in mapped)
    write(HERE / 'source-audit.json', {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'path_mapping': {'E:/work/image': str(ROOT.parent)}, 'images': inventory, 'signature_validation_performed': False})
    if not AUDIT.exists():
        shutil.copytree(LIVE, AUDIT)
    pipeline = module('audit06_pipeline', ROOT / 'tools/pipeline.py')
    pipeline.output = lambda character: AUDIT if character == CHAR else (_ for _ in ()).throw(ValueError('Character outside audit scope'))
    pipeline.preview = lambda: None
    for frame in (4, 6, 13):
        if (AUDIT / f'walk/E/{frame:02d}.png').exists():
            continue
        batch = f'E{frame:02d}-single-v1'
        folder = SOURCE / batch
        args = SimpleNamespace(command='import-walk', character=CHAR, direction='E', source=folder/'raw.png', prompt=folder/'prompt.txt', receipt=folder/'generation-receipt.json', batch_id=batch, common_scale=.88, chroma_profile='standard', rows=1, cols=1, source_cell_indices=None, idle_order=None, output_frames=str(frame), start_frame=1)
        pipeline.import_sheet(args)
    verifier = module('audit06_verifier', ROOT / 'tools/verify.py')
    original_mod = verifier.mod
    verifier.mod = lambda name: pipeline.KEYER if name == 'generate2dsprite' else pipeline.EDGE if name == 'edge_despill' else original_mod(name)
    verifier.ROOT = HERE
    reports = []
    for frame in (1, 2, 3, 4, 5, 6, 9, 13):
        try:
            result = verifier.verify(CHAR, 'E', False, frame)
        except Exception as exc:
            result = {'status':'failed', 'frame':frame, 'error':str(exc)}
        print(json.dumps(result), flush=True)
        write(HERE / f'validation-E-{frame:02d}.json', result)
        reports.append(result)
    frames = (1, 2, 3, 4, 5, 6, 9, 13)
    for label, bg in [('dark', (30, 33, 39)), ('light', (240, 235, 222))]:
        sheet = Image.new('RGB', (4 * 512, 2 * 560), bg)
        draw = ImageDraw.Draw(sheet)
        for slot, frame in enumerate(frames):
            im = Image.open(AUDIT / f'walk/E/{frame:02d}.png').convert('RGBA')
            im = im.resize((512, 512), Image.Resampling.LANCZOS)
            x, y = (slot % 4)*512, (slot // 4)*560
            sheet.paste(im, (x, y), im)
            draw.text((x+12, y+520), f'E {frame:02d}' + (' - isolated raw rebuild' if frame in (4,6,13) else ' - existing candidate'), fill=(255,255,255) if label == 'dark' else (20,20,20))
        sheet.save(HERE / f'E-available-{label}.png')
    e03 = Image.open(AUDIT / 'walk/E/03.png').convert('RGBA')
    closeup = Image.new('RGB', (1600, 800), (30,33,39))
    crop = e03.crop((250, 100, 750, 600)).resize((800,800), Image.Resampling.NEAREST)
    closeup.paste(crop, (0,0), crop)
    closeup.paste((240,235,222), (800,0,1600,800))
    closeup.paste(crop, (800,0), crop)
    closeup.save(HERE / 'E03-edge-closeup.png')
    evidence = read(AUDIT / 'processing/frame-sources.json')
    after = fingerprint(LIVE)
    assert before == after
    assert source_before == fingerprint(SOURCE)
    assert tools_before == fingerprint(ROOT / 'tools')
    write(HERE/'audit-summary.json', {'checked_at_utc': datetime.now(timezone.utc).isoformat(), 'character':CHAR, 'scope':'isolated audit; no live candidate, generation, shared pipeline or client edits', 'source_raw_count':len(inventory), 'reconstructed_frames':[1,2,3,4,5,6,9,13], 'newly_reconstructed_pending_raw_frames':[4,6,13], 'native_cell_min_px':1254, 'whole_cell_scale':1024/1254*.88, 'output_size':[1024,1024], 'anchor_px':[512,942], 'all_rebuilds_pixel_equal':all(r['status']=='partial_sources_pending_visual' for r in reports), 'live_candidate_unchanged': before==after, 'live_candidate_before':before, 'live_candidate_after':after, 'visual_review':'pending; E03 color fringe confirmed; incomplete direction', 'raw_rebuilds':{f'E{frame:02d}':evidence[f'walk/E/{frame:02d}.png'] for frame in (4,6,13)}, 'missing_even_after_pending_import':[7,8,10,11,12,14,15,16], 'full_30ms_loop_review_possible':False, 'reason':'8 E slots still have no raw; this audit never substitutes copies, mirrors or interpolation.'})
    print(json.dumps({'status':'isolated_audit_complete', 'raw':len(inventory), 'reconstructed':8, 'live_unchanged':True, 'output':str(HERE)}, ensure_ascii=False))

if __name__ == '__main__':
    main()
