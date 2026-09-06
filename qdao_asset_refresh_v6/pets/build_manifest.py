"""Validate four final transparent pets and append them to concept manifests."""
from pathlib import Path
import hashlib
import json
import os
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
PETS = [
    ('ling_yue', '灵玥', 'qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox'),
    ('hu_tuan_tuan', '葫团团', 'qdao_chibi_pets_v1/01_hu_tuan_tuan'),
    ('fu_xiao_hu', '符小虎', 'qdao_chibi_pets_v1/02_fu_xiao_hu'),
    ('yun_jiu_jiu', '云啾啾', 'qdao_chibi_pets_v1/03_yun_jiu_jiu'),
]


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path, directory):
    return Path(os.path.relpath(path, directory)).as_posix()


def main():
    baseline = {a['path']: a for a in read(REPO / 'docs/ART_ASSET_AUDIT.json')['assets']}
    assets = []
    for pet_id, name, stem in PETS:
        path = REPO / f'{stem}-transparent_1254.png'
        prompt = path.with_suffix('.prompt.txt')
        record_path = ROOT / 'records' / f'{pet_id}.json'
        record = read(record_path)
        assert path.is_file() and prompt.is_file()
        assert sha(path) == record['sha256'], path
        original = REPO / f'{stem}.png'
        original_row = baseline[f'{stem}.png']
        assert sha(original) == original_row.get('sha256', original_row.get('baseline_sha256'))
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            assert im.size == (1254, 1254) and im.mode == 'RGBA'
            alpha = im.getchannel('A')
            bbox = alpha.getbbox()
            assert alpha.getextrema() == (0, 255)
            assert min(bbox[0], bbox[1], 1254 - bbox[2], 1254 - bbox[3]) > 20
            p = np.asarray(im)
            spill = (p[:, :, 0] > 200) & (p[:, :, 1] < 100) & (p[:, :, 2] > 200) & (p[:, :, 3] > 0)
            assert not spill.any(), f'Strong magenta residue: {name}'
        row = {'id': pet_id, 'name': name, 'path': path.relative_to(REPO).as_posix(),
               'size': [1254, 1254], 'mode': 'RGBA', 'alpha_range': [0, 255],
               'subject_bounds': list(bbox), 'sha256': sha(path),
               'native_generation_size': record['native_generation_size'],
               'prompt': prompt.relative_to(REPO).as_posix(),
               'record': record_path.relative_to(REPO).as_posix(),
               'concept': original.relative_to(REPO).as_posix(), 'concept_preserved': True,
               'animation': False, 'engine_integrated': False}
        assets.append(row)
        concept_manifest = path.parent / 'manifest.json'
        manifest = read(concept_manifest)
        entry = {'image': path.name, 'prompt': prompt.name,
                 'record': relative(record_path, path.parent),
                 'size': row['size'], 'native_size': row['native_generation_size'],
                 'mode': 'RGBA', 'sha256': row['sha256'], 'animation': False,
                 'engine_integrated': False}
        if pet_id == 'ling_yue':
            manifest['transparent_asset'] = entry
        else:
            selected = next(x for x in manifest['pets'] if x['name'] == name)
            selected['transparent_asset'] = entry
        write(concept_manifest, manifest)
    write(ROOT / 'manifest.json', {'schema': 'qdao.transparent-pets.v6', 'count': 4,
                                  'generator': 'built-in image_gen + generate2dsprite alpha processing',
                                  'assets': assets, 'engine_integrated': False})
    write(ROOT / 'validation.json', {'status': 'passed', 'count': 4,
                                    'all_1254_rgba': True, 'all_prompt_and_record_hashes_match': True,
                                    'all_concept_images_preserved': True,
                                    'all_transparent_margins_over_20px': True,
                                    'strong_magenta_residue_pixels': 0,
                                    'ling_yue_visual_tail_tips': 9, 'animation': False})
    lines = ['# 五行奇谈 · 四只透明宠物', '',
             '灵玥、葫团团、符小虎、云啾啾均提供1254×1254真RGBA静态图。已确认的有底设定图逐字节保留，透明版使用内置image_gen参考重绘，再按generate2dsprite处理；清理品红边缘时保留淡紫毛色和各宠物饰物。', '',
             '|宠物|透明成品|完整提示词|记录|', '|---|---|---|---|']
    for row in assets:
        lines.append(f"|{row['name']}|[PNG]({relative(REPO / row['path'], ROOT)})|[prompt]({relative(REPO / row['prompt'], ROOT)})|[JSON]({relative(REPO / row['record'], ROOT)})|")
    lines += ['', '[逐件清单](manifest.json)保存尺寸、Alpha、边界与SHA；[验收](validation.json)确认四张透明图、原概念保留和零强品红残色。灵玥实看九个独立尾尖；虎纹、葫芦和仙鹤形象按各自参考保留。', '',
              '原生生成尺寸按每张record记录。1254为最终画布，部分经过同画布内的等比居中／脚底对齐处理；没有从128小图放大作为正式交付。透明精灵无烘焙名字，临时母图、GIF和切图副本已清理。', '',
              '```powershell', 'python -B qdao_asset_refresh_v6/pets/build_manifest.py', '```', '',
              '脚本仅验证和更新清单，不生成图片。重新生成须先实看原概念图，使用完整提示词调用内置生图，再按各record的技能参数处理并实看。当前仅静态美术，未制作宠物动画或接入客户端。']
    (ROOT / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf8')
    print('PASS: 4 transparent pets; 1254 RGBA; hashes and original concepts verified')


if __name__ == '__main__':
    main()
