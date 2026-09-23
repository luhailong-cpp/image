"""Build a byte-preserving, explicitly pending review snapshot for character 05.

Example:
  py -3 build_preview.py --revision ne-repair-v1 --selections selected-overrides.json
  py -3 build_preview.py --inspect-only

Selections use the 04 package interface: {"overrides": {"walk/NE/03.png":
{"path": "repo-relative/or/absolute.png", "sha256": "...",
"selected_revision": "NE03-v1", "visual_status": "pending"}}}.
V13 action slots cannot be overridden. Missing slots stay missing. No source image
is transformed or overwritten; resizing happens only in generated review images.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
import shutil
import sys

sys.dont_write_bytecode = True
import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
V14_ROOT = HERE.parents[1]
ROOT = V14_ROOT.parent
RECOVERY = V14_ROOT / 'recovery-20260921'
CHAR = '05_celestial_musician_girl'
DIRS = ('N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW')
OLD = ROOT / 'qdao_original_roster_v13/candidate' / CHAR
NEW = V14_ROOT / 'candidate' / CHAR
EXPECTED = [*[f'walk/{d}/{n:02d}.png' for d in DIRS for n in range(1, 17)],
            *[f'idle/{d}.png' for d in DIRS]]
PENDING_STATES = {'pending', 'root_selected_unapproved',
                  'static_reviewed_pending_dynamic', 'preserved_existing_not_reapproved'}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def resolve(path):
    p = Path(path)
    return (p if p.is_absolute() else ROOT / p).resolve()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def record_origin(source, selection):
    explicit = selection.get('source_record_file') if selection else None
    if explicit:
        records_file = resolve(explicit)
        require(records_file.is_relative_to(ROOT), 'Source record must be in this workspace')
        require(records_file.is_file(), f'Missing explicitly selected source record: {records_file}')
        return records_file
    origin = next((p for p in source.parents if p.name == CHAR), None)
    records_file = origin / 'processing/frame-sources.json' if origin else None
    return records_file if records_file and records_file.is_file() else None


def inventory(selections):
    require(selections.get('character_id', CHAR) == CHAR, 'Wrong character selection')
    overrides = selections.get('overrides', {})
    require(isinstance(overrides, dict), 'overrides must be a keyed object')
    require(all(k in EXPECTED and k.startswith('walk/') for k in overrides), 'Invalid override slot')
    old_keys = [k for k in EXPECTED if (OLD / k).is_file()]
    require(sum(k.startswith('walk/') for k in old_keys) == 52 and
            sum(k.startswith('idle/') for k in old_keys) == 8,
            'V13 inventory differs from the expected preserved 52 walk + 8 idle; investigate before building')
    rows, missing = [], []
    for key in EXPECTED:
        old, new, selection = OLD / key, NEW / key, overrides.get(key)
        if old.is_file():
            require(selection is None, f'Preserved V13 action override forbidden: {key}')
            source, revision, visual = old, 'preserved-v13', 'preserved_existing_not_reapproved'
        elif selection is not None:
            require(isinstance(selection, dict), f'Override must be an object: {key}')
            require(key.split('/')[1] in ('NE', 'SE', 'SW', 'W', 'NW'), f'Unexpected repair direction: {key}')
            source = resolve(selection['path'])
            require(source.is_relative_to(RECOVERY.resolve()), f'New selection must be inside recovery: {key}')
            require(CHAR in source.parts, f'Selection path must identify character 05: {key}')
            require(source.is_file(), f'Missing selected source: {source}')
            require(sha(source) == selection['sha256'], f'Selected SHA mismatch: {key}')
            revision = selection.get('selected_revision', 'selected-override')
            visual = selection.get('visual_status', 'pending')
            require(visual in PENDING_STATES, f'Selected visual status must remain pending, not rejected/approved: {key}')
        elif new.is_file():
            source, revision, visual = new, 'canonical-v14-candidate', 'pending'
        else:
            missing.append(key)
            continue
        source = source.resolve()
        source_hash = sha(source)
        binding = selections.get('expected_sources', {}).get(key)
        if binding:
            require(source == resolve(binding['path']) and source_hash == binding['sha256'],
                    f'Source differs from bound path/SHA: {key}')
        with Image.open(source) as image:
            require(image.format == 'PNG' and image.mode == 'RGBA', f'Expected RGBA PNG: {source}')
            size = list(image.size)
            require(size == ([512, 512] if old.is_file() else [1024, 1024]),
                    f'Expected preserved 512 or new 1024 source: {key}: {size}')
            pixels = np.asarray(image)
            pixel_hash = hashlib.sha256(image.tobytes()).hexdigest()
        alpha = pixels[:, :, 3]
        ys, xs = np.where(alpha > 8)
        require(len(xs) > 0 and int(alpha.min()) == 0, f'Empty or nontransparent source: {key}')
        top, bottom = int(ys.min()), int(ys.max())
        height = bottom - top + 1
        axis = float(np.median(xs[ys < top + max(1, int((height - 1) * .42))]))
        records_file = record_origin(source, selection)
        record = read(records_file).get(key) if records_file else None
        world_scale = 1024 / size[0]
        rows.append({
            'path': key, 'source': str(source), 'sha256': source_hash,
            'pixel_sha256': pixel_hash, 'size': size, 'pixels_per_unit': 52 if size[0] == 512 else 104,
            'selected_revision': revision, 'visual_status': visual,
            'preserved_v13': old.is_file(), 'copied_byte_exact': False,
            'source_record_file': str(records_file) if records_file else None,
            'source_record_file_sha256': sha(records_file) if records_file else None,
            'source_record': record,
            'native_source_size': record.get('source', {}).get('native_size') if record else None,
            'source_provenance_status': 'record_present_not_revalidated' if record else 'record_missing_not_verified',
            'alpha_bbox_native': [int(xs.min()), top, int(xs.max()) + 1, bottom + 1],
            'alpha_min': int(alpha.min()), 'alpha_max': int(alpha.max()),
            'anchor_native_px': [axis, bottom], 'foot_y_world_1024': bottom * world_scale,
            'body_axis_world_1024': axis * world_scale, 'subject_height_world_1024': height * world_scale,
            'preview_display_only_scale': world_scale,
            'review_note': selections.get('review_notes', {}).get(key, '')})
    require(len({r['sha256'] for r in rows}) == len(rows), 'Duplicate PNG bytes across selected slots')
    require(len({(tuple(r['size']), r['pixel_sha256']) for r in rows}) == len(rows),
            'Duplicate decoded image pixels across selected slots')
    return rows, missing


def build_images(out, rows):
    by_key, gifs, directions = {r['path']: r for r in rows}, [], {}
    for direction in DIRS:
        keys = [f'walk/{direction}/{n:02d}.png' for n in range(1, 17)]
        present = [key for key in keys if key in by_key]
        complete = len(present) == 16
        directions[direction] = {'available_walk': len(present), 'complete_inventory': complete,
                                 'idle_present': f'idle/{direction}.png' in by_key, 'visual_approval': False}
        for mode, color in [('dark', (30, 38, 46)), ('light', (240, 238, 228))]:
            ink = 'white' if mode == 'dark' else 'black'
            contact = Image.new('RGB', (2048, 2240), color)
            draw, displays = ImageDraw.Draw(contact), []
            for index, key in enumerate(keys):
                display = Image.new('RGB', (512, 512), color)
                if key in by_key:
                    with Image.open(out / 'runtime' / key) as native:
                        small = native.convert('RGBA').resize((512, 512), Image.Resampling.LANCZOS)
                    display.paste(small, (0, 0), small)
                else:
                    ImageDraw.Draw(display).text((160, 250), 'MISSING - NO SUBSTITUTE', fill=ink)
                x, y = index % 4 * 512, index // 4 * 560
                contact.paste(display, (x, y + 32))
                source_label = str(by_key[key]['size'][0]) + 'px ' + by_key[key]['selected_revision'] if key in by_key else 'MISSING'
                draw.text((x + 10, y + 8), f'{direction}{index + 1:02d} / {source_label}', fill=ink)
                displays.append(display)
            contact.save(out / f'preview/{direction}-contact-{mode}.png')
            seam = Image.new('RGB', (2048, 570), color)
            seam_draw = ImageDraw.Draw(seam)
            for column, index in enumerate((14, 15, 0, 1)):
                seam.paste(displays[index], (column * 512, 48))
                seam_draw.text((column * 512 + 15, 15), f'{direction}{index + 1:02d}', fill=ink)
            seam.save(out / f'preview/{direction}-seam15-16-01-02-{mode}.png')
            if complete:
                path = out / f'preview/{direction}-30ms-{mode}.gif'
                displays[0].save(path, save_all=True, append_images=displays[1:],
                                 duration=[30] * 16, loop=0, optimize=False, disposal=2)
                with Image.open(path) as check:
                    durations = []
                    for index in range(check.n_frames):
                        check.seek(index)
                        durations.append(check.info['duration'])
                    require(check.n_frames == 16 and durations == [30] * 16,
                            f'GIF does not contain sixteen 30 ms frames: {path}')
                    require(check.info.get('loop') == 0, f'GIF is not an infinite loop: {path}')
                gifs.append({'path': path.relative_to(out).as_posix(), 'sha256': sha(path), 'frames': 16,
                             'duration_ms': durations, 'cycle_ms': sum(durations),
                             'loop': 0, 'interpolation': False})
    return directions, gifs


HTML = r'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><title>05 天音少女八方向审查预览</title><style>
body{font:16px system-ui;margin:24px;background:#eee9dc;color:#173833}h1{font-size:26px}button,select{font:inherit;padding:8px;margin:5px}canvas{background:#20262e;width:512px;height:512px}#stage{overflow:auto;max-width:100%;max-height:1100px}#timeline{max-width:1000px}#timeline button.active{background:#175d57;color:white}.warn{color:#9a4229}pre{white-space:pre-wrap;max-width:1200px}#seam{display:flex;overflow:auto;gap:12px}#seam img{width:256px;background:#20262e}</style>
<h1>05 天音少女 · 八方向行走与独立站立</h1><p id="summary" class="warn"></p><p id="known-issues" class="warn"></p><p>旧512与新1024均原字节保留，按同世界尺寸预览；30ms/帧、480ms/圈。缺帧只显示缺槽，不复制或生成替代帧。此快照待验收，不代表美术批准或客户端验收。</p>
<select id="direction" aria-label="方向"></select><select id="action" aria-label="动作"><option value="walk">行走</option><option value="idle">独立站立</option></select><button id="play">播放</button><button id="prev">上一帧</button><button id="next">下一帧</button><select id="speed" aria-label="速度"><option value="30">30 ms / 帧</option><option value="120">120 ms / 帧慢看</option></select><select id="bg" aria-label="背景"><option value="#20262e">深底</option><option value="#f0eee4">浅底</option></select><select id="size" aria-label="尺寸"><option value="512">正常 512 显示</option><option value="1024">放大 1024 世界像素</option></select><div id="stage"><canvas width="1024" height="1024" id="canvas"></canvas></div><div id="timeline"></div><pre id="info"></pre><p>首尾 15 → 16 → 01 → 02：</p><div id="seam"></div><p id="links"></p><p><a href="manifest.json">完整来源、哈希与库存</a></p>
<script>const manifest=__MANIFEST__,rows=Object.fromEntries(manifest.files.map(r=>[r.path,r])),ims={},canvas=document.getElementById('canvas'),ctx=canvas.getContext('2d'),play=document.getElementById('play'),direction=document.getElementById('direction'),action=document.getElementById('action'),speed=document.getElementById('speed'),info=document.getElementById('info');let frame=1,playing=false,last=0,elapsed=0;
document.getElementById('summary').textContent=`快照 ${manifest.revision} · ${manifest.actual_walk}/128 行走 + ${manifest.actual_idle}/8 站立 · 待验收 · 浏览器动态验收未记录`;
document.getElementById('known-issues').textContent=Object.entries(manifest.review_notes||{}).map(([k,v])=>k+'：'+v).join(' ');
for(const d of Object.keys(manifest.directions)){let o=document.createElement('option');o.value=d;o.textContent=`${d} (${manifest.directions[d].available_walk}/16)`;direction.appendChild(o)}
for(const r of manifest.files){const im=new Image();im.src='runtime/'+r.path;im.onload=()=>{if(key()===r.path)draw()};ims[r.path]=im}
const buttons=[];for(let i=1;i<=16;i++){let b=document.createElement('button');b.textContent=String(i).padStart(2,'0');b.onclick=()=>{pause();frame=i;draw()};document.getElementById('timeline').appendChild(b);buttons.push(b)}
function key(){return action.value==='idle'?`idle/${direction.value}.png`:`walk/${direction.value}/${String(frame).padStart(2,'0')}.png`}
function pause(){playing=false;play.textContent='播放';elapsed=0}
function draw(){ctx.clearRect(0,0,1024,1024);const k=key(),r=rows[k],im=ims[k];if(im?.complete&&im.naturalWidth)ctx.drawImage(im,0,0,1024,1024);else{ctx.font='bold 36px system-ui';ctx.fillStyle='#bb7443';ctx.fillText(r?'载入中':'缺槽 / 无替代帧',300,500)}info.textContent=r?`${k} | ${r.size.join('×')} | ${r.selected_revision} | ${r.visual_status}\nSHA256: ${r.sha256}\n来源: ${r.source}`:`${k} 缺少真实素材`;buttons.forEach((b,i)=>{b.className=i+1===frame?'active':'';b.disabled=action.value==='idle';b.style.opacity=rows[`walk/${direction.value}/${String(i+1).padStart(2,'0')}.png`]?'1':'.4'})}
function refreshDirection(){pause();frame=1;const seam=document.getElementById('seam');seam.replaceChildren();for(const n of [15,16,1,2]){let box=document.createElement('div'),label=document.createElement('div');label.textContent=direction.value+String(n).padStart(2,'0');box.appendChild(label);let k=`walk/${direction.value}/${String(n).padStart(2,'0')}.png`;if(rows[k]){let im=document.createElement('img');im.src='runtime/'+k;im.alt=label.textContent;im.style.background=document.getElementById('bg').value;box.appendChild(im)}else box.append('缺槽');seam.appendChild(box)}const d=direction.value;document.getElementById('links').innerHTML=`<a href="preview/${d}-contact-dark.png">深底16帧总览</a> · <a href="preview/${d}-contact-light.png">浅底总览</a> · <a href="preview/${d}-seam15-16-01-02-dark.png">深底接缝</a> · <a href="preview/${d}-seam15-16-01-02-light.png">浅底接缝</a>`+(manifest.directions[d].complete_inventory?` · <a href="preview/${d}-30ms-dark.gif">深底30ms GIF</a> · <a href="preview/${d}-30ms-light.gif">浅底30ms GIF</a>`:' · 缺帧，不生成完整GIF');draw()}
play.onclick=()=>{if(action.value==='idle')return;playing=!playing;play.textContent=playing?'暂停':'播放';elapsed=0};document.getElementById('prev').onclick=()=>{pause();frame=(frame+14)%16+1;draw()};document.getElementById('next').onclick=()=>{pause();frame=frame%16+1;draw()};direction.onchange=refreshDirection;action.onchange=()=>{pause();draw()};speed.onchange=()=>{elapsed=0};document.getElementById('bg').onchange=e=>{canvas.style.background=e.target.value;document.querySelectorAll('#seam img').forEach(i=>i.style.background=e.target.value)};document.getElementById('size').onchange=e=>{canvas.style.width=e.target.value+'px';canvas.style.height=e.target.value+'px'};
function tick(t){if(last&&playing){elapsed+=t-last;let ms=+speed.value;if(elapsed>=ms){let count=Math.floor(elapsed/ms);frame=(frame-1+count)%16+1;elapsed-=count*ms;draw()}}last=t;requestAnimationFrame(tick)}refreshDirection();requestAnimationFrame(tick);</script></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', help='New immutable snapshot name; required unless inspecting only')
    parser.add_argument('--selections', type=Path, default=HERE / 'selected-overrides.json')
    parser.add_argument('--inspect-only', action='store_true', help='Read inventory and selected hashes without writing')
    args = parser.parse_args()
    require(args.inspect_only or args.revision, '--revision is required when building')
    require(not args.revision or re.fullmatch(r'[A-Za-z0-9_-]+', args.revision), 'Invalid revision name')
    selection_path = args.selections.resolve()
    if selection_path.is_file():
        selections = read(selection_path)
    else:
        require(selection_path == (HERE / 'selected-overrides.json').resolve(), 'Explicit selection file does not exist')
        selections = {'character_id': CHAR, 'status': 'baseline_inventory_pending', 'overrides': {}}
    rows, missing = inventory(selections)
    summary = {'character_id': CHAR, 'walk': sum(r['path'].startswith('walk/') for r in rows),
               'idle': sum(r['path'].startswith('idle/') for r in rows),
               'preserved_v13_actions': sum(r['preserved_v13'] for r in rows),
               'selected_overrides': len(selections.get('overrides', {})), 'missing': missing, 'approved': False}
    if args.inspect_only:
        print(json.dumps(summary, ensure_ascii=False))
        return
    out = HERE / 'revisions' / args.revision
    require(not out.exists(), 'Use a fresh revision; an existing snapshot must never be overwritten')
    (out / 'preview').mkdir(parents=True)
    write(out / 'selection-input.json', selections)
    for row in rows:
        source, target = Path(row['source']), out / 'runtime' / row['path']
        require(sha(source) == row['sha256'], f'Source changed during build: {source}')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        require(sha(target) == row['sha256'], f'Copy SHA mismatch: {target}')
        row['copied_byte_exact'] = True
    directions, gifs = build_images(out, rows)
    for row in rows:
        require(sha(Path(row['source'])) == row['sha256'], f'Source changed during build: {row["source"]}')
    manifest = {
        'schema': 'qdao-05-mixed-review-pending-v1', 'created_at_utc': datetime.now(timezone.utc).isoformat(),
        'revision': args.revision, 'character_id': CHAR,
        'status': 'inventory_complete_visual_pending' if not missing else 'inventory_incomplete_visual_pending',
        'target_walk': 128, 'target_idle': 8, 'actual_walk': summary['walk'], 'actual_idle': summary['idle'],
        'preserved_v13_actions': summary['preserved_v13_actions'], 'missing': missing,
        'directions': directions, 'frame_duration_ms': 30, 'cycle_duration_ms': 480, 'files': rows,
        'gif_checks': gifs, 'source_png_bytes_unchanged': True, 'old512_not_upscaled_on_disk': True,
        'new1024_not_downscaled_on_disk': True, 'preview_only_equal_world_display': True,
        'synthetic_frames_created': 0, 'formal_approval': False, 'client_integration': False,
        'browser_dynamic_review': {'performed': False, 'reason': 'Builder does not perform visual acceptance.'},
        'selection_input_sha256': sha(out / 'selection-input.json'),
        'selection_original_path': str(selection_path) if selection_path.is_file() else None,
        'selection_original_sha256': sha(selection_path) if selection_path.is_file() else None,
        'known_rework_slots': selections.get('known_rework_slots', []),
        'review_notes': selections.get('review_notes', {})}
    write(out / 'manifest.json', manifest)
    compact = {**manifest, 'files': [{k: v for k, v in row.items() if k != 'source_record'} for row in rows]}
    payload = json.dumps(compact, ensure_ascii=False).replace('<', '\\u003c')
    (out / 'index.html').write_text(HTML.replace('__MANIFEST__', payload), encoding='utf-8')
    print(json.dumps({**summary, 'snapshot': str(out), 'gif_count': len(gifs), 'cycle_ms': 480}, ensure_ascii=False))


if __name__ == '__main__':
    main()
