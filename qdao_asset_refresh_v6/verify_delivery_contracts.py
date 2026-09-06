"""Read-only checks for movement anchors, compatibility hashes and UI layers."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    move = REPO / 'character_move_8dir'
    manifest = read(move / 'manifest.json')
    frames = 0
    for direction, record in manifest['directions'].items():
        assert len(record['frames']) == 4
        assert (move / record['prompt']).is_file()
        assert (move / record['qc']).is_file()
        hashes = set()
        for row in record['frames']:
            path = move / row['file']
            assert digest(path) == row['sha256'], path
            hashes.add(row['sha256'])
            with Image.open(path) as im:
                assert im.size == (1254, 1254) and im.mode == 'RGBA'
                alpha = im.getchannel('A')
                bbox = alpha.getbbox()
                assert list(bbox) == row['alpha_bbox'] and bbox[3] == 1179
                assert alpha.getextrema() == (0, 255)
            frames += 1
        assert len(hashes) == 4, f'Duplicate frames in {direction}'
    assert frames == 32 and len(manifest['directions']) == 8

    compatibility = read(ROOT / 'hero_compat_manifest.json')['assets']
    for row in compatibility:
        path = REPO / row['path']
        assert digest(path) == row['sha256'], path
        with Image.open(path) as im:
            assert list(im.size) == row['size'] and im.mode == 'RGBA'
    assert len(compatibility) == 9

    layer_dir = REPO / 'q_daoist_login_ui_uncropped_highres_final_layers'
    layers = read(layer_dir / 'manifest_native_q5.json')['outputs']
    for row in layers:
        path = REPO / row['path']
        assert digest(path) == row['sha256'], path
        with Image.open(path) as im:
            assert list(im.size) == row['size'] and im.mode == row['mode']
    for size in ('5120x2160', '10240x4320'):
        with Image.open(layer_dir / f'q_daoist_login_background_ui_uncropped_final_{size}.png') as base, \
             Image.open(layer_dir / f'q_daoist_login_buttons_uncropped_final_{size}.png') as controls, \
             Image.open(layer_dir / f'q_daoist_login_ui_uncropped_final_recomposed_{size}.png') as actual:
            expected = Image.alpha_composite(base, controls)
            extrema = ImageChops.difference(expected, actual).getextrema()
            # Pillow rounds while the source builder (Sharp/libvips) truncates RGB.
            assert all(channel[1] <= 1 for channel in extrema[:3]) and extrema[3][1] == 0, size
            expected.close()

    # The only refreshed review board is allowed to change within preserve scope.
    allowed = {'qdao_ui_redesign_v5/components/overview.png',
               'qdao_ui_redesign_v5/components/overview.svg'}
    preserved = 0
    for row in read(REPO / 'docs/ART_ASSET_AUDIT.json')['assets']:
        if row['action'] == 'preserve' and row['path'] not in allowed:
            assert digest(REPO / row['path']) == row.get('sha256', row.get('baseline_sha256')), row['path']
            preserved += 1
    result = {'status': 'passed', 'movement_frames': frames,
              'distinct_frames_per_direction': 4, 'feet_y': 1179,
              'canonical_hero_compatibility_exports': len(compatibility),
              'legacy_ui_outputs': len(layers), 'independent_alpha_compositions': 2,
              'cross_library_rgb_tolerance': 1, 'alpha_tolerance': 0,
              'native_sharp_exact_recomposition_record': '../q_daoist_login_ui_uncropped_highres_final_layers/validation_native_q5.json',
              'accepted_files_preserved_byte_for_byte': preserved,
              'engine_integration': False}
    (ROOT / 'contracts_validation.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
