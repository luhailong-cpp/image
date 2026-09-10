"""Assemble a review artifact from human visual judgments, retaining exact file provenance."""
from pathlib import Path
from collections import Counter
import json, html, os
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads((OUT/p).read_text(encoding='utf-8'))
inv=read('inventory.json');sup=read('supplement.json');rev=read('revisions.json')
names=['client_designs','ui','actors','scenes','supplement','supplement-extra']
reviews=[read(f'{name}-findings.json') for name in names]
judgments={}; reviewed_pages=set()
for review in reviews:
    reviewed_pages.update(review.get('reviewed_pages',[]))
    for row in review['records']:
        if row['id'] in judgments:raise RuntimeError('Duplicate original judgment '+row['id'])
        judgments[row['id']]=row
original=inv['records']+sup['records'];lookup={r['id']:r for r in original}
records=[];unreviewed=[]
for row in original:
    r=dict(row);rid=r['representative'];a=judgments.get(rid)
    if a is None:unreviewed.append(r['id']);continue
    r.update({k:v for k,v in a.items() if k!='id'})
    r['reviewed_via']=rid
    rep=lookup[rid]
    r['contact_page']=r.get('contact_page',rep.get('contact_page'))
    r['thumbnail']=f'thumbs/{rid}.jpg' if (OUT/'thumbs'/f'{rid}.jpg').exists() else None
    records.append(r)
assert not unreviewed,unreviewed
index={r['id']:r for r in records}
revision_judgments={}
resolved=[]
for name in ['revision-client-findings.json','revision-actors-findings.json']:
    review=read(name); reviewed_pages.update(review.get('reviewed_pages',[]));resolved+=review.get('resolved_ids',[])
    for a in review['records']:revision_judgments[a['id']]=a
for r in rev['records']:
    assert r['id'] in revision_judgments,('missing revision review',r['id'])
    a=revision_judgments[r['id']];target=index[r['id']]
    target['previous_review']={k:target[k] for k in ['sha256','verdict','reason','action','thumbnail']}
    target.update(r);target.update({k:v for k,v in a.items() if k!='id'});target['reviewed_via']=r['id']
for r in records:
    if r['verdict']=='technical' and 'chroma_fringe' in r.get('issue_tags',[]):r['verdict']='quality'
labels={'match':'匹配，可保留','minor':'局部需统一','deviates':'明显偏离','technical':'技术／审查用图','quality':'切图质量需复核','historical':'历史／过程／参考','uncertain':'待核验'}
counts=Counter(r['verdict'] for r in records)
topcounts=Counter(r['top_folder'] for r in records)
folders=[]
for base,dirs,files in os.walk(ROOT):
    dirs[:]=sorted(x for x in dirs if x not in {'.git','node_modules','.venv','venv','__pycache__'} and Path(base,x)!=OUT)
    rel=Path(base).relative_to(ROOT).as_posix()
    folders.append({'path':rel,'reviewed_visual_files':sum(r['folder']==rel for r in records)})
