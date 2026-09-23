"""Package already reviewed character 17 assets; never grants visual approval itself."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw
from common import CHAR, DIRS, RECOVERY, read, require, sha, save_new, now


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--snapshot', type=Path, required=True)
    p.add_argument('--acceptance', type=Path, required=True)
    args = p.parse_args()
    out = args.snapshot.resolve()
    require(out.is_relative_to((RECOVERY / '17-delivery-preview/revisions').resolve()), 'Only character17 snapshots')
    manifest = read(out / 'manifest.json')
    review = read(args.acceptance)
    require(manifest['character_id'] == CHAR and review['character_id'] == CHAR, 'Wrong character')
    require(review['manifest_sha256'] == sha(out / 'manifest.json'), 'Review belongs to different bytes')
    require(review['offline_visual_approval'] is True, 'Manual final visual review is required')
    require(manifest['actual_walk'] == 128 and manifest['actual_idle'] == 8 and not manifest['missing'], 'Incomplete')
    require(not manifest['numeric_errors'], 'Numeric concerns unresolved')
    require((out / 'runtime-audit.json').exists() and (out / 'source-evidence.json').exists(), 'Missing audit/evidence')
    audit = read(out / 'runtime-audit.json')
    require(audit['manifest_sha256'] == review['manifest_sha256'] and audit['complete_inventory'], 'Wrong runtime audit')
    require(set(review['directions']) == set(DIRS), 'Need all direction decisions')
    require(all(v['accepted'] is True for v in review['directions'].values()), 'A direction is not accepted')
    for row in manifest['files']:
        require(sha(out / 'runtime' / row['path']) == row['sha256'], 'Runtime changed after review')
    summaries = []
    for mode, color in [('dark', (30, 38, 46)), ('light', (240, 238, 228))]:
        frames = []
        for n in range(1, 17):
            frame = Image.new('RGB', (1024, 568), color)
            draw = ImageDraw.Draw(frame)
            for i, direction in enumerate(DIRS):
                x, y = i % 4 * 256, i // 4 * 284
                draw.text((x + 12, y + 6), f'{direction} / {n:02d} / 30ms', fill='white' if mode == 'dark' else 'black')
                with Image.open(out / f'runtime/walk/{direction}/{n:02d}.png') as im:
                    small = im.resize((256, 256), Image.Resampling.LANCZOS)
                    frame.paste(small, (x, y + 24), small)
            frames.append(frame)
        path = out / f'preview/eight-directions-30ms-{mode}.gif'
        require(not path.exists(), 'Do not overwrite an existing final preview')
        frames[0].save(path, save_all=True, append_images=frames[1:], duration=[30] * 16, loop=0, optimize=False, disposal=2)
        with Image.open(path) as im:
            durations = []
            for i in range(im.n_frames):
                im.seek(i)
                durations.append(im.info['duration'])
        require(durations == [30] * 16, 'Overview GIF timing changed')
        summaries.append({'path': path.relative_to(out).as_posix(), 'sha256': sha(path), 'frames': 16, 'duration_ms': durations, 'cycle_ms': 480})
    save_new(out / 'acceptance.json', review)
    save_new(out / 'delivery.json', {
        'character_id': CHAR, 'recorded_at': now(), 'status': 'asset_and_offline_preview_accepted',
        'walk_count': 128, 'independent_idle_count': 8, 'final_size': [1024, 1024], 'format': 'RGBA PNG',
        'manifest_sha256': sha(out / 'manifest.json'), 'source_evidence_sha256': sha(out / 'source-evidence.json'),
        'acceptance_sha256': sha(out / 'acceptance.json'), 'runtime_audit_sha256': sha(out / 'runtime-audit.json'),
        'all_directions_accepted': True, 'client_integration': False, 'overview_gifs': summaries,
        'historical_snapshot_manifest_preserved': True,
        'note': 'Creation-time pending flags remain historical. acceptance.json grants the later offline decision for these exact hashes.'
    })
    index = out / 'index.html'
    original = index.read_text(encoding='utf-8')
    index.write_text(original.replace('</html>', '''<script>
document.getElementById('summary').className='';
document.getElementById('summary').textContent='17 灵篆书生 · 128/128 行走 + 8/8 独立站立 · 素材与离线预览验收通过 · 客户端未接入';
for(const row of Object.values(rows)) row.visual_status='离线验收通过';
draw();
</script><p><a href="acceptance.json">最终离线验收</a> · <a href="delivery.json">交付清单</a> · <a href="source-evidence.json">逐图来源证据</a> · <a href="preview/eight-directions-30ms-dark.gif">八方向循环总览</a></p></html>'''), encoding='utf-8')
    launcher = RECOVERY / '17-delivery-preview/index.html'
    require(not launcher.exists(), 'Do not overwrite an existing launcher')
    launcher.write_text(f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>17 灵篆书生成品</title><meta http-equiv="refresh" content="0;url=revisions/{out.name}/index.html"><p><a href="revisions/{out.name}/index.html">打开17灵篆书生八方向成品与预览</a></p></html>''', encoding='utf-8')
    print(json.dumps({'snapshot': str(out), 'delivery_sha256': sha(out / 'delivery.json'), 'overview_count': 2, 'accepted': True, 'client_integration': False}, ensure_ascii=False))


if __name__ == '__main__':
    main()
