"""Publish the user's changed retention policy and accurate current file counts."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
ROOT=Path(__file__).resolve().parent
ART=ROOT.parent
SESSION=ART/'builtin_q64_production/resume_single_city_20260921'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt=read(ROOT/'deletion-receipt.json');assert receipt['status']=='completed'
plan=read(ROOT/'cleanup-plan-final.json')
state=read(SESSION/'session-state.json')
assert state['sourceRetention']['deletedFiles']==receipt['deletedFiles']
verification_path=sorted(ROOT.glob('verification-*.json'))[-1]
verification=read(verification_path);assert not verification['errors']
updates=[]
def update(path,content):
    before=path.read_bytes() if path.exists() else None
    data=(json.dumps(content,ensure_ascii=False,indent=2)+'\n').encode('utf-8') if isinstance(content,dict) else content.encode('utf-8')
    updates.append((path,before,data))
note='用户已明确授权删除旧原图和回退图。此要求覆盖本交接中早先的全部原图／失败版保留要求；当前仅保留最新选用图、未完区域必需小片、布局／材质设计和当前验收证据，历史来源 SHA 与文本记录保留。'
for tile in ('r08_c07','r08_c08','r08_c09'):
    d=SESSION/('next_tile_'+tile)
    p=d/'handoff-state.json';obj=read(p)
    current=list((d/'native').glob('*.png'))
    obj['historicalRetainedNativeCountBeforeCleanup']=obj['retainedNativePngCountIncludingRejected']
    obj['retainedNativePngCountIncludingRejected']=len(current)
    obj['sourceRetention']={'userAuthorizedCleanup':True,'currentSelectedPngCount':len(current),
       'rejectedOriginalPngsDeleted':True,'historicalHashesAndRecordsRetained':True,
       'cleanupReceipt':str(ROOT/'deletion-receipt.json')}
    update(p,obj)
    p=d/'HANDOFF.md';text=p.read_text(encoding='utf-8-sig')
    text=text.replace('全部旧版、请求、回执、计划和参考保留。','旧版图片已按用户授权清理；请求、回执、来源 SHA、当前计划和必要参考保留。')
    prefix=f'> 清理后更新：本目录现保留 {len(current)}/16 张选用原生小片，旧失败 PNG 已删除，下面旧数量是清理前冻结值。'+note+'\n\n'
    update(p,prefix+text)
    p=d/'plan.json';obj=read(p);changed=False
    for patch in obj['patches']:
        value=patch.get('native') or patch.get('outputFile')
        target=(d/Path(value)) if value else None
        if target and not target.exists() and str(patch.get('status','')).lower().startswith('native_saved'):
            patch['status']='needs_regeneration_after_user_authorized_cleanup'
            patch['cleanupNote']='Saved old version failed material review and was removed; select new clean-material version after real generation.'
            changed=True
    if changed:update(p,obj)

doc=ART/'主城美术详细交接-20260921.md'
body=doc.read_text(encoding='utf-8-sig')
body=body.replace('本窗口停止新增生图，保留现有来源、失败版本和检查证据。','本窗口停止新增生图；旧原图和回退图已按用户后续授权清理，最新选用图、必要设计及来源文本记录保留。')
body=body.replace('不要修改这些旧核心来迁就新图。','不要修改这些选用核心来迁就新图。')
body=body.replace('已有失败回退全部保留：','已有失败问题的文本记录保留，相关旧图片已清理：')
body=body.replace('**保留失败记录，不能把旧报告改成通过。**','**保留失败结论文本，不能把旧报告改成通过；无需保留旧失败 PNG。**')
body=body.replace('保留每张完整原生返回字节，不只留核心裁切。','制作中的选用小片保留完整返回字节，完成组装后可按用户要求清理原图；来源 SHA 和生成记录保留。')
body=body.replace('& $CityArtPython "$CityArtSession\\provenance\\audit_native_sources.py"','# 旧 audit_native_sources.py 是历史全量原图审计；删除原图后不要再把它当当前全量通过检查。')
body=body.replace('本窗口没有执行 git add、commit、push、reset 或删除。','本窗口未执行 git add、commit、push 或 reset；已按用户后续授权删除清单中的过时主城图片及过程数据。')
body=body.replace('本轮回退材料在 `SESSION/history/`、各 `native/` 的旧版、`repairs/versions/`、`audit/` 的失败记录、`provenance/` 内容寻址旁证中。旧用户缓存路径可能失效，但已有原生文件在制作目录中的完整拷贝和 SHA 可继续使用；缺缓存不能作为删除来源或重写历史的理由。','历史生成／拼接／失败结论的文本与 SHA 记录仍在原处；旧原图、候选回退版和过时检查图片已按清理清单删除。保留的选用小片可继续制作，已删除来源无法逐字节重放。不要尝试从旧 E 盘路径恢复或把删除项当作通过复验。')
prefix=('> 2026-09-22 用户清理要求已执行。'+note+' 详见[清理结果与当前检查方法](cleanup-current-assets/README.md)。'
        '原交接快照属于清理前历史，不再表示原图仍在磁盘。当前整城仍是 8／256 候选、正式验收 0。\n\n')
update(doc,prefix+body)
for p,link in ((ART/'README.md','cleanup-current-assets/README.md'),(SESSION/'README.md','../../cleanup-current-assets/README.md')):
    text=p.read_text(encoding='utf-8-sig')
    update(p,'> 2026-09-22 已按用户授权清理旧原图／回退图，最新保留范围及实际数量见[清理记录]('+link+')。此前原生累计数字是历史生成记录，不表示清理后仍保留同等数量的原图。\n\n'+text)
p=SESSION/'handoff-20260921/新窗口启动提示词.md'
text=p.read_text(encoding='utf-8-sig')
text=text.replace('8. qdao_city_tiles_4k_20260916\\主城美术详细交接-20260921.md','8. qdao_city_tiles_4k_20260916\\主城美术详细交接-20260921.md\n9. qdao_city_tiles_4k_20260916\\cleanup-current-assets\\README.md（最新清理政策与磁盘保留范围）')
text=text.replace('保留旧失败版。','旧失败图片已按用户要求清理，保留失败结论与来源 SHA。')
text=text.replace('未改原图、真实回执','制作中选用原图、真实回执')
text=text.replace('保留其他窗口改动、原始来源和回退版本；不要删除、git add、提交、推送、reset 或覆盖共享记录。','用户已授权删除旧原图和回退版本，只保留最终拟用图与必要设计。当前已完成清理，来源 SHA、文本记录与未完区域选用小片保留。继续保护其他窗口改动；不要 git add、提交、推送、reset 或覆盖共享记录。')
update(p,text)

readme=f'''# 主城美术清理结果与当前保留范围

用户已明确要求：原图和回退版本不需要保留，只保留最终拟接入游戏的图和设计。本要求覆盖旧交接的原图／失败版保留要求。

已删除 **{receipt['deletedFiles']} 个文件，{receipt['deletedBytes']/1e9:.2f} GB（{receipt['deletedBytes']/1024**3:.2f} GiB）**，没有另建图片备份。范围只限 `D:/luyuan/wuxingqitan/image/qdao_city_tiles_4k_20260916` 内清单列明的过时图像与过程数据；未删除客户端、其他素材目录或宿主缓存。

保留 {len(plan['keep'])} 个当前图像／处理资产，约 {sum(x['bytes'] for x in plan['keep'])/1e9:.2f} GB：

- 各外观当前选用 26 张 4096² 图块，其中天墉城节庆 8 张。它们仍是候选，正式验收 0。
- r08_c07 的 9 张、r08_c08 的 2 张、r08_c09 的 5 张续作小片，共 16 张，尚未组成三个完整 4K 块。
- 当前布局／材质设计、下一块引导、真实邻块上下文，以及最新局部验收所需证据图。
- 生成版本、请求、实际回执、来源 SHA、拼接记录、失败结论和脚本等文本资料；这些不会把删除的图像恢复为“仍保留”。

## 文件证据

- [保留与删除清单](cleanup-plan-final.json)：每个文件的绝对路径、字节数、删除前 SHA 与保留理由。
- [删除回执](deletion-receipt.json)／[逐文件删除日志](deleted-files.jsonl)。删除前逐个校验 SHA、边界与非符号链接；若内容已变则拒绝删除。
- [清理后核验]({verification_path.name})：保留文件 SHA 与清理前一致，{verification['retainedImagesFullyDecoded']} 张图片完整解码；26 个当前 4K 和 16 个续作小片尺寸正确。清单删除项均已不存在。

## 新窗口继续

读取[详细交接](../主城美术详细交接-20260921.md)和[启动提示词](../builtin_q64_production/resume_single_city_20260921/handoff-20260921/新窗口启动提示词.md)，仍按一城一种外观补齐 256 张。原路径不变；不要把候选改成正式成品。

`resume_single_city_20260921/refresh_session.py` 已适配明确删除的旧来源，会按当前实际保留原图计数。`tools/verify_checkpoint.py` 对当前图块与仍保留原图完整核验；已授权删除的历史来源只核对删除前 SHA 记录，逐项写 `deleted_by_user_not_reverified`，不会标为当前字节通过。总状态可能为 `CURRENT_ASSETS_CONSISTENT_WITH_RETIRED_SOURCES`，它不是完整历史来源链复验或美术验收。

旧 `provenance/audit_native_sources.py` 和清理前冻结核验面向全部历史原图，删除后不再作为当前完整来源验证入口。历史索引和 SHA 文本保留；需要重新检查画面时从当前选用图产生新的原像素证据，已删除原图不再可供重放。

此清理没有新生图、客户端发布或 git add/commit/push/reset。正式验收仍为 0，模型实际版本仍未确认。
'''
update(ROOT/'README.md',readme)

# Guard every read-modify-write. No new rollback image copies are created.
for p,before,data in updates:
    assert (p.read_bytes() if p.exists() else None)==before,'Concurrent document change: '+str(p)
for p,before,data in updates:
    assert (p.read_bytes() if p.exists() else None)==before,'Concurrent document change: '+str(p)
    p.write_bytes(data)
for p in (ART/'status.json',ART/'production_catalog.json',ART/'builtin_q64_production/current-batch.json'):
    before=p.read_bytes();obj=json.loads(before.decode('utf-8-sig'));run=obj['activeProductionRun']
    run['sourceRetention']=state['sourceRetention']
    run['latestCleanup']={'file':'cleanup-current-assets/deletion-receipt.json','sha256':sha(ROOT/'deletion-receipt.json'),
      'verification':str(verification_path.relative_to(ART)),'verificationSha256':sha(verification_path)}
    if 'latestDetailedHandoff' in run:run['latestDetailedHandoff']['documentSha256']=sha(doc)
    run['currentWindowWorkState']='handoff_ready_user_authorized_obsolete_sources_deleted'
    obj['baselineSelectionCountMeaning']='Legacy candidate/source arrays and counts are historical pre-cleanup observations. Current selected artwork and physically retained sources are in activeProductionRun/sessionState. Deleted original bytes remain unavailable; their SHA metadata is retained.'
    if p.name=='status.json':
        obj['status']='single_city_art_incomplete_handed_off_sources_cleaned_by_user'
        if 'detailedArtContinuation' in obj.get('handoff',{}):obj['handoff']['detailedArtContinuation']['documentSha256']=sha(doc)
    assert p.read_bytes()==before,'Concurrent status change: '+str(p)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'documentsUpdated':len(updates),'sharedRecordsUpdated':3,'deletedFiles':receipt['deletedFiles'],'deletedBytes':receipt['deletedBytes'],'formalAccepted':0}))
