"""Record the UI visual audit performed on all 21 contact pages.

Classification rules below transcribe observed asset families; they do not infer
visual style from image statistics. Original assets are read-only.
"""
from pathlib import Path
import json
import re
from collections import Counter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/style-audit-20260909'
inventory = json.loads((OUT/'inventory.json').read_text(encoding='utf-8'))
representatives = [r for r in inventory['records'] if r['owner']=='ui' and r['representative']==r['id']]

def result(r, verdict, reason, action, tags=()):
    return dict(id=r['id'], verdict=verdict, reason=reason, action=action, issue_tags=list(tags))

records=[]
for r in representatives:
    p=r['path']; name=Path(p).stem
    if r['review_type']=='svg_code':
        if 'labels' in name:
            records.append(result(r,'technical','已检查 SVG 源码：独立原生文字层；HUD 对应 PNG 已实看。文字层不应按缺图、空白背景或画风不完整判错。','保留文字分层；随组件重新合成后检查排版。'))
        else:
            records.append(result(r,'technical','已检查 SVG 源码：嵌入 PNG 后组合或九宫格摆放，属于已实看的同名总览/HUD或登录图层的构建来源，未另外独立渲染本 SVG。其组件材质问题与已实看 PNG 相同。','随修订后的组件重新构建；不要把嵌入位图 SVG 当作可无限放大的独立矢量美术。',('inherits_ui_skin','svg_source_inspection')))
        continue
    if '/qstyle_redrawn_600x600/' in p:
        if '/fairygui_atlas/' in p:
            records.append(result(r,'technical','124 件正式物件的排布图集；已实看图集和各独立图标。留空与棋盘底属于图集/透明预览用途。','保留；若后续改单件，再同步图集。'))
        else:
            records.append(result(r,'match','逐件联系表实看：深玉绿底盘、米白与暖金、少量红穗，物件轮廓清楚，材质以手绘明暗表达；与道童葫芦及主城装饰一致。物件徽章用途允许局部较多金饰。','保留现有正式物件，不因金边或细节多而整体重绘。'))
        continue
    if '/qc/' in p or 'overview' in name:
        records.append(result(r,'technical','组件或分层审查总览；各独立内容已在本次联系表逐项观察。总览含不同状态和技术留白，不能当作完整游戏页面评价。','保留总览；组件修正后统一重建这些检视图。',('inherits_ui_skin',)))
        continue
    if name=='ui-skins-native':
        records.append(result(r,'deviates','母图绿条采用明亮玉石高光和大理石状流纹，米白/灰条沿用同一云纹胶囊端帽；相较确认选角参考的深绿低反光面、细框与安静留白，材质及控件形状已偏离。','先以确认参考重定各用途母皮肤；压低玉石反光与流纹对比，恢复页签、列表、输入框、卡片、主按钮的不同结构。',('glossy_jade','role_shape_reuse')))
        continue
    if name=='ui-emblems-native' or 'badges_sheet' in name:
        records.append(result(r,'minor','十枚功能徽标的符号、玉金配色和圆润轮廓延续道家主题；绿色反光和奶油状云团较确认参考及正式物件更亮更光滑，属轻微材质差异。','保留符号与布局，若统一 UI 母图时一并收敛高光和翠绿底色即可。',('badge_material',)))
        continue
    if '/hud/' in p:
        if 'labels' in name:
            records.append(result(r,'technical','独立透明中文标签层；已观察战斗、观战、角色三行。透明留白及不带按钮为预期拆层。','保留独立文字层。'))
        else:
            records.append(result(r,'deviates','三个 HUD 按钮继承亮翠绿、明显流纹和厚云饰端帽；在主城完整预览中比建筑深玉屋顶和人物服饰更像独立玉石胶囊，材质关联较弱。','复用修正后的深玉绿主按钮，沿用现有等比摆放与独立文字。',('glossy_jade','inherits_ui_skin')))
        continue
    if 'uncropped' in name or name=='q_daoist_login_ui_lidazui_headband_v2_5120x2160':
        if 'background' in name:
            records.append(result(r,'minor','背景层保留米白留白与 Q 道童，人物身份吻合；外框亮绿纹理被拉成长条，角饰和大边框材质比确认参考更光滑。无文字及无按钮是正常分层。','保留人物与分层结构，随主框材质修正重建。',('stretched_texture','inherits_ui_skin')))
        else:
            records.append(result(r,'deviates','分层/合成图中搜索、列表、服务器卡和标题呈同一云饰横胶囊；长标题与边框的玉石纹理被明显拉长。差异来自共用皮肤，不是分层少字导致。','替换对应用途的独立皮肤并重新合成 5120/10240 兼容输出；保留真实透明通道与独立文字。',('role_shape_reuse','stretched_texture','inherits_ui_skin')))
        continue
    if '/crops/' in p:
        if name in ('jade','ivory','muted'):
            records.append(result(r,'deviates','已实看母图原生裁切：三态为同一凸起云饰横胶囊，绿/灰表面流纹及亮边较参考明显；后续多种控件的共同偏差在此已存在。','重定母皮肤用途与材质后再裁切，不靠缩小饱和度单项处理。',('glossy_jade','role_shape_reuse')))
        else:
            records.append(result(r,'minor','原生裁切的造型、题材与玉金米白配色相符；与确认参考相比，高光边、奶油云团或绿底纹理稍强。此为中间素材，不按完整组件判断留白。','保留语义和基本造型；随 UI 母图小幅收敛反光、底纹或边饰体积。',('badge_material' if name not in ('frame','panel','corner','flower','divider','recommend') else 'ornament_material',)))
        continue
    if any(t in name for t in ('bottom_bar','summary_bar')):
        records.append(result(r,'minor','米白底与金边总体吻合，但长条中央纹理和两端装饰经适配后有压扁、拉长的感觉，和参考的细线、轻底纹不同。','重新按摘要/底栏的薄条用途适配，保持端饰与纹理比例。',('stretched_texture',)))
        continue
    if any(t in name for t in ('main_frame','content_panel','cloud_corner','gold_flower','recommend_badge')) or name.endswith('_stroke') or name=='divider':
        records.append(result(r,'minor','留白、米白/暖金与云纹形状属于同一主题；局部亮绿玉质、金边反光或花心宝石偏突出，框板在大尺寸适配后纹理稍拉长。','保留结构，统一框边厚度、金色反光和纹理尺度；装饰继续限定在边角。',('ornament_material',)))
        continue
    if name in ('check','lock') or name in ('status_dot_gray','status_dot_green','status_dot_orange') or (name=='status_red' and r['size']==[32,32]):
        records.append(result(r,'match','在实际小尺寸中，金边玉绿符号清楚且与 UI 主题相容；局部高光不构成明显的全局材质冲突。','保留小状态符号，统一皮肤时校正色值即可。'))
        continue
    if 'round_badge' in name or name.startswith('icon_') or name.endswith('_badge') or name.endswith('_dot'):
        records.append(result(r,'minor','功能徽标符号、轮廓与玉金主题吻合；底盘绿色和白云团比参考及正式物件稍亮、偏光滑。它们是徽章用途，不应因厚金边判为整批风格错误。','保留符号构图；酌情压低绿底/高光与云团反差，不必整套重画。',('badge_material',)))
        continue
    if any(t in name for t in ('primary_button','tab_','top_tab','top_button','list_row','left_row','list_bg','search','server_card')):
        records.append(result(r,'deviates','实看采用重复的云饰胶囊两端与凸起边框，普通/选中/禁用仅主要改变同一皮肤；绿面亮玉流纹、灰面石纹偏强，和确认参考中深绿细框、简洁列表及轻输入底板的用途差异不符。','按主按钮、页签、列表、搜索、服务器卡分别恢复轮廓与装饰密度；统一深玉绿低反光面及较安静的米白底。',('role_shape_reuse','glossy_jade')))
        continue
    raise RuntimeError(f'Unclassified visually reviewed item: {r["id"]} {p}')

