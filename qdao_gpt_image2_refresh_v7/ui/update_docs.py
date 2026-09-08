from pathlib import Path
repo=Path(__file__).resolve().parents[2]
def replace(rel,pairs):
    p=repo/rel;s=p.read_text('utf8')
    for old,new in pairs:s=s.replace(old,new)
    p.write_text(s,'utf8')

replace('qdao_gpt_image2_refresh_v7/ui/prepare_assets.py',[
 ("n=a['nine_slice']; im=patch(skins[key],w,h,[n[k] for k in ['left','top','right','bottom']])", "n=a['nine_slice']; borders=[n[k] for k in ['left','top','right','bottom']]\n            if category=='summary_bar': borders[0]=29\n            im=patch(skins[key],w,h,borders)"),
 ("compose_glyph(im,icons[g],gx,(h-40)/2-2,32)","compose_glyph(im,icons[g],gx,(h-40)/2-2,32)\n                if state=='selected':\n                    d=ImageDraw.Draw(im); d.line((20,h/2-13,20,h/2+13),fill='#F5DE92',width=4)\n                    d.polygon([(38,h-12),(62,h-12),(50,h-18)],fill='#EDD48B')")
])
replace('qdao_ui_redesign_v5/components/README.md',[
 ('通用 UI 控件 v5.2','通用 UI 控件 v7'),
 ('源文件是原创矢量图形，不含人物、场景或外部图片。','v7 以宿主内置 image_gen 新绘制的两张母图为美术来源；SVG 内嵌 PNG 保持便携，不依赖外部图片路径。母图原生均为 1254 × 1254，裁切与高分辨率导出不冒称原生高分辨率。详见 [v7 来源记录](../../qdao_gpt_image2_refresh_v7/ui/source-map.json)。'),
 ('`svg/` 是可缩放源文件','`svg/` 是保持原 viewport 和布局契约的便携包装文件（内嵌 AI 位图，并非无限细节矢量）'),
 ('跨度很大时优先按目标尺寸重建 SVG 或调整原生布局','跨度很大时优先按目标尺寸从母图重新适配或调整原生布局'),
 ('需要 Node.js 22 或更高版本，PNG 导出需要已经安装的 `sharp`。','需要 Python（Pillow、NumPy）及 Node.js 22 或更高版本，PNG 导出需要已经安装的 `sharp`。先在仓库根执行 `python qdao_gpt_image2_refresh_v7/ui/prepare_assets.py` 生成固定尺寸皮肤，再运行本构建器。')
])
replace('qdao_ui_redesign_v5/hud/README.md',[
 ('作为不可变背景','作为本次组合的背景来源'),
 ('没有重绘场景、改动人物或增加未确认功能。','v7 背景、人物和按钮均取自本轮新 AI 美术；三个入口的位置和独立文字层保留。组合步骤本身不再修改背景来源像素。')
])
replace('exact_qdao_slices/README.md',[
 ('未生成额外过程 PNG。','v7 母图和可复现中间图保存在 [v7 UI](../qdao_gpt_image2_refresh_v7/ui/README.md)。'),
 ('均为无字原生几何。','均为无动态文字的便携 SVG 包装，内嵌本轮 image_gen 新绘制并适配的 PNG。'),
 ('在仓库根目录运行（Node 22+，已有 Sharp）：','先运行 `python qdao_gpt_image2_refresh_v7/ui/prepare_assets.py` 裁切本轮母图，再在仓库根目录运行（Node 22+，已有 Sharp）：'),
 ('v5 圆徽标与花饰 SVG 是重建依赖。','本轮 source-map 与 derived/legacy 固定尺寸 AI 皮肤是重建依赖；SVG 内的位图不是原生矢量几何。')
])
replace('q_daoist_login_ui_uncropped_highres_final_layers/README_NATIVE_Q5.md',[
 ('v5 已完成的五张标准画面没有重绘或覆盖。','v7 重绘包含这些旧路径；v5 标准画面由全库任务独立更新。'),
 ('各三张分层','各三张分层'),
 ('按 2 倍与 4 倍绘制矢量','按 2 倍与 4 倍合成 AI 皮肤与独立文字'),
 ('框板和控件是原生 SVG','框板和控件是新 AI 母图的便携 SVG 位图包装'),
 ('所有临时检查图仅在内存中查看，本批没有添加过程 PNG。','本轮母图、裁切来源和 QC 总览保存在 v7/ui；每张旧/新哈希与实际原生尺寸单独记录。')
])
replace('exact_qdao_slices/build_native_q5.mjs',[("version:'native-q5.2'","version:'gpt-image2-q7'"),("date:'2026-09-06'","date:'2026-09-07'")])
replace('q_daoist_login_ui_uncropped_highres_final_layers/native_q5/build_layers.mjs',[
 ("version:'native-q5.2'","version:'gpt-image2-q7'"),("date:'2026-09-06'","date:'2026-09-07'"),
 ('Transparent independently drawn native control skins','Transparent newly AI-painted fixed-contract control skins'),
 ('Existing 1024px true-alpha Q hero','New v7 1024px true-alpha Q hero'),
 ('Existing main-city background','New v7 main-city background')
])
print('v7 artwork provenance and preserved UI contracts documented.')
