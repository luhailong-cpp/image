"""Build a fresh byte-preserving 17 snapshot from explicitly selected imported frames."""
from pathlib import Path
import argparse, hashlib, json, re, shutil
import numpy as np
from PIL import Image, ImageDraw
from common import *

PREVIEW = RECOVERY / '17-delivery-preview'
EXPECTED = [*[f'walk/{d}/{n:02d}.png' for d in DIRS for n in range(1, 17)], *[f'idle/{d}.png' for d in DIRS]]
PENDING_STATES = {'pending', 'root_selected_unapproved', 'static_reviewed_pending_dynamic'}

def selection_rows(document):
    require(document.get('character_id', CHAR) == CHAR, 'Wrong character selections')
    selections = document.get('overrides', document.get('selections', {}))
    require(isinstance(selections, dict) and all(key in EXPECTED for key in selections), 'Invalid selected slots')
    rows = []
    pixel_hashes, mirrored_hashes, raw_cells = {}, {}, {}
    for key in EXPECTED:
        if key not in selections:
            continue
        selection = selections[key]
        if isinstance(selection, str):
            selection = read(Path(selection))
        elif selection.get('import_result'):
            selection = {**read(Path(selection['import_result'])), **selection}
        require(selection.get('slot', key) == key, 'Selected import-result belongs to another slot')
        require(selection.get('visual_status', 'pending') in PENDING_STATES, 'Do not select a rejected or formally approved attempt')
        source = Path(selection['path']).resolve()
        require(source.is_relative_to((HERE / 'staging').resolve()) and source.is_file(), 'Selected PNG must be inside 17 staging')
        require(sha(source) == selection['sha256'], 'Selected SHA mismatch: ' + key)
        record_path = Path(selection['source_record_file']).resolve()
        require(record_path.is_relative_to((HERE / 'staging').resolve()), 'Source record must stay in 17 staging')
        source_record = read(record_path)[key]
        origin = record_path.parent.parent
        raw_path = origin / source_record['source']['path']
        require(sha(raw_path) == source_record['source']['sha256'], 'Selected raw SHA mismatch')
        require(source_record['output_sha256'] == sha(source), 'Source record does not bind selected PNG')
        require(source_record['source']['grid'] == [1, 1] and min(source_record['source']['native_size']) >= 1024,
                'Every selected action needs a native complete single frame')
        anchor = source_record['anchor_after_px']
        require(source_record['common_scale'] == .88 and abs(anchor[0] - 512) <= .5 and anchor[1] == 942, 'Changed 17 geometry contract')
        cell_identity = (source_record['source']['sha256'], tuple(source_record['source']['cell_xyxy']))
        require(cell_identity not in raw_cells, 'Same source cell assigned to two actions: ' + key)
        raw_cells[cell_identity] = key
        with Image.open(source) as image:
            require(image.mode == 'RGBA' and image.format == 'PNG' and image.size == (1024, 1024), 'Need 1024 RGBA PNG')
            rgba = np.array(image)
            pixels = hashlib.sha256(rgba.tobytes()).hexdigest()
            mirror = hashlib.sha256(rgba[:, ::-1].tobytes()).hexdigest()
        require(pixels not in pixel_hashes, 'Exact duplicate action pixels: ' + key)
        require(pixels not in mirrored_hashes, 'Exact horizontally mirrored action: ' + key)
        pixel_hashes[pixels], mirrored_hashes[mirror] = key, key
        alpha = rgba[:, :, 3]
        require(alpha.min() == 0 and alpha.max() > 8, 'Missing real alpha background/body')
        require(not any(np.any(edge) for edge in (alpha[0], alpha[-1], alpha[:, 0], alpha[:, -1])), 'Export touches boundary')
        y, x = np.where(alpha > 8)
        height = int(y.max() - y.min() + 1)
        axis = float(np.median(x[y < int(y.min()) + max(1, int((height - 1) * .42))]))
        require(abs(axis - 512) <= .5 and int(y.max()) == 942, 'Selected anchor drift')
        generation_path = Path(selection.get('raw_generation_record', GEN / selection['selected_revision'] / 'raw.png.generation.json'))
        generation = read(generation_path)
        require(generation['sha256'] == source_record['source']['sha256'], 'Generation record raw mismatch')
        rows.append({'path': key, 'sha256': sha(source), 'size': [1024, 1024], 'source': str(source),
            'selected_revision': selection['selected_revision'], 'visual_status': selection.get('visual_status', 'pending'),
            'copied_byte_exact': True, 'source_record_file': str(record_path), 'source_record_file_sha256': sha(record_path),
            'source_record': source_record, 'native_source_size': source_record['source']['native_size'],
            'raw_generation_record': str(generation_path), 'raw_generation_record_sha256': sha(generation_path),
            'actualModel': generation.get('actualModel'), 'actualQuality': generation.get('actualQuality'),
            'anchor_native_px': [axis, int(y.max())], 'subject_height_native_px': height,
            'body_scale': float(np.sqrt(np.count_nonzero(alpha[:, 256:768]) / (1024 * 1024))),
            'pixel_sha256': pixels, 'review_note': selection.get('review_note', '')})
    return rows

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--selections', type=Path, required=True)
    parser.add_argument('--require-complete', action='store_true')
    args = parser.parse_args()
    require(re.fullmatch(r'[A-Za-z0-9_-]+', args.revision), 'Invalid fresh revision name')
    out = PREVIEW / 'revisions' / args.revision
    require(not out.exists(), 'Preserve existing snapshot; use a fresh revision')
    selections = read(args.selections)
    rows = selection_rows(selections)
    bykey = {row['path']: row for row in rows}
    missing = [key for key in EXPECTED if key not in bykey]
    require(not args.require_complete or not missing, 'Cannot build a complete package while slots are missing')
    out.mkdir(parents=True)
    (out / 'preview').mkdir()
    save_new(out / 'selection-input.json', selections)
    for row in rows:
        destination = out / 'runtime' / row['path']
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(row['source'], destination)
        require(sha(destination) == row['sha256'], 'Runtime copy changed bytes')
        save_new(destination.with_suffix('.png.generation.json'), {
            **image_identity(destination), 'schemaVersion': 1, 'recordedAt': now(), 'route': 'derived-no-generation',
            'operation': 'byte-exact copy of selected reviewed-candidate file; no image transformation',
            'derivedFrom': [{'path': row['source'], 'sha256': row['sha256'], 'generationRecord': row['source'] + '.generation.json'}],
            'originalGenerationRecord': row['raw_generation_record'], 'actualModel': row['actualModel'],
            'actualQuality': row['actualQuality'], 'generationCalls': 0, 'paidApiCalls': 0, 'visualApproval': False})
    gifs, directions, numeric_errors = [], {}, []
    for direction in DIRS:
        keys = [f'walk/{direction}/{n:02d}.png' for n in range(1, 17)]
        present = [key for key in keys if key in bykey]
        complete = len(present) == 16
        idle_key = f'idle/{direction}.png'
        scales = [bykey[key]['body_scale'] for key in present]
        heights = [bykey[key]['subject_height_native_px'] for key in present]
        cv = float(np.std(scales) / np.mean(scales)) if scales else None
        mean = float(np.mean(heights)) if heights else None
        drift = abs(bykey[idle_key]['subject_height_native_px'] / mean - 1) if mean and idle_key in bykey else None
        if cv is not None and cv > .08:
            numeric_errors.append(direction + ': body_scale_cv > .08')
        if drift is not None and drift > .08:
            numeric_errors.append(direction + ': idle_walk_height_drift > .08')
        directions[direction] = {'available_walk': len(present), 'complete_inventory': complete, 'idle_present': idle_key in bykey,
            'visual_approval': False, 'body_scale_cv': cv, 'subject_height_mean': mean, 'idle_walk_height_drift': drift}
        for mode, color in [('dark', (30, 38, 46)), ('light', (240, 238, 228))]:
            text = 'white' if mode == 'dark' else 'black'
            contact = Image.new('RGB', (2048, 2240), color)
            draw = ImageDraw.Draw(contact)
            displays = []
            for index, key in enumerate(keys):
                display = Image.new('RGB', (512, 512), color)
                if key in bykey:
                    with Image.open(out / 'runtime' / key) as image:
                        small = image.resize((512, 512), Image.Resampling.LANCZOS)
                        display.paste(small, (0, 0), small)
                else:
                    ImageDraw.Draw(display).text((120, 250), 'MISSING - NO SUBSTITUTE', fill=text)
                x, y = index % 4 * 512, index // 4 * 560
                contact.paste(display, (x, y + 32))
                draw.text((x + 10, y + 8), direction + f'{index + 1:02d}', fill=text)
                displays.append(display)
            contact.save(out / f'preview/{direction}-contact-{mode}.png')
            seam = Image.new('RGB', (2048, 570), color)
            sd = ImageDraw.Draw(seam)
            for col, index in enumerate((14, 15, 0, 1)):
                seam.paste(displays[index], (col * 512, 48))
                sd.text((col * 512 + 15, 15), direction + f'{index + 1:02d}', fill=text)
            seam.save(out / f'preview/{direction}-seam15-16-01-02-{mode}.png')
            if complete:
                gif = out / f'preview/{direction}-30ms-{mode}.gif'
                displays[0].save(gif, save_all=True, append_images=displays[1:], duration=[30] * 16, loop=0, optimize=False, disposal=2)
                with Image.open(gif) as check:
                    durations = []
                    for index in range(check.n_frames):
                        check.seek(index)
                        durations.append(check.info['duration'])
                    require(check.n_frames == 16 and durations == [30] * 16, 'GIF frame timing/count differs')
                gifs.append({'path': gif.relative_to(out).as_posix(), 'sha256': sha(gif), 'frames': 16, 'duration_ms': durations, 'cycle_ms': 480})
    means = [row['subject_height_mean'] for row in directions.values() if row['subject_height_mean']]
    if means and max(means) / min(means) > 1.1:
        numeric_errors.append('cross_direction_mean_height_ratio > 1.10')
    for mode, color in [('dark', (30, 38, 46)), ('light', (240, 238, 228))]:
        contact = Image.new('RGB', (2048, 1120), color)
        draw = ImageDraw.Draw(contact)
        for index, direction in enumerate(DIRS):
            key = f'idle/{direction}.png'
            x, y = index % 4 * 512, index // 4 * 560
            draw.text((x + 10, y + 8), direction + ' idle', fill='white' if mode == 'dark' else 'black')
            if key in bykey:
                with Image.open(out / 'runtime' / key) as image:
                    small = image.resize((512, 512), Image.Resampling.LANCZOS)
                    contact.paste(small, (x, y + 32), small)
        contact.save(out / f'preview/idle-contact-{mode}.png')
    manifest = {'schema': 'qdao-17-isolated-review-v1', 'created_at_utc': now(), 'revision': args.revision, 'character_id': CHAR,
        'status': 'inventory_complete_visual_pending' if not missing else 'inventory_incomplete_visual_pending',
        'target_walk': 128, 'target_idle': 8, 'actual_walk': sum(r['path'].startswith('walk/') for r in rows),
        'actual_idle': sum(r['path'].startswith('idle/') for r in rows), 'missing': missing, 'directions': directions,
        'frame_duration_ms': 30, 'cycle_duration_ms': 480, 'files': rows, 'gif_checks': gifs, 'numeric_errors': numeric_errors,
        'source_png_bytes_unchanged': True, 'all_actions_native_single_frame': True, 'no_exact_duplicates_or_horizontal_mirrors': True,
        'preview_only_downsample': True, 'formal_approval': False, 'client_integration': False,
        'browser_dynamic_review': {'performed': False, 'reason': 'Package creation is not visual or browser playback acceptance.'},
        'selection_input_sha256': sha(out / 'selection-input.json')}
    save_new(out / 'manifest.json', manifest)
    compact = {**manifest, 'files': [{k: v for k, v in row.items() if k != 'source_record'} for row in rows]}
    template = (HERE / 'preview-template.html').read_text(encoding='utf-8')
    with (out / 'index.html').open('x', encoding='utf-8') as handle:
        handle.write(template.replace('__MANIFEST__', json.dumps(compact, ensure_ascii=False)))
    save_new(out / 'audit.json', {'manifest_sha256': sha(out / 'manifest.json'), 'runtime_png_count': len(rows),
        'gif_count': len(gifs), 'numeric_errors': numeric_errors, 'visual_review': 'pending', 'client_integration': False})
    print(json.dumps({'snapshot': str(out), 'manifest_sha256': sha(out / 'manifest.json'), 'walk': manifest['actual_walk'],
        'idle': manifest['actual_idle'], 'missing_count': len(missing), 'gif_count': len(gifs), 'numeric_errors': numeric_errors,
        'visual_review': 'pending'}, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
