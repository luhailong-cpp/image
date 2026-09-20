from pathlib import Path
import json, os

batch = Path(__file__).resolve().parents[1]
registry = Path.home() / '.codex/image-generation-config.json'
override = os.environ.get('GPT_IMAGE_CONFIG')
if override is not None:
    if not override.strip():
        raise ValueError('GPT_IMAGE_CONFIG must name a nonempty JSON path')
    settings_path = Path(override.strip()).expanduser()
else:
    current = Path.cwd()
    settings_path = next((parent / 'config/image-generation.json' for parent in (current, *current.parents) if (parent / 'config/image-generation.json').is_file()), None)
    if settings_path is None:
        settings_path = Path(json.loads(registry.read_text(encoding='utf-8-sig'))['config_path']).expanduser()
        if not settings_path.is_absolute():
            settings_path = registry.parent / settings_path
image_settings = json.loads(settings_path.read_text(encoding='utf-8-sig'))
if not isinstance(image_settings, dict) or type(image_settings.get('schema_version')) is not int or image_settings['schema_version'] != 1:
    raise ValueError('Image settings require schema_version=1')
if not all(isinstance(image_settings.get(k), str) and image_settings[k].strip() for k in ('model', 'quality')):
    raise ValueError('Image settings require nonempty model and quality')
catalog_path = batch / 'production_catalog.json'
catalog = json.loads(catalog_path.read_text(encoding='utf-8-sig'))
plans = batch / 'q64_production_plans'
plans.mkdir(exist_ok=True)
for appearance in catalog['variants']:
    runtime_variant = 'day' if appearance['variant'] == 'day' else 'festival'
    appearance['runtimeVariant'] = runtime_variant
    appearance_id = appearance['city'] + '_' + appearance['variant']
    source_w, source_h = appearance['sourcePixels']
    tiles = []
    for row in range(16):
        for col in range(16):
            tile_id = f'r{row+1:02d}_c{col+1:02d}'
            x, z = 50 + col * 18.75, 300 - (row + 1) * 18.75
            tile = {
                'id': tile_id, 'row': row + 1, 'column': col + 1,
                'finalPixelRect': [col * 4096, row * 4096, 4096, 4096],
                'worldRect': {'x': x, 'z': z, 'width': 18.75, 'height': 18.75},
                'runtimeWorldRect': {'x': x, 'y': z, 'width': 18.75, 'height': 18.75},
                'plannedOutput': f"{appearance['city']}/{runtime_variant}/tiles/{tile_id}.png",
                'originalLayoutSourceBox': [col * source_w / 16, row * source_h / 16, (col + 1) * source_w / 16, (row + 1) * source_h / 16],
                'state': 'planned_not_generated', 'nativeGenerationRequired': True, 'accepted': False,
            }
            if appearance_id == 'tianyong_festival' and tile_id == 'r10_c07':
                assert x == 162.5 and z == 112.5
                tile['state'] = 'local_candidate_exists_not_production_accepted'
                tile['candidateFile'] = '../builtin_q64_r10_c07/output/tianyong_r10_c07_q64_4k_candidate.png'
            tiles.append(tile)
    assert len(tiles) == 256 and len({t['id'] for t in tiles}) == 256
    assert tiles[0]['finalPixelRect'] == [0, 0, 4096, 4096]
    assert tiles[-1]['finalPixelRect'] == [61440, 61440, 4096, 4096]
    plan = {
        'schemaVersion': 1, 'kind': 'offline_production_plan_not_runtime_manifest',
        'city': appearance['city'], 'appearance': appearance['variant'],
        'runtimeVariant': runtime_variant, 'displayName': appearance['displayName'],
        'route': 'builtin_image_gen', 'requestedModel': image_settings['model'],
        'requestedQuality': image_settings['quality'],
        'imageSettingsConfig': str(settings_path.resolve()),
        'imageModelPolicy': '../../docs/IMAGE_MODEL_POLICY.md',
        'requestMeaning': 'Future generation preference; actual model and quality require per-call evidence. Host selectors may be unavailable.',
        'wholeCityPixels': [65536, 65536], 'grid': {'rows': 16, 'columns': 16},
        'tilePixels': [4096, 4096], 'originalLayoutSource': appearance['source'],
        'originalLayoutSourceSha256': appearance['sourceSha256'],
        'worldRect': {'x': 50, 'z': 0, 'width': 300, 'height': 300},
        'fullCityStyleReference': f'../builtin_q64_all_city_references/{appearance_id}/map-native-layout-reference.png',
        'referenceRole': 'Style/layout only; never interpolate as production art',
        'productionTilesAccepted': 0, 'runtimePublished': False, 'tiles': tiles,
    }
    (plans / f'{appearance_id}.json').write_text(json.dumps(plan, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    appearance['completeGridPlan'] = f'q64_production_plans/{appearance_id}.json'
catalog_path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'planFiles': 7, 'plannedTiles': 1792, 'existingSampleCoordinateVerified': True, 'runtimePublished': False}))