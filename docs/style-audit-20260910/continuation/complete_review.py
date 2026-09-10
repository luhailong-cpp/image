"""Attach visual judgments to current UI records and consolidate review evidence."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib,json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
def read(rel):return json.loads((OUT/rel).read_text(encoding='utf-8'))
def write(rel,obj):(OUT/rel).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
ui=read('ui/inventory.json')
now=datetime.now(timezone.utc).isoformat()
for r in ui['records']:
    n=int(r['id'][1:]); name=Path(r['path']).stem
    r['reviewed_at_utc']=now
    r['review_basis']='direct_contact_sheet' if r['id']==r['representative'] else 'identical_decoded_pixels_to_reviewed_representative'
    r['verdict']='style_compatible'
    r['reason']='当前原图经联系表查看，控件用途与玉绿/米白/暖金体系连贯；不等同全部边缘或运行时拉伸验收。'
    if n<=18 or n==20 or (40<=n<=98 and not any(x in name for x in ['badge','dot','stroke'])) or 144<=n<=157:
        r['verdict']='style_remaster'
        r['reason']='旧玉石流纹和凸起云头仍显著，主按钮/列表/页签/搜索的形态区分不足；应从按用途设计的无字母件统一，再同步派生。'
    if n in [19,21,38,39,100]:
        r['verdict']='style_refinement'
        r['reason']='颜色主题相关，但局部边饰、金属体积或源件拉伸感比指定参考厚重；按新母件统一材质与比例。'
    if 22<=n<=31 or (40<=n<=98 and 'badge' in name) or 101<=n<=112:
        r['verdict']='style_refinement'
        r['reason']='功能徽标仍是较亮青翠颗粒玉底、较厚硬亮金环，较参考更像独立另一套皮肤；符号内容可保留。'
    if n in [115,118,122,124,125,130]:
        r['verdict']='cutout_texture_repair'
        r['reason']='画法方向接近参考，但无字中心可辨矩形补纹、水平色带或直切接线；恢复连续底纹再验收。'
    if n==143:
        r['verdict']='cutout_border_repair'
        r['reason']='头像框左边大段缺失，上沿断续，残点可见；不能作完整四边头像框交付。'
    if n==158:
        r['verdict']='technical_text_layer'
        r['reason']='纯HUD动态文字导出，按文字层用途保留；不因缺少皮肤判风格不合。'
    if n>=159:
        r['verdict']='draft_style_compatible_pending_export'
        r['reason']='v10当前源件采用安静深玉/米白底、柔金边与局部桂花/流苏/月纹，较旧件更接近参考；仍是源稿或试切，未据此认定正式158资源已替换。'
        if '.tassel-' in name or '.stamp-' in name or '.body' in name:
            r['reason']+='该件是装饰/主体拆分中间件，单独截断处须在重新拼合时判断，不能单看碎片当损坏。'
        if '/source/' in r['path']:
            r['reason']+='洋红底是待抠图来源，不是正式透明成品。'
ui['reviewed_at_utc']=now
ui['verdict_counts']=dict(Counter(r['verdict'] for r in ui['records']))
ui['visual_review_complete_for_listed_contacts']=True
write('ui/review.json',ui)

groups={'ui':ui['records'],'icons':read('icons/review.json')['records'],'edges':read('edges/review.json')['records'],
        'roster':list(read('review-roster.json')['files'].values()),'maps':list(read('review-maps.json')['files'].values())}
snap=read('snapshot.json');snapshot={r['path']:r for r in snap['records']}
coverage={};errors=[]
late_updates={r['path']:r for r in read('ui/end-changes.json')}
for group,rows in groups.items():
    for r in rows:
        p=r['path'];sha=r.get('sha256') or r.get('snapshot_sha256')
        assert sha,p
        assert sha==snapshot[p]['sha256'],f'review not on snapshot: {p}'
        c=coverage.setdefault(p,{'path':p,'sha256':sha,'review_groups':[]})
        assert c['sha256']==sha
        c['review_groups'].append(group)
for p,r in coverage.items():
    r['sha256_at_validation']=hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
    expected=r['sha256']
    if p in late_updates:
        expected=late_updates[p]['sha256']
        r['latest_reviewed_sha256']=expected
        r['latest_review_evidence']=late_updates[p]
        r['latest_review_observation']='收尾更新版本已直接查看：深玉/米白/柔金与局部桂花流苏仍符合新方向，拆分主体和挂穗仍作为制作中间件，未当正式重切通过。'
    if r['sha256_at_validation']!=expected:errors.append(p)
new={r['path'] for r in snap['new_or_changed']}
missing_new=sorted(new-coverage.keys())
result={'generated_utc':now,'snapshot_cutoff_utc':snap['completed_utc'],'snapshot_visual_paths':len(snapshot),
        'review_unique_paths':len(coverage),'group_record_counts':{g:len(rs) for g,rs in groups.items()},
        'new_paths_covered':len(new)-len(missing_new),'new_paths_without_visual_review':missing_new,
        'evidence_changed_after_review':errors,'late_updated_paths_re_reviewed':sorted(late_updates),'source_art_modified':False,'records':list(coverage.values())}
write('coverage.json',result)
assert not errors and not missing_new

report='''# 全文件夹风格补查 · 2026-09-10

**上次留下的逐件风格与边缘复核已补完。旧UI问题仍在；新v10原画方向已接近参考，但不能把新源稿算作旧切片已替换。**

本轮固定快照：2026-09-10 10:12:46 UTC，共 **3,245条视觉路径**；相对前次3,219条，新增26、修改0、缺失0。包含备份和过程图，排除Git/依赖/审查输出。对比仍依据[指定风格原图](../../../docs/references/ui-style-20260910.png)和[UI规范第2节](../../../qdao_ui_redesign_v5/UI_SPEC.md)。

## 本轮补完的范围

| 范围 | 实际视觉覆盖 | 结论 |
|---|---|---|
| 正式UI合同 | 158条PNG路径；相同解码像素关联后120个独立画面，8页全部实看 | 旧云头/玉石流纹仍需重制；属性切片的拼补和断边仍存在。 |
| v10新增源稿/试切 | 快照内17条，包含3张母图和14个试切/拆分件 | 深玉底、米白纸面、柔金边和少量桂花/流苏/月纹更接近参考。未替换正式158条资源。 |
| 正式物件 | 124枚全部看图；4张补做原尺寸抽查 | 主体画法同族，可保留；2张确认残边，见下表。 |
| 功能徽标 | 11条路径，10种不同画面 | 青翠颗粒玉底、厚亮金环需统一；leaf与peach_spirit是同SHA桃子别名。 |
| 正式动作 | 32帧全部轮廓＋每帧独立浅/深底发梢放大 | 原画风格可保留；每帧已分别确认品红细边。 |
| 正式宠物 | 4张全图＋各自局部边缘放大 | 风格可保留，只有低优先级细边清理；保留九尾狐正常淡紫毛。 |
| v11人物制作稿 | 8张源图，含4立绘、52个动作格 | 25/26/28基本匹配；27比例偏长，旧斜表有方向重复及切格风险。 |
| 天墉新增稿 | 2张地图风格稿＋1份参考副本 | 玉绿暖金stylematch稿更贴近基准；均未作为生产地图接入。 |

去掉跨组重复后，本轮有 **346条唯一图像路径**得到新的视觉记录。26条新增路径全部覆盖。收尾时7个v10试切件再次更新，也已补看并分别记录新SHA，见[最后版本对照](ui/end-changes.jpg)。正式UI的38个像素一致副本通过逐件像素哈希关联到已实看的代表图；没有用统计值代替风格判断。此前未变来源的审查仍见[上次报告](../README.md)。

## 仍需处理的具体位置

| 类别 | 位置 | 建议 |
|---|---|---|
| UI材质与造型 | 旧通用组件、exact、登录原子件/分层、HUD；10种功能徽标 | 用v10同风格母件继续重切同步，主按钮、列表、页签与输入框分别保持用途层级，不能只压暗旧图。 |
| 属性切片纹理 | `button_primary`、`title_plate`、`tab_horizontal`、`tab_vertical_normal/selected`、`step_plate` | 去字填补仍能辨认；修连续底纹后按原尺寸/拉伸尺寸重组检查。 |
| 属性框体 | `portrait_frame.png` | 左边缺失、上边断续，需完整重切。 |
| 动作边缘 | `character_move_8dir/` 32帧各自发梢 | 保留道童原画，定向清理已确认的品红边；每帧证据见[边缘索引](edges/README.md)。 |
| 物件边缘 | `17_han_zhongli_palm_leaf_fan.png`、`004_golden_cudgel.png` | 前者圆框/下方绿穗、后者圆框有洋红细边；[原尺寸证据](icons/native-checks.jpg)。不据此宣称全部124都有残边。 |
| 人物比例 | v11 `27_ink_kite_ranger` | 窄脸/高马尾/轻瘦身份保留；躯干腿部收短、减少硬切阴影，回到本批2.2–2.8头身目标。 |
| 动作源格 | v11 25的cardinal、27的旧diagonal | 主体接近/跨越等分行界，旧斜表前后斜向有重复；SW补表只解决对应方向输入，仍须检查最终整套方向与裁框。 |

棕色结算窗与两版主城HUD混用问题沿用前次实看结论；本轮其SHA未变化。保存截图仅证明文件内容，不代表当前客户端画面。新v10母件的body/tassel/stamp是拆分中间件，必须重新拼合验收，不能把单独碎片直接当作断边成品。

## 对照图与明细

![v10当前源件与试切总览](ui/new_draft-01.jpg)

- [正式UI 1](ui/formal_contract-01.jpg) · [2](ui/formal_contract-02.jpg) · [3](ui/formal_contract-03.jpg) · [4](ui/formal_contract-04.jpg) · [5](ui/formal_contract-05.jpg) · [6](ui/formal_contract-06.jpg) · [7](ui/formal_contract-07.jpg) · [8](ui/formal_contract-08.jpg)；[UI逐件记录](ui/review.json)。
- [物件/徽标逐件记录](icons/review.json) · [徽标原图对比](icons/badges-01.jpg) · [动作/宠物逐件记录](edges/review.json)。
- [v11人物与母表记录](review-roster.json) · [地图风格记录](review-maps.json)。
- [固定快照清单](snapshot.json) · [去重覆盖及结束SHA核验](coverage.json)。

本轮只修改审查目录中的报告与分析图，没有清理/重画原素材，也没有替换客户端。此次已完成的是固定快照内的风格比较与列明的局部边缘检查；不是全部图片逐像素合格、动画播放验收或生产资源修复完成。快照之后另一个制作任务的新输出需用新SHA另行验收。
'''
(OUT/'README.md').write_text(report,encoding='utf-8')
entry=OUT.parent/'README.md'
text=entry.read_text(encoding='utf-8')
banner='> **后续补查已完成：**158份正式UI、124物件、32动作帧及本轮新增素材详见[最新补查结果](continuation/README.md)。下文保留07:35快照；v10“当时无图”的状态已由新报告更新。\n\n'
if banner not in text:
    title,rest=text.split('\n',1)
    entry.write_text(title+'\n\n'+banner+rest.lstrip('\n'),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False))
