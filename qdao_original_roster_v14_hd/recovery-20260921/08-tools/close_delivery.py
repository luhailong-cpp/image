"""Close the 08 handoff only after deletion logs and retained-file audit pass."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

HERE=Path(__file__).resolve().parent
RECOVERY=HERE.parent
DELIVERY=RECOVERY/'08-delivery-preview'
FINAL=DELIVERY/'revisions'/'final-v1'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
audit=read(FINAL/'runtime-audit-after-cleanup.json')
assert audit['status']=='passed' and not audit['errors']
plan=read(HERE/'cleanup-final-plan.json')
plan_sha=sha(HERE/'cleanup-final-plan.json')
logs=[json.loads(line) for line in (HERE/'cleanup-final-execution.jsonl').read_text(encoding='utf-8-sig').splitlines() if line.strip()]
deleted={r['path']:r for r in logs if r['status']=='deleted' and r['plan_sha256']==plan_sha}
summary={}
for scope in ('workspace','host'):
    rows=plan[scope]
    for row in rows:
        assert not Path(row['path']).exists(),row['path']
        assert deleted[row['path']]['sha256']==row['sha256'],row['path']
    summary[scope]={'deleted_files':len(rows),'deleted_bytes':sum(r['bytes'] for r in rows)}
extensions={'.png','.jpg','.jpeg','.gif','.webp','.bmp','.tif','.tiff','.avif'}
retained=[]
for name in ('08-generation','08-delivery-preview','08-tools'):
    for p in (RECOVERY/name).rglob('*'):
        if p.is_file() and p.suffix.lower() in extensions:
            assert p.is_relative_to(FINAL),str(p)
            retained.append(p)
assert len(retained)==202,len(retained)
inventory=read(FINAL/'production-inventory.json')
report={'schema':'qdao08-final-retention-completion-v1','completedAt':datetime.now(timezone.utc).isoformat(),
        'status':'complete','deleted':summary,'retained_game_png':136,'retained_preview_design_images':66,
        'plan_path':str(HERE/'cleanup-final-plan.json'),'plan_sha256':plan_sha,
        'execution_log_path':str(HERE/'cleanup-final-execution.jsonl'),'execution_log_sha256':sha(HERE/'cleanup-final-execution.jsonl'),
        'source_audit_sha256':sha(FINAL/'file-audit-before-cleanup.json'),
        'runtime_audit_sha256':sha(FINAL/'runtime-audit-after-cleanup.json'),
        'pending_raw_processing':[],'missing_slots':[],'client_integration':'not_performed',
        'original_sources':'Removed as authorized after source audit; historical paths and hashes are unchanged textual evidence.',
        'shared_identity_style_designs':'Outside this cleanup; still current design references.'}
(FINAL/'cleanup-completion.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
handoff=DELIVERY/'08-HANDOFF.md'
text=handoff.read_text(encoding='utf-8')
text=text.replace('素材制作、八方向离线目视验收和最终来源核验已完成；授权图片清理正在收尾。','素材制作、八方向离线目视验收、最终来源核验、授权图片清理及清理后复核全部完成。')
text=text.replace('原图、拒稿、回退和加工图片按用户2026-09-23确认规则清理；本段在执行日志确认后更新完成数量。',f'原图、拒稿、回退和加工图片按用户2026-09-23确认规则已清理：本角色工作区删除{summary["workspace"]["deleted_files"]}个图片副本，另删除真实回执精确对应的{summary["host"]["deleted_files"]}个宿主原图。最终保留136张游戏PNG与66张配套预览／设计检查图片。清理后逐图SHA、当前预览引用及16×30毫秒GIF时长复核通过；文字证据保留。')
text += '\n清理证据：[完成记录](revisions/final-v1/cleanup-completion.json)、[清理后复核](revisions/final-v1/runtime-audit-after-cleanup.json)、[清理前逐稿库存](revisions/final-v1/production-inventory.md)。全部136张素材及八方向离线验收通过，无待处理原图、无缺方向或帧号；本窗口在08停止。\n'
handoff.write_text(text,encoding='utf-8')
prompt=RECOVERY/'new-window-prompts'/'08_alchemy_prodigy_boy.md'
ptext=prompt.read_text(encoding='utf-8')
ptext=ptext.replace('2026-09-23 最新角色记录：','2026-09-28 本角色128行走＋8独立站立、八方向离线验收及授权图片清理全部完成，客户端接入未进行。最新角色记录：')
prompt.write_text(ptext,encoding='utf-8')
print(json.dumps({'status':'complete','deleted':summary,'retained_images':len(retained),'handoff':str(handoff)},ensure_ascii=False))