data={
    'owner':'ui',
    'reviewed_pages':[f'contacts/ui/{i:02d}.jpg' for i in range(1,22)],
    'records':records,
    'findings':[
        {'title':'UI 的材质偏差在 v7 母图阶段已经存在','severity':'high','paths':['qdao_gpt_image2_refresh_v7/ui/source/ui-skins-native.png','qdao_gpt_image2_refresh_v7/ui/derived/crops/jade.png','exact_qdao_slices/fx_top_tab_active.png','qdao_ui_redesign_v5/components/png/primary_button_normal.png','qdao_ui_redesign_v5/hud/hud_skin.png'],'evidence':'对照已确认 designs/attribute-panels/v2-painted/reference-style.png：参考 UI 深绿面反光轻，细金框和边角云饰分工清楚；v7 绿皮肤有连续亮玉反光、大理石状流纹和凸起端帽。主城完整 HUD 预览亦可见同样差异。','action':'优先修订 v7 母皮肤的深玉色、反光宽度与底纹强度，再同步衍生组件及 HUD。'},
        {'title':'不同用途的控件被同一种横胶囊造型覆盖','severity':'high','paths':['exact_qdao_slices/fx_left_row_idle_1.png','exact_qdao_slices/fx_search_box.png','exact_qdao_slices/fx_server_card_0.png','qdao_ui_redesign_v5/components/png/tab_normal.png','qdao_ui_redesign_v5/components/png/list_row_normal.png','qdao_ui_redesign_v5/components/png/search_normal.png','qdao_gpt_image2_refresh_v7/ui/prepare_assets.py'],'evidence':'21 页联系表可见页签、列表、搜索和卡片重复同一云饰端帽。prepare_assets.py main() 将这些类别统一映射到 jade/ivory/muted，并经 patch() 九宫格适配；这是来源核对事实。','action':'分别制作页签、列表、输入框、服务器卡、主按钮的皮肤。参考的列表更方正简洁、边线轻，云饰集中在主要框角与主操作，避免每行都做成主按钮。'},
        {'title':'高分辨兼容分层放大了长条纹理与边角比例问题','severity':'medium','paths':['q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_ui_uncropped_final_recomposed_10240x4320.png','q_daoist_login_ui_uncropped_highres_final_layers/q_daoist_login_background_ui_uncropped_final_5120x2160.png','q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/bottom_bar_bg_green_white.png'],'evidence':'放大实看 10240 合成图，长标题绿面和竖框纹理被拉成长带；卡片、输入与导航行均为同样的细长云饰按钮。人物与米白内容区域仍相符。大输出尺寸并未补充原生纹理细节。','action':'保留人物、透明分层、尺寸合同；先修皮肤并按目标比例适配纹理，再统一重建各兼容尺寸。'},
        {'title':'十枚功能徽标需要轻微材质统一，124 个正式物件可保留','severity':'low','paths':['qdao_gpt_image2_refresh_v7/ui/source/ui-emblems-native.png','qdao_ui_redesign_v5/components/badges_overview.png','q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/character_artifacts_redrawn_24_600x600','q_daoist_login_ui_10240_redraw_clear_final_layers/q_daoist_login_buttons_redrawn_atomic/qstyle_redrawn_600x600/west_eight_immortals_redrawn_100_600x600'],'evidence':'正式物件逐张联系表实看后，深玉底、暖金、米白、红穗及明暗笔触总体连贯；金属与玉器本身的丰富材质符合物件用途。十枚功能徽标更亮、更光滑，但符号和圆润轮廓一致。','action':'保留 124 正式物件；功能徽标只需收敛翠绿底色、镜面高光和云团白度，不建议整批推倒。'}
    ],
    'notes':[
        '基准：docs/QDAO_ART_DIRECTION.md 与已确认选角图 designs/attribute-panels/v2-painted/reference-style.png；另实看 qdao_ui_redesign_v5/source/04_main_city_hud.png 的完整背景适配。',
        '21 页全部实际显示并观察，每页最多 16 个独立像素代表；所有 representative=id 均有记录，别名由总审查按像素映射回填。并非声称每个相同像素别名均单独打开。',
        '八个 review_type=svg_code 文件已阅读源码。它们是原生文字层或嵌入 PNG 的组合源，本轮没有独立渲染，已明确按 technical 记录；同名 PNG 或相应导出图层已实际显示。',
        '部分旧 README 保留较早 SVG 原生重绘的叙述；本轮来源以当前 prepare_assets.py、v7/source-map.json 与实际嵌入 PNG 的 SVG 为准。',
        '本次只做对比记录，不修改、不重生成原始游戏素材。'
    ]
}
(OUT/'ui-findings.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'representatives':len(representatives),'recorded':len(records),'counts':dict(Counter(x['verdict'] for x in records))},ensure_ascii=False))
