"""Report actual original-roster asset and installation progress; creates no artwork."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
FORMAL=Path('E:/work/mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV13')
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 try: return json.loads(p.read_text(encoding='utf-8-sig'))
 except (OSError,ValueError): return {}
inv=read(ROOT/'inventory.json');rows=[]
for c in inv['characters']:
 p=ROOT/'candidate'/c['character_id'];m=read(p/'manifest.json');v=read(p/'validation.json');q=read(p/'qc.json');mp=p/'manifest.json'
 accepted=all(x.get('status')=='passed' for x in (m,v,q)) and mp.exists() and v.get('manifest_sha256')==sha(mp)
 f=FORMAL/c['character_id']/'manifest.json';installed=accepted and f.exists() and sha(f)==sha(mp)
 rows.append({'id':c['character_id'],'name':c['name'],'restored_baseline_record':c['matches_git_manifest'],'walk_frames':sum((p/'walk'/d/f'{n:02}.png').exists() for d in ['N','NE','E','SE','S','SW','W','NW'] for n in range(1,17)),'independent_idles':sum((p/'idle'/f'{d}.png').exists() for d in ['N','NE','E','SE','S','SW','W','NW']),'source_and_visual_accepted':accepted,'installed_matching_accepted_manifest':installed})
status={'updated_utc':datetime.now(timezone.utc).isoformat(),'source_commit':inv['source_commit'],'characters':rows,'total':len(rows),'accepted':sum(r['source_and_visual_accepted'] for r in rows),'installed':sum(r['installed_matching_accepted_manifest'] for r in rows),'timing':{'frame_ms':30,'frames_per_direction':16,'cycle_ms':480}}
(ROOT/'PROGRESS.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 原版角色 16 帧制作进度','',f"更新：{status['updated_utc']}",'',f"原版角色共 {len(rows)} 位，素材验收完成 {status['accepted']} 位，正式游戏资源接入 {status['installed']} 位。",'',f"原图已按提交 {inv['source_commit']} 恢复；新动画独立保存在 V13。目标为八方向各 16 帧、每帧 30 毫秒、循环 480 毫秒。",'', '| 角色 | 已切行走帧 /128 | 独立站立 /8 | 素材验收 | 正式游戏接入 |','|---|---:|---:|---|---|']
for r in rows:
 lines.append(f"| {r['id'][:2]} {r['name']} | {r['walk_frames']} | {r['independent_idles']} | {'通过' if r['source_and_visual_accepted'] else '进行中' if r['walk_frames'] or r['independent_idles'] else '待制作'} | {'已接入' if r['installed_matching_accepted_manifest'] else '待接入'} |")
lines+=['','素材验收同时核对最终 manifest、QC 和源图重建结果。游戏接入计数要求正式目录与通过验收的 manifest 哈希一致。实际 Unity 运行记录位于 runtime-validation，各轮输入快照标明其测试的素材版本。','','[原版形象总览](old-style-overview.jpg) · [逐文件恢复记录](restoration.json) · [23 位角色清单](inventory.json)','']
(ROOT/'PROGRESS.md').write_text('\n'.join(lines),encoding='utf-8');print(json.dumps({k:status[k] for k in ['total','accepted','installed']}))
