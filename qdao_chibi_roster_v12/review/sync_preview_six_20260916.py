from pathlib import Path
import json, hashlib, shutil, datetime, re
root=Path(r'E:\work\image\qdao_chibi_roster_v12')
site=root/'review/site'
game=Path(r'E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12')
ids=['23_lantern_courier','24_lu_dongbin','25_lion_drum_guard','26_osmanthus_healer','29_he_xiangu','30_han_xiangzi']
names=['灯穗小使','吕洞宾','狮鼓护卫','桂香药婆','何仙姑','韩湘子']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
records=[]
for cid in ids:
 c=root/('candidate-natural-body' if cid=='29_he_xiangu' else 'candidate-stable-body')/cid
 m=json.loads((c/'manifest.json').read_text(encoding='utf-8'));q=json.loads((c/'qc.json').read_text(encoding='utf-8'));a=json.loads((game/cid/'appearance.json').read_text(encoding='utf-8'))
 assert q['status']=='passed' and q['visual_review']=='passed'
 assert m['alignment']['version']==3 and a['alignmentVersion']==3
 assert a['manifest_sha256']==sha(c/'manifest.json')
 files=[f for f in m['files'] if f['path'].endswith('.png')];assert len(files)==81
 for f in files:
  assert sha(c/f['path'])==f['sha256'];assert sha(game/cid/f['path'])==f['sha256']
 dest=site/'assets/v12'/cid;backup=site/'assets/pre-natural'/cid
 changed=[f for f in files if not (dest/f['path']).exists() or sha(dest/f['path'])!=f['sha256']]
 if changed:
  if dest.exists() and not backup.exists():shutil.copytree(dest,backup)
  for f in files:
   d=dest/f['path'];d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(c/f['path'],d)
 for f in files:assert sha(dest/f['path'])==f['sha256']
 records.append({'character_id':cid,'source':str(c),'manifest_sha256':sha(c/'manifest.json'),'png_count':len(files),'changed_png_count':len(changed),'site_and_game_hashes_match':True,'previous_site_backup':str(backup)})
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
report={'status':'passed','verified_utc':now,'scope':'site assets and published PNG hashes; runtime tests are separate','characters':records,'pending':['27_ink_kite_ranger','28_moon_rabbit_artificer']}
(site/'preview-source-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=site/'index.html';t=p.read_text(encoding='utf-8')
t=re.sub(r'<div class="notice">.*?</div>','<div class="notice">灯穗小使、吕洞宾、狮鼓护卫、桂香药婆、何仙姑、韩湘子已完成本轮道家 Q 版与自然步态修正并接入游戏项目。墨鸢游侠、月兔机关师仍在收尾。</div>',t,count=1)
t=re.sub(r'<p class="deployment">.*?</p>','<p class="deployment">已完成 6 / 8 位：每人八方向、每方向 8 张行走帧，另有独立站立图。新批次游戏运行验证仍在进行。</p>',t,count=1)
t=t.replace('已导出；游戏当前使用V12，造型仍待本次核对。','本轮修正已完成，游戏素材已接入 V12。').replace('现有导出，待本次核对','本轮修正已完成')
p.write_text(t,encoding='utf-8')
state='2026-09-16 当前状态：灯穗小使、年轻吕洞宾、狮鼓护卫、桂香药婆、何仙姑、韩湘子已完成本轮道家 Q 版与自然步态修正，均按对齐 v3 接入游戏。每人 64 张真实行走、8 张独立站立和 1 张肖像，含条带共 81 张 PNG。站点与已发布素材逐文件 SHA 核对一致。墨鸢游侠、月兔机关师仍在收尾。新批次的运行验证尚未完成；最近一次当前代码尝试被聚宝斋缺少 Trade 类型的编译错误拦住，保留失败证据。内部检查通过不等于用户已认可整批美术。'
current='游戏当前实际接入 V12 的有 23 灯穗小使、24 吕洞宾、25 狮鼓护卫、26 桂香药婆、29 何仙姑、30 韩湘子；27 墨鸢游侠、28 月兔机关师仍使用同 ID 的 V11。'
for filename in ['README.md','CLIENT_CONTRACT.md']:
 p=root/filename;t=p.read_text(encoding='utf-8');paras=t.split('\n\n')
 assert paras[1].startswith('2026-09-14 当前状态：')
 paras[1]=state;paras[2]=current
 t='\n\n'.join(paras)
 if filename=='README.md':
  t=t.replace('2026-09-14 13:13 UTC，23灯穗小使、24吕洞宾、25狮鼓护卫已完成本轮修正并接入。','历史记录：2026-09-14 13:13 UTC，23灯穗小使、24吕洞宾、25狮鼓护卫已完成本轮修正并接入。')
  t=t.replace('其他五位仍在本轮制作/验收中。','这是当时的三位角色回归范围；其余角色的最新状态见本文开头。')
 else:
  t=t.replace('客户端目录、世界动画器和战斗外观加载已实现版本选择与完整性回退，并已有上述四位V12接入。当前只做吕洞宾自然走路样板；其余角色保持现有版本，暂停后续批量发布。运行资源完整性门禁和内部passed标记不能替代用户对造型、步态及脸型比例的确认。','客户端目录、世界动画器和战斗外观加载已实现版本选择与完整性回退。当前逐角色完成整套美术与资源验收后发布；本轮六位已接入，另两位继续收尾。运行资源完整性门禁和内部 passed 标记不能替代用户对造型、步态及脸型比例的确认。')
 p.write_text(t,encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