summary={'file_count':len(records),'initial_files':len(inv['records']),'added_files':len(sup['records']),'rechecked_changed_files':len(rev['records']),'contact_pages_reviewed':len(reviewed_pages),'verdict_counts':dict(counts),'top_folder_counts':dict(sorted(topcounts.items())),'scope_cutoff_utc':sup['snapshot_utc'],'revisions_captured_utc':rev['captured_utc'],'generated_utc':datetime.now(timezone.utc).isoformat(),'all_listed_files_have_judgment':True,'resolved_during_audit':resolved,'note':'This is a frozen read-only review snapshot. Other tasks continued adding/replacing art during review. Later changes are outside this snapshot. No original art was modified by this audit.'}
result={'summary':summary,'reference_paths':['designs/attribute-panels/v2-painted/reference-style.png','docs/QDAO_ART_DIRECTION.md','docs/WUXING_QITAN_HANDOFF.md'],'records':records,'folders':folders,'reviewed_pages':sorted(reviewed_pages)}
(OUT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
path_by_id={r['id']:r['path'] for r in records}
def link(path,label=None):return f'[{label or path}](../../{path})'
def ridlink(rid):return link(path_by_id[rid])
md=['# 五行奇谈 · 全文件夹美术对比','',f'已对照 **{len(records):,} 个视觉文件**，包括正式素材、切片、来源母图、历史备份、隐藏暂存图和 SVG。已实际查看 **{len(reviewed_pages)} 页联系表**，对主要问题放大复核；相同像素副本通过哈希关联，8 个复杂 SVG 另核对源码和同名导出。','',
'主要偏差集中于旧 UI 控件及派生整屏；人物、宠物和物件大部分仍在同一美术家族。新属性切片方向更接近已确认稿，但局部去字纹理仍需精修。',
'',f'**快照范围：**文件集合截至 {sup["snapshot_utc"]}；期间变化的 {len(rev["records"])} 个原路径复核于 {rev["captured_utc"]}。其他任务仍在新增、覆盖素材，本文对每件记录被审阅的 SHA-256；快照之后的改动不自动继承结论。本次只生成审查文件，没有修改原素材。','',
'[逐文件筛选查看](index.html) · [完整记录与哈希](results.json) · [初始来源清单](inventory.json) · [新增文件清单](supplement.json) · [变动复核](revisions.json)','',
'## 判断基准','',link('designs/attribute-panels/v2-painted/reference-style.png','用户最近提供的选角风格参考')+' 为 UI 首要基准：深玉绿、米白纸面、细暖金边、局部云饰，表面安静、手绘层次柔和。人物与场景结合项目定调，保留 Q 比例、道家元素和清晰大色块。职业颜色、宠物物种体态、地图俯视用途不直接等同于风格错误。','',
'部分带 v1/v5 名字的旧路径已被 v7 覆盖，文件名和旧文档的“保留不变”不能证明它还是当初确认的图。真正参考文件与当前交付必须分开。','',
'## 优先修正','',
'### 1. 旧横条 UI：母图材质和控件造型偏离','',
'亮绿玉石流纹、凸起金色云纹端帽被反复用在按钮、页签、列表、搜索框和服务器卡片上，较参考更亮、更厚、更像同一种胶囊按钮。根源在 v7 母图及映射；重新裁切同一母图不能恢复原稿区别。','',
'涉及 `exact_qdao_slices/`、v5 `components/` 与 `hud/`、v7 `ui/`、旧登录原子与分层、客户端 `prepared/UI/`，以及旧属性预览的复制资源。','',
'代表：'+ridlink('A0198')+'、'+ridlink('A0192')+'、'+ridlink('A0281')+'。来源证据：'+link('qdao_gpt_image2_refresh_v7/ui/prepare_assets.py')+'、'+link('qdao_gpt_image2_refresh_v7/ui/source-map.json')+'。','',
'建议按主按钮、次按钮、页签、列表、输入框和卡片分别建立无字母件，再按原尺寸、透明度及九宫格约定统一派生。','',
'### 2. 结算与 HUD：存在另一套皮肤和版本混用','',
ridlink('A0291')+' 当前仍为大面积深棕木纹面板；按钮已更新成绿云饰，但主面板尚未接近米白纸面与深玉标题。','',
link('qdao_ui_redesign_v5/04_main_city_hud_2560x1080.png')+' 与 '+link('qdao_ui_redesign_v5/source/04_main_city_hud.png')+' 是两套场景/按钮版本。需要先确定统一来源；当前 source 版仍继承亮玉流纹，确定版本后还应统一按钮材质，再重建导出。截图只证明记录中的画面，未在本轮运行实际客户端检查当前引用。','',
'### 3. 新属性切片：方向已对，剩下局部去字质量','',
ridlink('X0002')+'、'+ridlink('X0023')+'、'+ridlink('X0025')+'、'+ridlink('X0027')+'、'+ridlink('X0030')+' 可见水平色带或矩形填补，手绘底纹连续性不足；头像框 '+ridlink('X0012')+' 仍有轻微角接残点。','',
'建议局部恢复无字底纹、修齐边线。审查期间已看到关闭按钮背景块、宠物卡残线、灵玥头像取景、标题透明底等问题得到修复；新属性运行截图也已替换旧亮绿厚框，**这些已修复项不再列为当前待办**。','',
'### 4. 人物与宠物：边缘质量优先，避免把正常差异当错误','',
link('character_move_8dir/east_frame_01.png')+'、'+link('character_move_8dir/south_frame_01.png')+' 放大可见品红细边；同批 32 帧应按同一边缘处理规则复核。'+link('qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png')+' 尾毛外缘有类似残色，处理时保留本身淡紫毛色。','',
'多数职业和宠物的身份、配色与画法可保留。审查期间 11 张正式人物被 v9 差异化角色覆盖，已另按新版本复核；人物多样化属于该版本方向，不能把成熟脸、不同身形或非玉绿职业色直接归为失败。旧 `prepared` 副本和新正式人物需注意版本对应。','',
'宝宝旧整屏 '+link('designs/attribute-panels/v2-painted/02-pet-ui.png')+' 中云啾啾是成年鹤头像，与幼鹤设定不一致；新增头像切片已改为正确幼鹤，旧整屏仅需同步头像修订。','',
'## 可以保留的部分','',
'- **124 个物件图标**：深玉底、金边、米白材质、云纹和红穗整体连贯。雕刻与金属光泽符合物件用途，不建议整批重画。十枚功能徽标的符号和造型也可保留，只需轻微统一翠绿底与光泽。',
'- **多数人物和三只幼宠**：Q 比例与手绘家族一致；少量人物的硬边光影可定向精修。v7 腰挂葫芦四向候选不能直接混入手持葫芦八向正式动作。',
'- **场景与天墉地图**：场景大体保持同一家族。天墉 36 切片内部一致，较参考沉重、细碎是整组美术差异，不是每张切片失败；如调整应从母图统一处理后再切。',
'- **技术层与过程图**：透明云气、黑遮罩、纯文字 SVG、洋红背景母图、联系表有各自用途；不因缺背景或保留色键母底而判风格错误。','',
'## 文件夹覆盖','',
'以下数量包含复制路径与来源，并非需要独立重绘的工作量。逐件结论见筛选页面；历史/技术图不计作“全部待重做”。','',
'| 文件夹 | 视觉文件 | 明显偏离 | 局部需统一 |','|---|---:|---:|---:|']
for folder,n in sorted(topcounts.items()):
    rows=[r for r in records if r['top_folder']==folder]
    md.append(f'| `{folder}` | {n} | {sum(r["verdict"]=="deviates" for r in rows)} | {sum(r["verdict"]=="minor" for r in rows)} |')
empty_tops=[]
for p in ROOT.iterdir():
    if p.is_dir() and p.name not in topcounts and p.name not in {'.git'}:empty_tops.append(p.name)
md+=['','另已遍历但未发现本次范围内图片的顶层目录：'+', '.join(f'`{x}`' for x in sorted(empty_tops))+'。Git 内部对象、依赖库与本报告自己的输出不计作项目美术。','',
'## 审查范围与使用方式','',
'- 全覆盖指列入清单的文件都有人工视觉结论、同像素关联结论或技术源码结论；不是逐像素质检认证。',
'- 所有独立位图均经过联系表查看，关键项另放大；没有把尺寸/哈希检查成功当作风格验收。',
'- 动画按帧静态看风格与边缘，本轮不等同于动画连续性、引擎交互、导航或碰撞验收。',
'- 同步清单提到的若干旧客户端路径仅为本库外部引用，不能据此声称已经看到其图片或当前客户端正在使用。',
'- 每张联系表格子显示稳定编号；在筛选页搜索编号或文件名即可看到完整路径、结论和修正方向。','']
(OUT/'README.md').write_text('\n'.join(md),encoding='utf-8')

# A local, dependency-free browser for all reviewed paths. Art files remain external/read-only.
payload=json.dumps({'summary':summary,'labels':labels,'records':[{k:r.get(k) for k in ['id','path','top_folder','verdict','reason','action','issue_tags','sha256','thumbnail','review_type','reviewed_via','revision']} for r in records]},ensure_ascii=False).replace('</','<\\/')
template='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>五行奇谈 · 全库美术对比</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f3f0e7;color:#243c33;font:15px/1.6 system-ui,"Microsoft YaHei",sans-serif}header,main{max-width:1500px;margin:auto;padding:24px}header{border-bottom:1px solid #c8bc9f}h1{font-size:27px;margin:0 0 8px}p{margin:8px 0}a{color:#176448}.tools{display:flex;gap:12px;flex-wrap:wrap;position:sticky;top:0;background:#f3f0e7;padding:15px 0;z-index:2}input,select{font:inherit;padding:10px;border:1px solid #998d70;border-radius:5px;background:#fffef7;min-height:44px}input{flex:1;min-width:240px}.count{padding:10px 0;color:#65766c}table{width:100%;border-collapse:collapse;background:#fffdf6}th{text-align:left;background:#e4e5d7}td,th{padding:12px;border-bottom:1px solid #dedacb;vertical-align:top}.thumb{width:160px;height:128px;object-fit:contain;background:#e8e1d0}.path{overflow-wrap:anywhere;font-size:13px}.tag{display:inline-block;padding:3px 8px;border-radius:4px;background:#e5ebe1;font-size:13px}.deviates{background:#f3d9cd;color:#7e2e14}.minor{background:#f4e5bd;color:#65500b}.historical,.technical{background:#e9e5db;color:#62695f}small{color:#738177}details{margin:6px 0}summary{cursor:pointer}.reason{min-width:260px}button{font:inherit;padding:10px;cursor:pointer}footer{padding:20px 0;color:#647164}@media(max-width:780px){header,main{padding:16px}table,tbody,tr,td{display:block}thead{display:none}tr{padding:12px;border-bottom:2px solid #c7c6b4}td{padding:5px;border:0}.thumb{width:100%;height:170px}.reason{min-width:0}}</style>
<header><h1>五行奇谈 · 全库美术对比</h1><p>以已确认选角稿、人物与场景定调逐项比较。保留来源、旧版与复制路径，按用途判断。</p><p><a href="README.md">阅读结论与修正顺序</a> · <a href="../../designs/attribute-panels/v2-painted/reference-style.png">查看风格基准</a> · <a href="results.json">完整记录</a></p><small id="snapshot"></small></header>
<main><div class="tools"><input id="search" type="search" aria-label="搜索文件名、编号或问题" placeholder="搜索文件名、编号或问题"><select id="folder" aria-label="按文件夹筛选"><option value="">全部文件夹</option></select><select id="verdict" aria-label="按结论筛选"><option value="">全部结论</option></select></div><div class="count" id="count" role="status" aria-live="polite"></div><table><thead><tr><th>审阅图像</th><th>文件与判断</th><th>原因与建议</th></tr></thead><tbody id="rows"></tbody></table><footer>缩略图是审阅时的快照。原文件链接可能已被其他任务更新，以记录的 SHA-256 为准。本报告没有修改原素材。</footer></main>
<script id="data" type="application/json">__DATA__</script><script>
const data=JSON.parse(document.getElementById('data').textContent),rows=document.getElementById('rows'),search=document.getElementById('search'),folder=document.getElementById('folder'),verdict=document.getElementById('verdict');
document.getElementById('snapshot').textContent=`共 ${data.summary.file_count} 个路径 · ${data.summary.contact_pages_reviewed} 页联系表 · 文件集合快照 ${data.summary.scope_cutoff_utc}`;
for(const f of Object.keys(data.summary.top_folder_counts).sort()){const o=new Option(f,f);folder.add(o)}for(const [k,v] of Object.entries(data.labels))verdict.add(new Option(v,k));
function el(t,cls,txt){const e=document.createElement(t);if(cls)e.className=cls;if(txt!==undefined)e.textContent=txt;return e}
function render(){const q=search.value.toLowerCase();const selected=data.records.filter(r=>(!folder.value||r.top_folder===folder.value)&&(!verdict.value||r.verdict===verdict.value)&&(!q||[r.id,r.path,r.reason,...(r.issue_tags||[])].join(' ').toLowerCase().includes(q)));rows.replaceChildren();const frag=document.createDocumentFragment();for(const r of selected){const tr=el('tr'),imtd=el('td'),mid=el('td'),text=el('td','reason');if(r.thumbnail){const img=el('img','thumb');img.src=r.thumbnail;img.alt=r.path;img.loading='lazy';imtd.append(img)}else imtd.append(el('small','', 'SVG 源码 / 对应导出已核验'));mid.append(el('span','tag '+r.verdict,data.labels[r.verdict]));const p=el('p','path');const a=el('a','',r.id+' · '+r.path);a.href='../../'+r.path;a.target='_blank';p.append(a);mid.append(p);const de=el('details');de.append(el('summary','',r.revision?'已复核期间更新的版本':'查看来源记录'));de.append(el('small','path','SHA-256: '+r.sha256+'；依据 '+r.reviewed_via+'；'+r.review_type));mid.append(de);text.append(el('p','',r.reason),el('p','',r.action));tr.append(imtd,mid,text);frag.append(tr)}rows.append(frag);document.getElementById('count').textContent=`显示 ${selected.length} / ${data.records.length} 个文件路径；重复路径不等于独立重绘任务。`}
search.addEventListener('input',render);folder.addEventListener('change',render);verdict.addEventListener('change',render);render();</script></html>'''
(OUT/'index.html').write_text(template.replace('__DATA__',payload),encoding='utf-8')
checks={'all_listed_files_have_judgment':len(records)==len(original),'all_revisions_have_new_judgment':len(revision_judgments)==len(rev['records']),'all_contact_pages_exist':all((OUT/p).exists() for p in reviewed_pages),'all_thumbnails_exist':all(not r['thumbnail'] or (OUT/r['thumbnail']).exists() for r in records),'listed_files':len(records),'judged_files':len(records),'revisions':len(rev['records']),'reviewed_pages':len(reviewed_pages),'read_errors':[r['path'] for r in records if r['review_type']=='read_error'],'unreviewed':unreviewed,'reference_exists':(ROOT/'designs/attribute-panels/v2-painted/reference-style.png').exists()}
assert all(checks[k] for k in ['all_listed_files_have_judgment','all_revisions_have_new_judgment','all_contact_pages_exist','all_thumbnails_exist','reference_exists'])
(OUT/'coverage-validation.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'summary':summary,'validation':checks},ensure_ascii=False,indent=2))
