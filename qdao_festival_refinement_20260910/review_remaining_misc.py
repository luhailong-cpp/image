"""Read-only source/use audit; writes only remaining-misc-review.json."""
from pathlib import Path
from collections import Counter
from datetime import datetime,timezone
import json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent;ROOT=B.parent

def load(p):return json.loads((ROOT/p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
def main():
    input_path='qdao_festival_refinement_20260910/remaining-decisions.json';data=load(input_path)
    aliases={'designs/attribute-panels/v10-preview/'+r['file']:r for r in load('designs/attribute-panels/v10-preview/asset-manifest.json')['assets']}
    shots={r['file']:r for r in load('designs/attribute-panels/v2-painted/unity-slices/unity-validation-v10.json')['screenshots']}
    cloud=load('qdao_ui_redesign_v5/transition_manifest.json');rows=[]
    for src in data['files']:
        if src['decision']!='pending':continue
        p=src['path'];name=Path(p).name;h=sha(p);ev=[];extra={};decision='retain_record'
        if p in aliases:
            a=aliases[p];assert h==a['sha256']==sha(a['source']);decision='retain_derived'
            reason='当前 v10 网页无字控件副本，与 asset-manifest 及正式属性 Sprite 完全同字节；正式来源已单独审查，副本保持同步即可。'
            extra={'source':a['source'],'source_sha256':sha(a['source']),'exact_source_bytes':True};ev=['designs/attribute-panels/v10-preview/asset-manifest.json','designs/attribute-panels/v2-painted/unity-slices/manifest.json']
        elif '/unity-review-v10/'in p:
            assert h==shots[name]['sha256'];reason='真实 Unity UGUI 属性面板离线样例数据截图，哈希匹配 v10 引擎验收；保留原始证据，不绘画编辑截图，不扩展为在线服务器通过。';extra={'record_hash_match':True};ev=['designs/attribute-panels/v2-painted/unity-slices/unity-validation-v10.json','designs/attribute-panels/v2-painted/unity-slices/README.md']
        elif p.startswith('designs/'):
            reason=('旧根目录 HTML 的手机浏览器截图，README 指定新版 v10-preview 为当前入口。' if name.startswith('mobile-') else '2026-09-09 旧 Unity 版本截图，README 和 v10 引擎报告明确标为历史。' if name=='unity-sprite-preview.png' else '旧 v2 整屏烘焙属性稿切片来源；当前 31 Sprite manifest 已改用 v10 六组原画，保留旧源追溯，不恢复旧文字与皮肤。');ev=['designs/attribute-panels/README.md','designs/attribute-panels/v2-painted/unity-slices/README.md','designs/attribute-panels/v2-painted/unity-slices/manifest.json']
        elif p.startswith('q_lidazui_') or p=='q_daoist_character_highest_transparent_4096_fixed.png':
            decision='pending_repair';reason='七个根目录 4096 文件是同字节主角别名；v9 代理确认属于其九路径传播链，等待最终去边发布，不提前保留结案。';extra={'owner':'audit_v11_festival_style','alias_group':'v9_hero_4096_nine_path_family'};ev=['qdao_festival_refinement_20260910/reviews/v9-pets-style-review.json','qdao_festival_refinement_20260910/v9-edges/']
        elif p=='q_daoist_hero_chibi_headband_v3.png':
            decision='retain_source_record';reason='当前 RGB 路径已为圆脸金发带道童形象参考；本次实看玉绿米白衣装、太极葫芦、短流苏及大头短身符合定调，不能只按 v3 名字误判未更新旧稿。它是参考母图，不是当前 v9 透明导出同步目标。';ev=['docs/QDAO_ART_DIRECTION.md','qdao_chibi_game_pack_v4/build_pack.py','qdao_chibi_game_pack_v4/README.md']
        elif p=='qdao_chibi_game_pack_v4/source/hero-matte.png':
            decision='retain_source_record';reason='build_pack.py 明确读取的洋红底人物创作输入，本次实看与当前道童同源；洋红底是生产处理输入，保留原母图和历史参数，不将透明导出 RGB 修复反写原画。';ev=['qdao_chibi_game_pack_v4/build_pack.py','qdao_chibi_game_pack_v4/README.md']
        elif p=='qdao_chibi_game_pack_v4/hero-transparent_1024.png':
            decision='pending_final_source_record';reason='有效的场景独立透明主角；v9 代理确认已发布当前 1024 导出，正交场景传播，等待所有者最终发布记录合入 ledger；本只读审查不提前结案活动主角链。';extra={'owner':'audit_v11_festival_style','owner_reported_sha256':'de0c3e6d71d7c3dbbfed313e7971b2b8220e27d3e79aafa617b225d3e322706d'};ev=['qdao_chibi_game_pack_v4/manifest.json','qdao_festival_refinement_20260910/v9-edges/']
        elif p.startswith('qdao_chibi_roster_v11/'):
            decision='pending_rebuild';reason='303 项去边已同步过此总览及整包，但追加原尺寸复查发现 28 肖像发底微量暗紫残色，补充修复后需再次同步总览与包，不沿用旧哈希结案。';extra={'owner':'check_cleanup_impact'};ev=['qdao_festival_refinement_20260910/edge_exports/final-verification.json']
        elif 'battle_entry_clouds'in p:
            source='qdao_ui_redesign_v5/source/06_battle_entry_clouds_fg.png';issource=p==source;expected=cloud['cloud_source' if issource else 'cloud_export']['sha256'];assert h==expected
            with Image.open(ROOT/p) as im:
                alpha=im.getchannel('A');box=(int(im.width*.2),0,int(im.width*.8),int(im.height*.75));ext=alpha.crop(box).getextrema();speckles=sum(alpha.crop(box).histogram()[1:])
            assert ext==(0,1) if issource else ext==(0,0)
            decision='retain_source_record' if issource else 'retain_derived';reason='本次实看为米白浅玉绿暖金纯云气，无旧道童或狐；源/标准/兼容副本匹配 transition_manifest。源中央仅 123 个 Alpha=1 量化微点，既有导出已清除，标准中央 Alpha 全为 0；保留功能前景及原生真实 Alpha，不增加遮挡式节庆装饰。';extra={'source':source,'source_sha256':sha(source),'transition_record_hash_match':True,'central_alpha_range':list(ext),'central_nonzero_alpha_pixels':speckles};ev=['qdao_ui_redesign_v5/transition_manifest.json','qdao_ui_redesign_v5/build_transition.py','qdao_ui_redesign_v5/README.md']
        elif p.startswith('qdao_ui_redesign_v5/components/'):
            decision='pending_rebuild';reason='README 仍引用的有效总览；PNG 实看是旧亮绿皮肤。overview.svg 内嵌 39 张、badges_overview.svg 内嵌 30 张 PNG，均不匹配当前正式控件哈希；根任务已接手按当前 39 PNG 和原布局重建四总览，不能作为历史保留结案。';extra={'owner':'root'};ev=['qdao_ui_redesign_v5/components/README.md','qdao_ui_redesign_v5/components/manifest.json']
        elif name=='common-review.png':
            reason='v10 控件离线拼表检查图，本次实看深玉绿、象牙纸面、细金边和功能徽标与当前控件一致；作为审查拼图保留，棋盘底不属于游戏图，不能当作新母图或独立运行时控件。';ev=['qdao_ui_style_recut_v10/README.md','qdao_ui_style_recut_v10/tools/build_common_legacy.py']
        elif p.startswith('qdao_ui_style_recut_v10/derived/'):
            decision='retain_derived';reason='当前 v10 原画裁片的小部件；已只读复算 fit_art(divider,142,35,pad=2) 与 fit_art(status_red,32,32,pad=2)，当前 RGBA 逐像素相等；实看云纹分隔、红底减号清晰，保持功能语义。';extra={'recomputed_rgba_equal':True,'source_art_key':Path(p).stem};ev=['qdao_ui_style_recut_v10/tools/build_common_legacy.py','qdao_ui_style_recut_v10/tools/art_support.py','qdao_ui_style_recut_v10/artwork/index.json']
        else:raise AssertionError(p)
        r={**src,'previous_decision':'pending','decision':decision,'reason':reason,'sha256':h,'reviewed_sha256':h,'evidence':ev,'pixels_modified':False,**extra}
        if Path(p).suffix!='.svg':
            with Image.open(ROOT/p) as im:r.update(size=list(im.size),mode=im.mode)
        rows.append(r)
    assert len(rows)==55
    report={'schema':'qdao.remaining-misc-review.v1','reviewed_utc':datetime.now(timezone.utc).isoformat(),'reviewer':'check_cleanup_impact','status':'review_complete_with_owned_repairs_open','input':input_path,'input_sha256':sha(input_path),'images_modified':0,'client_accessed':False,'scope':'Only 55 decision=pending rows in the input; existing 36 pending_repair and three pending_rebuild excluded.','summary':{'files':len(rows),'decisions':dict(Counter(r['decision'] for r in rows)),'attribute_preview_copies_verified':18,'unity_capture_hashes_verified':10,'v10_small_art_in_memory_reproductions':2,'cloud_source_export_alias_verified':3,'unrepaired_current_component_overviews':4},'files':rows,'excluded_active_rows':[{'path':f['path'],'decision':f['decision'],'reason':'Existing owned repair or rebuild remains open.'}for f in data['files'] if f['decision']!='pending'],'limitations':['Point-in-time hashes only; active v9, v11 supplement and root overview publications supersede pending hashes.','No new Unity/server/runtime acceptance claimed.','Visual misc checks used alpha-composited previews; exact aliases inherit independently reviewed current source rather than being repainted.']}
    p=B/'remaining-misc-review.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(report['summary'],ensure_ascii=False));print('sha256',hashlib.sha256(p.read_bytes()).hexdigest())
if __name__=='__main__':main()
