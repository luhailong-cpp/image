"""Build v10 common and legacy UI skins from reviewed painted artwork.

Only writes the v10 staging and derived directories. The frozen contracts supply
pixel canvases, resize axes, nine-slice borders, content insets, and atlas cells.
Artwork source borders are explicit in artwork/index.json via art_support;
no percentage-based source cropping or old UI pixels are used.
"""
from pathlib import Path
import base64
import copy
import hashlib
import json
from xml.sax.saxutils import escape
from PIL import Image, ImageDraw
from art_support import PACK, REPO, load_art, fit_art, nine_slice, save

PACK = Path(PACK)
REPO = Path(REPO)
STAGED = PACK / 'staged'
DERIVED = PACK / 'derived'
COMPONENT_ROOT = Path('qdao_ui_redesign_v5/components')
ATOMIC_ROOT = Path('q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic')
SOURCE_MAP = 'qdao_ui_style_recut_v10/source-map.common.json'
BUILDER = 'qdao_ui_style_recut_v10/tools/build_common_legacy.py'
AUTHORING = ('New built-in image_gen v10 painted artwork matching the user reference; '
             'explicit source-border nine-slice resampling, alpha-preserving layout; '
             'portable embedded PNG in SVG. Dynamic text remains separate.')
SYMBOLS = ['taiji', 'pagoda', 'furnace', 'mountain', 'lotus', 'sword', 'water',
           'compass', 'peach_spirit', 'flame']
LANCZOS = Image.Resampling.LANCZOS


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def staged_path(relative):
    relative = Path(relative)
    target = (STAGED / relative).resolve()
    if not target.is_relative_to(STAGED.resolve()):
        raise ValueError(f'Unsafe staged path: {relative}')
    return target


def magnifier(canvas, x, y, size, color):
    """Native functional search glyph; not claimed as generated painted artwork."""
    scale = 3
    layer = Image.new('RGBA', (canvas.width * scale, canvas.height * scale))
    draw = ImageDraw.Draw(layer)
    x, y, r = x * scale, y * scale, size * .29 * scale
    line_width = max(2, round(size * .1 * scale))
    draw.ellipse((x-r, y-r, x+r, y+r), outline=color, width=line_width)
    draw.line((x+r*.65, y+r*.65, x+r*1.7, y+r*1.7), fill=color, width=line_width)
    canvas.alpha_composite(layer.resize(canvas.size, LANCZOS))


def common_skin(category, state):
    if category == 'main_frame':
        return 'frame'
    if category == 'content_panel':
        return 'panel'
    if state == 'disabled':
        return 'muted'
    if category == 'primary_button':
        return 'jade'
    if category == 'tab':
        # Ivory idle tabs preserve the contract's dark text; title is the active jade plaque.
        return 'title' if state == 'selected' else 'ivory'
    if category == 'list_row' or category.startswith('server_card'):
        return 'card_selected' if state == 'selected' else 'card_normal'
    if category == 'search':
        return 'card_selected' if state == 'selected' else 'card_normal'
    return 'card_normal'


def legacy_skin(asset):
    role, name, state = asset['role'], Path(asset['png']).name, asset.get('state', 'normal')
    if state == 'disabled':
        return 'muted'
    if role == 'tab' or name.startswith('top_button'):
        return 'title' if state == 'selected' else 'ivory'
    if role in {'list_row', 'server_card_base', 'search'} or name.startswith(('list_bg', 'server_card_bg')):
        return 'card_selected' if state == 'selected' else 'card_normal'
    if role == 'summary_bar' or name.startswith('bottom_bar'):
        return 'card_normal'
    return 'jade' if state == 'selected' else 'ivory'


