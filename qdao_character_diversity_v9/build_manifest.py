"""Validate and index the 22 redesigned straight-haired original Daoist Q characters."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PACK = REPO / 'q_daoist_character_pack_4096'

# Manually authored design labels, not generated image prompts.
DESIGNS = {
 1: ('霜刃女冠', '成年', '窄鹅蛋脸、细长眼', '直黑短发、白玉道冠', '直线长袍、清冷收剑'),
 2: ('赤符小顽童', '幼童', '雀斑圆鼻、缺牙笑', '直发双丸束髻', '矮圆短打、蓬松裤脚'),
 3: ('莲灯医姑', '中年', '丰润脸、弯月笑眼', '低盘直发、一缕白发', '宽大藕粉医袍、莲灯'),
 4: ('镇岳护法', '成年', '方脸浓平眉、小胡须', '直发高束髻', '宽肩短厚护甲、圆盾'),
 5: ('紫微琴师', '成年', '长椭圆脸、半垂凤眼', '银灰直发长辫', '紫灰大袖、侧身弦乐'),
 6: ('白眉雷师', '老年', '白眉短白须、圆鼻', '直白发、黑高法冠', '矮实深靛法袍、雷令'),
 7: ('玄月夜行女', '青年', '小麦肤、棱角脸灰眼', '短直靛发、偏分', '精瘦短道服、双月刃'),
 8: ('圆肚丹师', '中年', '圆眼镜、小胡须', '直发小髻、后退发际', '最圆腹、橘米围袍、丹炉'),
 9: ('竹间弓手', '青年', '晒肤长脸、浅雀斑', '直发长辫、竹笠', '轻短袍、绑腿、竹弓'),
 10: ('赤缨枪将', '成年', '方圆脸、利落浓眉', '直黑高马尾', '强健短甲、方形裙甲'),
 11: ('玉拳少年', '少年', '圆脸粗弯眉、眯眼笑', '直短寸头、侧边剃线', '矮壮桶形、大玉护拳'),
 12: ('铁刃老客', '年长', '窄长脸、灰胡须', '直发、黑布方巾', '瘦长宽袍、肩扛铁刀'),
 13: ('风行短发女', '青年', '心形脸、单侧虎牙', '栗红偏分短直发', '三角披风、灯笼裤'),
 14: ('雪团小女冠', '幼童', '困倦圆眼、小圆脸', '直银发、低双发髻', '最矮球形厚斗篷、抱雪兔'),
 15: ('沧浪水士', '成年', '长脸柳叶眼', '中分直黑发、小玉冠', '修长Q长衫、水纹折扇'),
 16: ('金铃舞姬', '青年', '蜜色肤、弯眉笑眼', '直黑发双粗辫', '灯笼裤、短披肩、双铃'),
 17: ('墨篆先生', '老年', '白眉长须、小圆墨镜', '直白发、高儒道冠', '细窄墨袍、毛笔卷轴'),
 18: ('沙海道姑', '成年', '深棕肤、宽颧骨', '直发盘辫、沙色头巾', '坚实披袍、宽腰带、日轮杖'),
 19: ('山野御灵童', '少年', '棕肤三角脸、机灵眉', '分层短直发、叶饰', '草编披肩、短裤、竹笛'),
 20: ('星盘女掌门', '成年', '菱形脸、窄长眼', '直黑发高盘髻、银月簪', '庄重钟形长袍、罗盘阵旗'),
 21: ('胖灶道长', '中年', '宽圆脸、八字胡笑眼', '直黑短发、白厨巾', '宽壮圆腹、围裙、铁锅'),
 22: ('茶肆小刀客', '青年', '窄下巴、单挑眉', '整齐直黑锅盖短发', '细瘦短褂、白围腰、茶盘短刀'),
}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    current = Path(__file__).resolve().parents[1] / 'qdao_character_diversity_v9/festival_edge_refinement.json'
    if current.exists():
        import runpy
        runpy.run_path(str(current.parent.parent / 'qdao_festival_refinement_20260910/v9-edges/verify_current.py'), run_name='__main__')
        return
    baseline = read(HERE / 'baseline.json')
    previous = {x['path']: x for x in baseline['assets']}
    inherited = {x['path']: x for x in read(HERE / 'inherited_refinements.json')['records']}
    edges = {x['path']:x for x in read(HERE / 'final_edge_cleanup.json')['records']}
    assert set(edges) <= set(previous)
    assert set(inherited) <= set(previous)
    published = {x['path']: x for x in read(REPO / 'qdao_exposure_refinement_v8/processing.json')['records']}
    assets = []
    # Limit this revision to the original paths; later packs are independent.
    for path in sorted(REPO / row['path'] for row in baseline['assets']):
        number = int(path.name[:2]) if path.name[:2].isdigit() else 0
        name = DESIGNS[number][0] if number else '金发带Q道童'
        digest = sha(path)
        candidates = 0
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            assert im.size == (4096, 4096) and im.mode == 'RGBA', path.name
            alpha = im.getchannel('A'); bbox = alpha.getbbox()
            assert alpha.getextrema() == (0, 255)
            assert min(bbox[0], bbox[1], 4096-bbox[2], 4096-bbox[3]) > 20
            if number:
                p = np.asarray(im)
                candidates = int(((p[:, :, 0]>200) & (p[:, :, 1]<100) & (p[:, :, 2]>200) & (p[:, :, 3]>0)).sum())
        row = {'id': path.stem, 'name': name, 'path': path.name, 'size': [4096,4096],
               'mode': 'RGBA', 'alpha_range': [0,255], 'subject_bounds': list(bbox), 'sha256': digest,
               'strong_chroma_candidates': candidates}
        original = previous[path.relative_to(REPO).as_posix()]
        refinement = inherited.get(path.relative_to(REPO).as_posix())
        edge = edges.get(path.relative_to(REPO).as_posix())
        if edge:
            assert edge['status'] == 'passed' and edge['alpha_unchanged'] and edge['outside_regions_unchanged']
            assert digest == edge['output_sha256']
        if refinement:
            source = published[refinement['path']]
            assert refinement['status'] == source['status'] == 'published'
            assert refinement['alpha_unchanged'] is True
            inherited_output = edge['before_sha256'] if edge else digest
            assert inherited_output == refinement['output_sha256'] == source['output_sha256']
            assert refinement['original_sha256'] == source['original_sha256']
        if number:
            record_path = PACK / 'records' / f'{path.stem}.json'
            record = read(record_path)
            assert record['art_revision'] == 'v9-character-diversity', path.name
            assert digest == record['sha256'] and digest != original['sha256']
            if refinement:
                assert record['generation_export_sha256'] == refinement['original_sha256']
                assert record['inherited_refinement'] == refinement
            if edge:
                assert record['final_edge_cleanup'] == edge
            assert (PACK / record['prompt']).is_file()
            assert record['model_and_quality_verified'] is False
            row.update({'age_direction': DESIGNS[number][1], 'face_direction': DESIGNS[number][2],
                        'hair_direction': DESIGNS[number][3], 'silhouette_direction': DESIGNS[number][4],
                        'prompt': record['prompt'], 'record': record_path.relative_to(PACK).as_posix(),
                        'creation_method': 'individually generated original Daoist Q redesign',
                        'native_generation_size': record['native_generation_size']})
        else:
            refinement = inherited.get(path.relative_to(REPO).as_posix())
            expected_sha = refinement['output_sha256'] if refinement else original['sha256']
            if refinement:
                assert refinement['original_sha256'] == original['sha256'] and refinement['alpha_unchanged']
            assert digest == expected_sha, 'Preserved canonical hero changed outside verified refinement'
            row.update({'creation_method': 'approved canonical hero identity preserved; inherited verified v8 exposure refinement',
                        'record': '../qdao_asset_refresh_v6/hero_compat_manifest.json'})
        assets.append(row)
    assert len(assets) == 24 and sum('age_direction' in row for row in assets) == 22
    visual = read(HERE / 'visual_qa.json')
    assert visual['status'] == 'passed' and len(visual['assets']) == 22
    reviewed = {row['id']: row for row in visual['assets']}
    for row in assets:
        if 'age_direction' in row:
            assert reviewed[row['id']]['sha256'] == row['sha256'], 'Visual review is stale'
            assert reviewed[row['id']]['status'] == 'passed'
            assert row['strong_chroma_candidates'] == reviewed[row['id']].get('accepted_color_candidates', 0), 'Unreviewed color-key candidate'
    manifest = {'schema': 'qdao.portraits.v9', 'date': '2026-09-11',
                'baseline_commit': baseline['baseline_commit'], 'final_count':24,
                'individually_redesigned_characters':22, 'preserved_canonical_hero_aliases':2,
                'common_size':[4096,4096], 'style':'original diverse Daoist Q cast; no curly hair',
                'native_size_policy':'4096 is compatibility export; actual native sizes recorded per image',
                'asset_root':'q_daoist_character_pack_4096',
                'model_quality_policy':'Project AGENTS documents the built-in GPT Image 2 path. The tool exposes no model or quality switch; high quality is the goal, not a force-set per-call parameter.',
                'status':'static_art_only', 'engine_integration':False, 'assets':assets}
    write(PACK / 'manifest.json', manifest)
    write(HERE / 'manifest.json', manifest)
    write(HERE / 'compatibility_map.json', {'date':'2026-09-11', 'count':24,
          'mapping':[{'old_path':prior['path'], 'new_path':prior['path'],
              'old_size':prior['size'], 'new_size':row['size'],
              'old_sha256':prior['sha256'], 'new_sha256':row['sha256'],
              'action':'redesigned' if 'age_direction' in row else 'preserved'
          } for row in assets for prior in [previous['q_daoist_character_pack_4096/' + row['path']]]]})
    write(HERE / 'validation.json', {'status':'passed', 'date':'2026-09-11', 'redesigned':22, 'preserved':2,
          'all_same_original_paths_and_sizes':True, 'all_rgba':True,
          'all_current_record_hashes_match':True,
          'inherited_published_refinements':len(inherited),
          'inherited_alpha_unchanged':True,
          'local_edge_cleanup_count':len(edges),
          'local_edge_cleanup_alpha_and_outside_regions_unchanged':True, 'all_redesigns_changed':True,
          'unreviewed_strong_chroma_candidates':0,
          'reviewed_color_candidates':sum(row['strong_chroma_candidates'] for row in assets),
          'all_transparent_margins_over_20px':True,
          'native_resolution_separately_recorded':True,
          'visual_review':'passed; current hashes match visual_qa.json',
          'engine_integration':False})
    lines = ['# 五行奇谈 · 原创道家Q版人物', '',
       '2026-09-11完成根据“人物太相似”的反馈重设计01–22职业人物。全部保留原文件名和4096×4096真RGBA画布；两张金发带主角参考造型保持，沿用此前已验收的曝光修正。角色通过脸型、年龄感、直发发型、胖瘦体态、衣袍轮廓和姿态区分。', '',
       '全部不用卷发；直发可剪短、束起、盘髻或编辫。可借鉴传统仙侠群像的洒脱、清灵、英气和灵动气质，具体脸型、头饰、服装、配色和法器为本项目重新设计，不采用既有角色的成套标志性组合。', '',
       '[角色清单](manifest.json) · [设计说明](../qdao_character_diversity_v9/DESIGN_BRIEF.md) · [验证](../qdao_character_diversity_v9/validation.json) · [视觉验收](../qdao_character_diversity_v9/visual_qa.json)', '',
       '完整人工提示词在prompts/，逐图生成和透明处理记录在records/。实际原生尺寸单独记录；4096为原路径兼容导出，不冒称原生4K。按AGENTS使用宿主内置GPT Image 2路径；工具不开放模型/质量参数开关，high是质量目标，未宣称逐次强制设置。过程母图和处理副本不保留为交付。', '',
       '旧英文文件名中的boy/girl仅作为历史资源ID；实际年龄与造型以本表和当前图片为准。', '',
       '|角色|年龄感|脸型、头发|轮廓|成品|','|---|---|---|---|---|']
    for row in assets:
        lines.append(f"|{row['name']}|{row.get('age_direction','主角')}|{row.get('face_direction','原形象')}；{row.get('hair_direction','金发带直短发')}|{row.get('silhouette_direction','原形象')}|[PNG]({row['path']})|")
    lines += ['', '```powershell', 'python -B qdao_character_diversity_v9/build_manifest.py',
              'python -B qdao_character_diversity_v9/process_character.py --raw <本轮生成PNG> --id <原stem> --reference-note <实际参考方式>', '```', '',
              '本包是静态人物，未改主角[八向动作](../character_move_8dir/README.md)，未制作这些职业人物的新动画或接入客户端。']
    (PACK / 'README.md').write_text('\n'.join(lines)+'\n', encoding='utf8')
    print('PASS: 22 redesigned v9 portraits + 2 preserved hero references; all 4096 RGBA')


if __name__ == '__main__':
    main()
