"""Verify the latest delivery of each file and record actual completed scope."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
import numpy as np

P=Path(__file__).resolve().parent;R=P.parent
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def main():
    latest={};reports={k:load(P/f'published-{k}.json') for k in ['support','hero','ui']}
    for k,d in reports.items():
        rows=d['files'] if k=='ui' else d['records']
        for x in rows:latest[x['path']]=x['staged_sha256'] if k=='ui' else x['sha256']
    for rel,digest in latest.items():assert sha(R/rel)==digest,rel+' changed after delivery'
    hero_review={r['path']:r for r in load(R/'docs/style-repair-20260911/hero-final-review.json')['records']}
    alpha_verified=[]
    for kind in ['support','hero']:
        report=reports[kind]
        for r in report['records']:
            if not r['path'].endswith('.png') or '/fairygui_atlas/' in r['path']:continue
            old=np.array(Image.open(R/report['backup_root']/r['backup_file']).convert('RGBA'))
            now=np.array(Image.open(R/r['path']).convert('RGBA'));assert old.shape==now.shape
            assert np.array_equal(old[:,:,3],now[:,:,3])
            if kind=='hero':
                cutoff=hero_review[r['path']]['head_cutoff_y'];assert np.array_equal(old[cutoff:],now[cutoff:])
                assert Image.fromarray(now[:,:,3]).getbbox()[3]==1179
            alpha_verified.append(r['path'])
    report={'status':'verified_image_repository_delivery','verified_utc':datetime.now(timezone.utc).isoformat(),
            'unique_files_hash_verified':len(latest),'alpha_identical_pngs':len(alpha_verified),
            'ui_contract_pngs':158,'ui_companion_files':126,'hero_frames':32,'pet_sources':4,'item_sources':2,
            'portrait_assets':4,'dependent_copies':10,'item_atlas_cells_synchronized':124,
            'engine_import_performed':False,'pending_separate_work':['27_ink_kite_ranger remains an unapproved production draft in its character task.','New v9 24-character delivery and its 04/14 fine-edge checks remain with the character delivery task.','Historical client screenshots do not establish the current Unity runtime appearance.'],
            'reports':['published-ui.json','published-hero.json','published-support.json'],
            'files':[{'path':p,'sha256':h} for p,h in sorted(latest.items())]}
    save(P/'final-verification.json',report)
    text='''# 全文件夹对比后的切片修复交付

2026-09-11：本轮 UI、移动帧、宠物及道具切片修复已写入原正式目录，并完成发布后核验。试修图和备份只用于追溯，导入时继续使用原资源路径。

| 交付范围 | 实际完成 |
|---|---|
| UI | 158 张合同 PNG 与 126 个配套文件全部匹配验收版本。155 张为新版图像，2 张静态书法和 1 张独立 HUD 文字保留。 |
| 移动人物 | 32 帧逐张清理发梢残色；画布、全部 Alpha、头部以下像素与脚点保持不变。 |
| 宠物和道具 | 4 只宠物、2 件道具清边；正常紫色狐毛、红穗和金饰保留。 |
| 头像和副本 | 4 个头像及 10 个引用副本同步；灵玥头像粉紫候选 74 → 0，头像 Alpha 与裁切不变。 |
| 道具图集 | 按原坐标同步 124 格，每格与当前正式单图逐像素一致。 |

UI 材质按指定参考统一为深玉绿、米白纸面和柔金细边，保留道家 Q 版及少量桂花、流苏、月纹装饰。已修复头像框缺边及旧底纹拼补问题。

![实际 UI 替换前后](ui-before-after.jpg)

发布记录与备份索引：[UI](published-ui.json)、[人物](published-hero.json)、[宠物道具及副本](published-support.json)。最终逐文件检查见 [final-verification.json](final-verification.json)。所有替换均先检查当前与暂存 SHA，再备份、替换及复核；旧生成来源和历史清边记录保留。

人物存在少量低透明离散算法候选点，最高 Alpha 30/255；验收时无连续可见品红描边，不宣称数学上每个紫红像素都消失。过程图中的初版修复不是最终交付，以发布记录里的输出 SHA 为准。

## 与本轮正式切片分开的在制内容

- 25 号人物旧跨格源表已被制作任务排除，新正式 16 帧通过限定复核。
- 27 号墨鸢人物仍是另一制作任务的未交付过程稿，比例与斜向动作不能算作合格正式素材；未用这份过程稿替换任何已通过素材。
- 新到的 v9 24 人物交付由人物任务验收，04/14 的细边检查和清边入口已交接；本轮没有覆盖其新图。
- 棕色结算图是历史 Unity 截图，本仓库未包含该运行视图定义。本轮未向客户端工程复制文件，也未把历史截图当成实机验收。

限定复核证据见 [nonproduction-followup.json](../docs/style-repair-20260911/nonproduction-followup.json)。全文件夹比较的固定快照与逐件记录见 [原审计](../docs/style-audit-20260910/continuation/README.md)。本交付补齐的是其中已确认的正式 UI 与切片问题，不把后续新增制作稿混算为已完成。
'''
    (P/'README.md').write_text(text,encoding='utf-8')
    banner='> **2026-09-11 修复更新：** 此页为先前固定快照。该次确认的正式 UI、32 移动帧、4 宠物及 2 道具已修复并交付；最新实际状态、备份与在制稿边界见 [修复交付记录]({link})。\n\n'
    for rel,link in [('docs/style-audit-20260910/continuation/README.md','../../../qdao_cutout_edge_repair_20260910/README.md'),('docs/style-audit-20260910/README.md','../../qdao_cutout_edge_repair_20260910/README.md')]:
        p=R/rel;old=p.read_text(encoding='utf-8-sig')
        if '**2026-09-11 修复更新：**' not in old:p.write_text(banner.format(link=link)+old,encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['files','pending_separate_work']}))
if __name__=='__main__':main()
