from pathlib import Path
import json,hashlib,shutil,datetime
root=Path(r'E:\work\image\qdao_chibi_roster_v12');site=root/'review/site';e=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\23-25-current-code');now=datetime.datetime.now(datetime.timezone.utc).isoformat()
s=json.loads((e/'summary.json').read_text());snap=json.loads((e/'input-snapshot.json').read_text());assert s['status']=='passed';assert len(snap['matchingCSharpFiles'])==360
s['validation_scope']={'code':'current saved main project, all360 C# files matched at test start','art':'23/24/25,81 PNGs and appearance.json each,246 files matched at test start','earlier_guild_compile_failure':'resolved in current saved inputs; historical attempt retained'}
s['visual_runtime_review']={'status':'passed','newly_viewed_image':'tianyong-23_lantern_courier.png','reviewed_utc':now}
(e/'summary.json').write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for cid in s['characterIds']:
 c=root/'candidate-stable-body'/cid;f=c/'client-integration.json';rec=json.loads(f.read_text()) if f.exists() else {}
 rec.update(status='published_and_verified',verified_utc=now,target_project=r'E:\work\mmorpg-client',source_manifest_sha256=hashlib.sha256((c/'manifest.json').read_bytes()).hexdigest(),png_count=81,alignment_version=3,runtime_evidence=str(e/'summary.json'),editmode_passed=127,playmode_passed=8,validation_scope=s['validation_scope'])
 f.write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=root/'candidate-stable-body/23_lantern_courier';d=site/'assets/v12'/c.name;b=site/'assets/pre-natural'/c.name
if d.exists() and not b.exists():shutil.copytree(d,b)
for f in json.loads((c/'manifest.json').read_text())['files']:
 if f['path'].endswith('.png'):
  dest=d/f['path'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(c/f['path'],dest);assert hashlib.sha256(dest.read_bytes()).hexdigest()==f['sha256']
p=site/'index.html';t=p.read_text(encoding='utf-8').replace('吕洞宾、狮鼓护卫完整八方向修正已接入游戏项目','吕洞宾、狮鼓护卫、灯穗小使完整八方向修正已接入游戏项目').replace('当前游戏 24 吕洞宾、25 狮鼓护卫、26 桂香药婆、29 何仙姑、30 韩湘子接入 V12；其中本轮自然步态修正已完成 24、25。','当前游戏 23、24、25、26、29、30 接入 V12；其中本轮自然步态修正已完成灯穗小使、吕洞宾、狮鼓护卫。').replace("name:'灯穗小使',exported:true,integrated:false","name:'灯穗小使',exported:true,integrated:true");p.write_text(t,encoding='utf-8')
p=root/'README.md';t=p.read_text(encoding='utf-8')
t=t.replace('游戏当前实际接入V12的有24吕洞宾、25狮鼓护卫、26桂香药婆、29何仙姑、30韩湘子；23灯穗小使、27墨鸢游侠、28月兔机关师仍使用同ID的V11。','游戏当前实际接入V12的有23灯穗小使、24吕洞宾、25狮鼓护卫、26桂香药婆、29何仙姑、30韩湘子；27墨鸢游侠、28月兔机关师仍使用同ID的V11。')
if '23/24/25 当前代码联合回归' not in t:t+='\n\n## 23/24/25 当前代码联合回归\n\n2026-09-14 13:13 UTC，23灯穗小使、24吕洞宾、25狮鼓护卫已完成本轮修正并接入。先前公会枚举缺失已由当前工程补齐；本次360个C#与246个人物资源文件在启动前逐一匹配，127/127 EditMode、8/8 PlayMode通过。独立副本运行，不操作用户已打开的Unity场景。证据：'+str(e/'summary.json')+'。其他五位仍在本轮制作/验收中。\n'
p.write_text(t,encoding='utf-8')
print('Recorded current saved-code verification for23/24/25; updated23 preview')

