"""Current-file contact sheets for visual inspection; source assets are read-only."""
from pathlib import Path
import hashlib, json, importlib.util
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
spec = importlib.util.spec_from_file_location('prior_tools', OUT.parent/'style-audit-20260909/audit_tools.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
data = json.loads((OUT/'delta.json').read_text(encoding='utf-8-sig'))
records = {r['path']:r for r in data['records']}
font = ImageFont.truetype('C:/Windows/Fonts/msyh.ttc', 19)
small = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 13)

samples = [
 ('指定风格参考', 'docs/references/ui-style-20260910.png'),
 ('旧属性暂存稿', '.work/commit-qa/01-character_2560x1080.png'),
 ('根目录 · 登录兼容图', 'q_daoist_login_clear_lidazui_headband_2560x1080.png'),
 ('八向动作 · 当前正式帧', 'character_move_8dir/east_frame_01.png'),
 ('客户端保存截图 · 结算', 'client_ui_refresh_20260908/qa/11-result-native.png'),
 ('新属性切片 · 当前总览', 'designs/attribute-panels/v2-painted/unity-slices/sprite-overview.png'),
 ('exact · 旧云头页签', 'exact_qdao_slices/fx_top_tab_active.png'),
 ('正式人物 · 更新后的竹弓少女', 'q_daoist_character_pack_4096/09_bamboo_archer_girl_transparent_4096.png'),
 ('正式人物 · 更新后的书法师', 'q_daoist_character_pack_4096/17_ghost_script_calligrapher_boy_transparent_4096.png'),
 ('旧登录原子件 · 搜索框', 'q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/search_box_with_icon.png'),
 ('旧登录分层 · 重组画面', 'q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_ui_uncropped_final_recomposed_5120x2160.png'),
 ('v6 · 历史物件母图', 'qdao_asset_refresh_v6/icons/.work/batch01/normalized-source.png'),
 ('v9 · 人物过程稿', 'qdao_character_diversity_v9/.work/09_bamboo_archer_girl_transparent_4096/single-1.png'),
 ('v4 · 当前主城预览', 'qdao_chibi_game_pack_v4/preview-main-city_2560x1080.png'),
 ('幼宠 · 云啾啾', 'qdao_chibi_pets_v1/03_yun_jiu_jiu-transparent_1254.png'),
 ('v7 · 旧 UI 母图', 'qdao_gpt_image2_refresh_v7/ui/source/ui-skins-native.png'),
 ('v7 · 物件母图', 'qdao_gpt_image2_refresh_v7/icons/source/batch01.png'),
 ('v5 · HUD 标准导出', 'qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png'),
 ('v5 · HUD source 版本', 'qdao_ui_redesign_v5/source/04_main_city_hud.png'),
 ('天墉 · 地图整体', 'tianyong_city_6x6/Previews/tianyong_city_master_preview_2048.png'),
 ('九尾狐 · 当前透明图', 'qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png'),
]
# Exposure data are copies/proof, not another creative style family.
rec = records['exact_qdao_slices/fx_top_tab_active.png']
backup = rec.get('exposure',{}).get('backup')
if backup:
    samples.append(('曝光备份 · 调整前同一页签', 'qdao_exposure_refinement_v8/'+backup))

manifest = []
for label, rel in samples:
    p = ROOT/rel
    assert p.exists(), rel
    sha = hashlib.sha256(p.read_bytes()).hexdigest()
    assert sha == records[rel]['current_sha256'], f'changed after metadata snapshot: {rel}'
    manifest.append({'label':label,'path':rel,'sha256':sha,'inspection':'current contact sheet'})

for start in range(0,len(samples),9):
    page = Image.new('RGB',(1800,1510),'#f6f0e3')
    draw = ImageDraw.Draw(page)
    draw.text((24,15),f'当前文件夹代表图对照 · {start//9+1} / {(len(samples)+8)//9} · 样张，不代表逐图验收',font=font,fill='#183e31')
    for i,(label,rel) in enumerate(samples[start:start+9]):
        x=(i%3)*600; y=55+(i//3)*480
        im = prior.open_art(ROOT/rel)
        page.paste(prior.preview(im,570,365),(x+15,y+10))
        draw.text((x+15,y+383),label,font=font,fill='#183e31')
        # Full paths remain available in the manifest; wrap on the board.
        for j in range(0,len(rel),76):
            draw.text((x+15,y+415+(j//76)*16),rel[j:j+76],font=small,fill='#595348')
    page.save(OUT/f'folders-{start//9+1:02}.jpg',quality=93)

focus = [
 ('旧页签：密集玉石流纹、凸起云头', 'exact_qdao_slices/fx_top_tab_active.png'),
 ('主按钮：中心横向色带与直切接线', 'designs/attribute-panels/v2-painted/unity-slices/png/button_primary.png'),
 ('竖页签：矩形补纹', 'designs/attribute-panels/v2-painted/unity-slices/png/tab_vertical_selected.png'),
 ('数值底板：中央补块', 'designs/attribute-panels/v2-painted/unity-slices/png/step_plate.png'),
 ('头像框：左边和上边断裂', 'designs/attribute-panels/v2-painted/unity-slices/png/portrait_frame.png'),
]
board=Image.new('RGB',(1600,1150),'#f6f0e3'); d=ImageDraw.Draw(board)
d.text((24,16),'当前切片问题实图 · 下方小件按像素放大，未修改源素材',font=font,fill='#183e31')
reference = prior.open_art(ROOT/'docs/references/ui-style-20260910.png').crop((55,65,665,915))
board.paste(prior.preview(reference,480,710),(20,70))
d.text((25,800),'参考：深玉底、纸面、柔和细金边',font=font,fill='#183e31')
for i,(label,rel) in enumerate(focus):
    x=540+(i%2)*520; y=70+(i//2)*355
    im=prior.open_art(ROOT/rel)
    bbox=im.getchannel('A').getbbox()
    if bbox: im=im.crop(bbox)
    scale=min(3,480/im.width,275/im.height)
    im=im.resize((round(im.width*scale),round(im.height*scale)),Image.Resampling.NEAREST)
    board.paste(prior.preview(im,490,280),(x,y))
    d.text((x,y+288),label,font=font,fill='#183e31')
    d.text((x,y+320),Path(rel).name,font=small,fill='#595348')
    sha=hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()
    assert sha == records[rel]['current_sha256'],rel
    manifest.append({'label':label,'path':rel,'sha256':sha,'inspection':'current pixel enlargement'})
board.save(OUT/'comparison.jpg',quality=95)
(OUT/'visual-samples.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'samples':len(samples),'focused_details':len(focus),'outputs':['folders-01.jpg','folders-02.jpg','folders-03.jpg','comparison.jpg','visual-samples.json']}))