def make_common(asset):
    width, height = asset['width'], asset['height']
    category, state = asset['category'], asset.get('state', 'normal')
    details = {}
    if asset.get('nine_slice'):
        key = common_skin(category, state)
        borders = [asset['nine_slice'][side] for side in ('left', 'top', 'right', 'bottom')]
        result = nine_slice(key, width, height, tuple(borders), pad=3)
        sources = [key]
        details['destination_borders_ltrb'] = borders
        if state in {'selected', 'disabled'}:
            glyph = 'check' if state == 'selected' else 'lock'
            x, y = width-49 if category == 'search' else 30, round((height-40)/2-2)
            result.alpha_composite(fit_art(glyph, 32, 32, pad=0), (x, y))
            sources.append(glyph)
            details['state_glyph_xywh'] = [x, y, 32, 32]
            if state == 'selected':
                draw = ImageDraw.Draw(result)
                draw.line((20, height/2-13, 20, height/2+13), fill='#F5DE92', width=4)
                draw.polygon([(38, height-12), (62, height-12), (50, height-18)], fill='#EDD48B')
                details['native_semantic_marks'] = ['selection rail', 'bottom selection notch']
        if category == 'search':
            color = '#697764' if state == 'disabled' else '#FFF7DE' if state == 'selected' else '#795638'
            magnifier(result, 39, height/2-5, 32, color)
            details.setdefault('native_semantic_marks', []).append('search magnifier')
        if category in {'main_frame', 'content_panel'}:
            if result.getpixel((width//2, height//2))[3] < 250:
                raise ValueError(f'{asset["id"]}: opaque ivory center contract not met')
    elif category == 'round_badge':
        key = asset['symbol']
        result, sources = fit_art(key, width, height, pad=5), [key]
    elif category == 'status_dot':
        key = 'status_' + state
        result, sources = fit_art(key, width, height, pad=2), [key]
    else:
        key = {'gold_flower': 'flower', 'cloud_corner': 'corner', 'recommend_badge': 'recommend'}.get(category, category)
        result, sources = fit_art(key, width, height, pad=2), [key]
    return result, sources, details


def make_legacy(asset, badge_cells):
    width, height, role = asset['width'], asset['height'], asset['role']
    details = {}
    if role in {'tab', 'list_row', 'search', 'summary_bar', 'server_card_base', 'control_base'}:
        logical_width, logical_height = asset.get('legacy_import', {}).get('target_size', [width, height])
        grid = (asset.get('legacy_import', {}).get('scale9grid_center_xywh')
                or asset['nine_slice']['center_xywh'])
        left, top, center_width, center_height = grid
        sx, sy = width/logical_width, height/logical_height
        borders = [round(left*sx), round(top*sy), round((logical_width-left-center_width)*sx),
                   round((logical_height-top-center_height)*sy)]
        key = legacy_skin(asset)
        result = nine_slice(key, width, height, tuple(borders), pad=max(2, round(3*min(sx, sy))))
        details['destination_borders_ltrb'] = borders
        details['logical_grid_center_xywh'] = grid
        if role == 'search':
            magnifier(result, min(32, left/2)*sx, (logical_height/2-4)*sy,
                      26*min(sx, sy), '#795638')
            details['native_semantic_marks'] = ['search magnifier']
        sources = [key]
    elif role in {'round_badge', 'legacy_alias'}:
        key = asset['symbol']
        result, sources = fit_art(key, width, height, pad=5 if width == 420 else 2), [key]
    elif role == 'status_dot':
        key = 'status_' + asset.get('status_color', 'red')
        result, sources = fit_art(key, width, height, pad=3), [key]
    elif role == 'ornament':
        result, sources = fit_art('flower', width, height, pad=5), ['flower']
    elif role == 'decorative_divider':
        result, sources = fit_art('divider', width, height, pad=2), ['divider']
    elif role == 'badge_sheet':
        result = Image.new('RGBA', (width, height))
        for symbol, cell in zip(SYMBOLS, badge_cells, strict=True):
            x, y, cell_width, cell_height = cell['source_cell']
            # Keep the historic 328px painted item box and all source-cell coordinates.
            result.alpha_composite(fit_art(symbol, 328, 328, pad=4),
                                   (round(x+(cell_width-328)/2), round(y+(cell_height-328)/2)))
        sources = list(SYMBOLS)
        details['atlas_source_cells_preserved'] = [cell['source_cell'] for cell in badge_cells]
    else:
        raise ValueError(f'Unknown legacy role: {role}')
    return result, sources, details


def export_pair(image, png_relative, svg_relative, derived_path, title):
    if image.mode != 'RGBA':
        raise ValueError(f'{title}: artwork is not RGBA')
    if image.getchannel('A').getextrema() != (0, 255):
        raise ValueError(f'{title}: alpha contract must contain both 0 and 255')
    save(image, derived_path)
    data = Path(derived_path).read_bytes()
    png_path, svg_path = staged_path(png_relative), staged_path(svg_relative)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    svg_path.parent.mkdir(parents=True, exist_ok=True)
    png_path.write_bytes(data)
    width, height = image.size
    encoded = base64.b64encode(data).decode('ascii')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
           f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">'
           f'<title>{escape(title)}</title><image width="{width}" height="{height}" '
           f'xlink:href="data:image/png;base64,{encoded}"/></svg>\n')
    svg_path.write_text(svg, encoding='utf-8')
    return {'png_sha256': sha(data), 'svg_sha256': sha(svg.encode('utf-8'))}


def main():
    common = copy.deepcopy(read_json(PACK/'contracts/components.json'))
    legacy = copy.deepcopy(read_json(PACK/'contracts/legacy.json'))
    badge_manifest = read_json(REPO/ATOMIC_ROOT/'manifest_ai_qstyle_badges.json')
    cells = badge_manifest['outputs']
    derivatives, records = {}, []
    for asset in common['assets']:
        result, sources, details = make_common(asset)
        assert result.size == (asset['width'], asset['height'])
        png, svg = COMPONENT_ROOT/asset['png'], COMPONENT_ROOT/asset['svg']
        hashes = export_pair(result, png, svg, DERIVED/'components'/f'{asset["id"]}.png', asset['id'])
        asset.pop('v7_sources', None)
        asset.update(authoring=AUTHORING, v10_sources=sources, v10_source_map='../../'+SOURCE_MAP, **hashes)
        derivatives[asset['id']] = sources
        records.append({'id': asset['id'], 'png': png.as_posix(), 'svg': svg.as_posix(),
                        'size': list(result.size), 'sources': sources, **details, **hashes})
    for asset in legacy['assets']:
        result, sources, details = make_legacy(asset, cells)
        assert result.size == (asset['width'], asset['height'])
        hashes = export_pair(result, asset['png'], asset['svg'],
                             DERIVED/'legacy'/Path(asset['png']).name, Path(asset['png']).stem)
        asset.pop('v7_source_map', None)
        asset.update(authoring=AUTHORING, v10_sources=sources, v10_source_map=SOURCE_MAP, **hashes)
        derivatives[asset['png']] = sources
        records.append({'png': asset['png'], 'svg': asset['svg'], 'size': list(result.size),
                        'sources': sources, **details, **hashes})
    save(fit_art('status_red', 32, 32, pad=2), DERIVED/'status_red.png')
    save(fit_art('divider', 142, 35, pad=2), DERIVED/'divider.png')
    native_sources = []
    for source in sorted((PACK/'source').glob('*.png')):
        with Image.open(source) as picture:
            native_sources.append({'file': source.relative_to(PACK).as_posix(),
                                   'size': list(picture.size), 'sha256': sha(source.read_bytes())})
    provenance = {'source_map': '../../'+SOURCE_MAP, 'prepare': '../../'+BUILDER,
                  'artwork_index': '../../qdao_ui_style_recut_v10/artwork/index.json',
                  'native_sources': native_sources, 'model_parameter_exposed': False,
                  'quality_parameter_exposed': False}
    common.update(version='10.0', updated='2026-09-10', authoring=AUTHORING, ai_provenance=provenance)
    common['renderer'] = {'png': 'Pillow', 'svg': 'portable embedded PNG'}
    legacy.update(version='gpt-image2-q10', date='2026-09-10', source_builder=BUILDER,
                  ai_provenance={**provenance, 'source_map': SOURCE_MAP, 'prepare': BUILDER,
                                 'artwork_index': 'qdao_ui_style_recut_v10/artwork/index.json'},
                  renderer={'png': 'Pillow', 'svg': 'portable embedded PNG'})
    write_json(staged_path(COMPONENT_ROOT/'manifest.json'), common)
    write_json(staged_path('exact_qdao_slices/manifest_native_q5.json'), legacy)
    atomic = copy.deepcopy(legacy)
    atomic['assets'] = [asset for asset in legacy['assets'] if asset['png'].startswith(ATOMIC_ROOT.as_posix()+'/')]
    atomic.update(asset_count=len(atomic['assets']), exact_slice_count=0,
                  full_manifest='../../exact_qdao_slices/manifest_native_q5.json')
    write_json(staged_path(ATOMIC_ROOT/'manifest_native_q5.json'), atomic)
    redrawn = read_json(REPO/ATOMIC_ROOT/'manifest_redrawn.json')
    redrawn.update(version='gpt-image2-q10', authoring=AUTHORING, v10_source_map='../../'+SOURCE_MAP)
    write_json(staged_path(ATOMIC_ROOT/'manifest_redrawn.json'), redrawn)
    badge_manifest.update(authoring='New built-in image_gen v10 painted emblems; true-alpha atlas at preserved legacy coordinates.',
                          v10_source_map='../../'+SOURCE_MAP)
    write_json(staged_path(ATOMIC_ROOT/'manifest_ai_qstyle_badges.json'), badge_manifest)
    source_map = {'tool': 'built-in image_gen', 'requested_model': 'gpt-image-2',
                  'requested_quality': 'highest available; tool has no exposed quality parameter',
                  'model_parameter_exposed': False, 'quality_parameter_exposed': False,
                  'style_reference': '../docs/references/ui-style-20260910.png',
                  'artwork_index': 'artwork/index.json', 'native_sources': native_sources,
                  'derivatives': derivatives, 'records': records,
                  'postprocess': 'Reviewed RGBA painted crops; explicit source borders mapped to preserved contract destination borders; uniform icons and atlas placement; native search and state markers identified per asset.'}
    write_json(PACK/'source-map.common.json', source_map)
    print(json.dumps({'common_assets': len(common['assets']), 'legacy_assets': len(legacy['assets']),
                      'png_svg_pairs': len(records), 'status': 'staged_for_visual_review'}))


if __name__ == '__main__':
    main()
