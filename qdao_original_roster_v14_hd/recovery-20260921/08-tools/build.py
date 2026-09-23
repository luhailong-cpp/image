"""Build an immutable 08 offline review snapshot; never grants visual approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, re, shutil
from PIL import Image, ImageDraw
from process import GEN, OUT, RECOVERY, DIRS, read, write, sha

DELIVERY = RECOVERY / '08-delivery-preview'
HERE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--selection', type=Path, help='Optional JSON object mapping idle/D or walk/D/01 to exact attempt')
    parser.add_argument('--directions', default=','.join(DIRS), help='Comma-separated directions for an explicitly partial review snapshot')
    args = parser.parse_args()
    requested_directions = args.directions.split(',')
    if not set(requested_directions).issubset(DIRS):
        raise ValueError('Unknown direction')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.revision):
        raise ValueError('Unsafe revision name')
    selected = read(args.selection) if args.selection else {}
    byslot, exclusions = {}, []
    for meta in sorted(OUT.glob('*/source.json')):
        row = read(meta); attempt = row['attempt']; review_path = GEN / attempt / 'review.json'
        if row['slot'].split('/')[1] not in requested_directions:
            continue
        review = read(review_path) if review_path.is_file() else {'status': 'unreviewed'}
        if review.get('status') == 'rejected':
            exclusions.append({'attempt': attempt, 'review': review, 'review_sha256': sha(review_path)})
            continue
        if sha(row['raw']['file']) != row['raw']['sha256'] or sha(row['request']['file']) != row['request']['sha256']:
            raise ValueError('Changed generation input: ' + attempt)
        if sha(meta.parent / 'frame.png') != row['output_sha256']:
            raise ValueError('Changed processed frame: ' + attempt)
        slot = row['slot']; byslot.setdefault(slot, []).append((row, meta, review, review_path))
    chosen = []
    for slot, entries in byslot.items():
        if slot in selected:
            matches = [v for v in entries if v[0]['attempt'] == selected[slot]]
            if len(matches) != 1:
                raise ValueError('Selection not available/non-rejected: ' + slot)
            chosen.append(matches[0])
        elif len(entries) == 1:
            chosen.append(entries[0])
        else:
            raise ValueError('Multiple non-rejected attempts; specify --selection: ' + slot)
    unknown = set(selected) - set(byslot)
    if unknown:
        raise ValueError('Selection has unavailable slots: ' + ','.join(sorted(unknown)))
    raw_hashes = [v[0]['raw']['sha256'] for v in chosen]
    output_hashes = [v[0]['output_sha256'] for v in chosen]
    if len(raw_hashes) != len(set(raw_hashes)) or len(output_hashes) != len(set(output_hashes)):
        raise ValueError('One source/output has been assigned to multiple slots')
    dest = DELIVERY / 'revisions' / args.revision
    if dest.exists():
        raise ValueError('Revision exists; preserve it and choose a new name')
    dest.mkdir(parents=True)
    expected = [f'walk/{d}/{f:02d}' for d in DIRS for f in range(1, 17)] + [f'idle/{d}' for d in DIRS]
    files = []
    for row, meta, review, review_path in chosen:
        slot, attempt = row['slot'], row['attempt']; relative = 'runtime/' + slot + '.png'
        target = dest / relative; target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(meta.parent / 'frame.png', target)
        evidence = dest / 'evidence' / attempt; evidence.mkdir(parents=True)
        for name in ('source.json', 'raw.png.generation.json', 'frame.png.generation.json'):
            shutil.copy2(meta.parent / name, evidence / name)
        if review_path.is_file():
            shutil.copy2(review_path, evidence / 'review.json')
        for name in ('raw.png', 'prompt.txt', 'request.json', 'receipt.json'):
            # Raw is referenced by exact SHA, not duplicated per derived snapshot.
            if name != 'raw.png': shutil.copy2(GEN / attempt / name, evidence / name)
        files.append({'slot': slot, 'path': relative, 'sha256': sha(target), 'size': [1024, 1024],
          'source_attempt': attempt, 'raw': row['raw'], 'source_record': str((evidence / 'source.json').relative_to(dest)),
          'source_record_sha256': sha(evidence / 'source.json'), 'anchor_px': row['anchor_px'], 'bbox_px': row['bbox_px'],
          'source_review': review, 'visual_review': 'pending'})
    present = {v['slot']: v for v in files}; missing = [v for v in expected if v not in present]
    gifs, contact_sheets = [], []
    preview = dest / 'preview'; preview.mkdir()
    for direction in DIRS:
        for theme, color in [('light', (240, 238, 228)), ('dark', (30, 38, 46))]:
            sheet = Image.new('RGB', (2048, 2176), color); draw = ImageDraw.Draw(sheet)
            displays = []
            feet = Image.new('RGB', (2048, 1200), color); feet_draw = ImageDraw.Draw(feet)
            seam = Image.new('RGB', (2048, 544), color); seam_draw = ImageDraw.Draw(seam)
            for frame in range(1, 17):
                slot = f'walk/{direction}/{frame:02d}'; row = present.get(slot)
                x, y = ((frame-1) % 4) * 512, ((frame-1) // 4) * 544
                label = f'{direction} {frame:02d}' + ('' if row else ' MISSING')
                draw.text((x+12, y+8), label, fill='white' if theme == 'dark' else 'black')
                if row:
                    original = Image.open(dest / row['path']).convert('RGBA')
                    image = original.resize((512, 512), Image.Resampling.LANCZOS)
                    display = Image.new('RGB', (512, 512), color); display.paste(image, (0, 0), image)
                    displays.append(display); sheet.paste(display, (x, y+32))
                    crop = original.crop((256, 724, 768, 1024))
                    fx, fy = ((frame-1) % 4) * 512, ((frame-1) // 4) * 300
                    feet.paste(crop, (fx, fy), crop)
                    feet_draw.text((fx+8, fy+8), label, fill='white' if theme == 'dark' else 'black')
                    if frame in (15, 16, 1, 2):
                        sx = (15, 16, 1, 2).index(frame) * 512
                        seam.paste(display, (sx, 32))
                        seam_draw.text((sx+12, 8), label, fill='white' if theme == 'dark' else 'black')
            path = preview / f'{direction}-contact-{theme}.jpg'; sheet.save(path, quality=92)
            contact_sheets.append({'path': path.relative_to(dest).as_posix(), 'sha256': sha(path), 'preview_only_downsample': True})
            if len(displays) == 16:
                for kind, composite in [('feet-1to1', feet), ('seam', seam)]:
                    composite_path = preview / f'{direction}-{kind}-{theme}.jpg'
                    composite.save(composite_path, quality=96)
                    contact_sheets.append({'path': composite_path.relative_to(dest).as_posix(), 'sha256': sha(composite_path), 'review_composite_only': True})
                path = preview / f'{direction}-30ms-{theme}.gif'
                displays[0].save(path, save_all=True, append_images=displays[1:], duration=[30]*16, loop=0, optimize=False, disposal=2)
                with Image.open(path) as gif:
                    durations = []
                    for i in range(gif.n_frames): gif.seek(i); durations.append(gif.info.get('duration'))
                if durations != [30]*16:
                    raise ValueError('GIF did not retain all sixteen 30ms frames: ' + str(path))
                gifs.append({'path': path.relative_to(dest).as_posix(), 'sha256': sha(path), 'frames': 16, 'durations_ms': durations, 'cycle_ms': 480, 'preview_only_downsample': True})
    manifest = {'schema': 'qdao-08-offline-review-v1', 'character_id': '08_alchemy_prodigy_boy', 'revision': args.revision,
      'createdAt': datetime.now(timezone.utc).isoformat(), 'directions': list(DIRS), 'frame_duration_ms': 30, 'cycle_duration_ms': 480,
      'actual_walk': sum(v['slot'].startswith('walk/') for v in files), 'actual_idle': sum(v['slot'].startswith('idle/') for v in files),
      'missing': missing, 'files': files, 'rejected_attempts': exclusions, 'gifs': gifs, 'contact_sheets': contact_sheets,
      'status': 'inventory_complete_visual_pending' if not missing else 'inventory_incomplete_visual_pending',
      'visual_approval': False, 'browser_review_performed': False, 'unity_validation': False, 'formal_client_validation': False,
      'no_reused_source_sha': True, 'no_pose_interpolation': True, 'common_whole_cell_scale': .88,
      'scripts': [{'file': str(HERE / name), 'sha256': sha(HERE / name)} for name in ('process.py', 'build.py', 'preview.html')]}
    write(dest / 'manifest.json', manifest)
    template = (HERE / 'preview.html').read_text(encoding='utf-8')
    (dest / 'index.html').write_text(template.replace('__MANIFEST__', json.dumps(manifest, ensure_ascii=False).replace('</', '<\\/')), encoding='utf-8')
    (DELIVERY / 'index.html').write_text(f'<!doctype html><meta charset="utf-8"><title>08 炼丹童子</title><h1>08 炼丹童子</h1><p>{manifest["actual_walk"]}/128 行走；{manifest["actual_idle"]}/8 站立。离线美术审阅待完成。</p><a href="revisions/{args.revision}/index.html">打开 {args.revision} 30毫秒/帧预览</a>', encoding='utf-8')
    print(json.dumps({'revision': str(dest), 'walk': manifest['actual_walk'], 'idle': manifest['actual_idle'], 'missing': len(missing), 'gifs': len(gifs), 'visual_approval': False}, ensure_ascii=False))

if __name__ == '__main__': main()
