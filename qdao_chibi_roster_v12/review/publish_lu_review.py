from pathlib import Path
import json,shutil,hashlib
root=Path(r'E:\work\image\qdao_chibi_roster_v12');site=root/'review/site';character=root/'candidate-stable-body/24_lu_dongbin'
previous=site/'assets/pre-natural/24_lu_dongbin'
if not previous.exists():shutil.copytree(site/'assets/v12/24_lu_dongbin',previous)
m=json.loads((character/'manifest.json').read_text());records=[]
for item in m['files']:
    rel=item['path']
    if not rel.endswith('.png'):continue
    src=character/rel;dest=site/'assets/v12/24_lu_dongbin'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dest)
    if rel.startswith('idle/') or rel.startswith('walk/') and not rel.endswith('strip.png'):
        preview=site/'sample'/rel;preview.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,preview)
        assert hashlib.sha256(preview.read_bytes()).hexdigest()==item['sha256'];records.append({'path':rel,'sha256':item['sha256']})
assert len(records)==72
p=site/'sample.html';t=p.read_text(encoding='utf-8-sig').replace('assets/v12/24_lu_dongbin/','assets/pre-natural/24_lu_dongbin/').replace('尚未导入游戏','已接入游戏项目').replace('尚未接入游戏','已接入游戏项目').replace('这次完整修正候选','本次修正 · 已接入').replace('修正候选','本次修正').replace('完整八方向候选','完整八方向修正版本').replace('当前候选原图','当前帧原图').replace('候选 ·','修正版本 ·')
p.write_text(t,encoding='utf-8')
p=site/'index.html';t=p.read_text(encoding='utf-8-sig').replace('此页用于核对现有素材；批量制作与发布暂停；正在单独修正吕洞宾自然走路样板，候选图不代表最终认可。','吕洞宾完整八方向修正已接入游戏项目；其他角色仍逐项修正，候选图不代表整批完成。');p.write_text(t,encoding='utf-8')
p=root/'review/verify_review_pages.cjs';t=p.read_text(encoding='utf-8-sig').replace('/assets/v12/24_lu_dongbin/idle/','/assets/pre-natural/24_lu_dongbin/idle/');p.write_text(t,encoding='utf-8')
(site/'sample/current-export.json').write_text(json.dumps({'character':'24_lu_dongbin','status':'imported_into_game_project','frames':records},indent=2),encoding='utf-8')
print('Updated72 preview PNGs and current index assets; previous art preserved separately for comparison')
