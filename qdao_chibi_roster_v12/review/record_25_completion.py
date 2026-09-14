from pathlib import Path
import json,hashlib,shutil,datetime
root=Path(r'E:\work\image\qdao_chibi_roster_v12'); now=datetime.datetime.now(datetime.timezone.utc).isoformat()
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
c=root/'candidate-stable-body/25_lion_drum_guard'
e=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\25-lion-guard')
manifest=json.loads((c/'manifest.json').read_text()); sha=hashlib.sha256((c/'manifest.json').read_bytes()).hexdigest()
assert sha=='5d90d5b04eea74bf5f780e221fc5cfb8e1de313faac344e9258a4e9b45a7b840'
scope={'code_scope':'exact previous passing 357 C# baseline; three Guild files restored only in independent clone','current_saved_project':'first attempt compilation blocked by 4 missing guild_error enum members; current source files untouched','resource_scope':'81 newly published character PNGs and appearance.json verified equal to game project'}
s=json.loads((e/'summary.json').read_text()); s.update({'validation_scope':scope,'visual_runtime_review':{'status':'passed','image':'tianyong-25_lion_drum_guard.png','reviewed_utc':now}});write(e/'summary.json',s)
write(c/'client-integration.json',{'status':'published_and_verified','verified_utc':now,'target_project':r'E:\work\mmorpg-client','source_manifest_sha256':sha,'png_count':81,'alignment_version':3,'runtime_evidence':str(e/'summary.json'),'editmode_passed':127,'playmode_passed':8,'validation_scope':scope})
site=root/'review/site'; old=site/'assets/v12'/c.name; backup=site/'assets/pre-natural'/c.name
if old.exists() and not backup.exists():shutil.copytree(old,backup)
for f in manifest['files']:
 if f['path'].endswith('.png'):
  src=c/f['path']; dst=old/f['path']; dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
  assert hashlib.sha256(dst.read_bytes()).hexdigest()==f['sha256']
p=site/'index.html'; t=p.read_text(encoding='utf-8-sig').replace('吕洞宾完整八方向修正已接入游戏项目；其他角色仍逐项修正，候选图不代表整批完成。','吕洞宾、狮鼓护卫完整八方向修正已接入游戏项目；其他角色仍逐项修正，候选图不代表整批完成。').replace('当前游戏仅 24 吕洞宾、26 桂香药婆、29 何仙姑、30 韩湘子接入 V12。其余角色仍使用 V11。','当前游戏 24 吕洞宾、25 狮鼓护卫、26 桂香药婆、29 何仙姑、30 韩湘子接入 V12；其中本轮自然步态修正已完成 24、25。').replace("name:'狮鼓护卫',exported:true,integrated:false","name:'狮鼓护卫',exported:true,integrated:true");p.write_text(t,encoding='utf-8')
p=root/'README.md';t=p.read_text(encoding='utf-8-sig').replace('游戏当前实际接入V12的仅有24吕洞宾、26桂香药婆、29何仙姑、30韩湘子；23灯穗小使、25狮鼓护卫、27墨鸢游侠、28月兔机关师仍使用同ID的V11。已接入的四位也在本次造型、步态和比例复核范围内','游戏当前实际接入V12的有24吕洞宾、25狮鼓护卫、26桂香药婆、29何仙姑、30韩湘子；23灯穗小使、27墨鸢游侠、28月兔机关师仍使用同ID的V11。已接入的角色也在本次造型、步态和比例复核范围内')
if '狮鼓护卫：本轮接入记录' not in t:t+='\n\n## 狮鼓护卫：本轮接入记录\n\n25 狮鼓护卫已完成 64 张真实行走、8 张独立站立和 v3 定位验收，81 PNG 已接入并验证 SHA。城市截图已人工查看。独立副本定向测试 127/127 EditMode、8/8 PlayMode 通过。代码使用上次通过的 357 文件基线；第一次使用当前保存主工程的尝试因 4 个缺失的公会枚举编译失败，记录保留，原工程公会文件未改。这不是当前主工程全量编译通过声明。证据：'+str(e/'summary.json')+'。\n'
p.write_text(t,encoding='utf-8')
p=root/'candidate-stable-body/28_moon_rabbit_artificer';q=json.loads((p/'qc.json').read_text());q['visual_review']='hold_requires_gait_corrections';q['visual_followup']='visual-followup.json';write(p/'qc.json',q)
write(p/'visual-followup.json',{'status':'hold_do_not_publish','reviewed_utc':now,'reviewed':'8 complete idle + 8 walk contact boards','findings':['E/SE/S/SW/W04 and08 still high knee/precontact kick','NE/NW04 and08 high precontact lift','E/SE/SW/W02 and06 back hook needs low walk correction'],'preserve':['previously fixed NW arms','portrait and independent idle','all usable selected cells'],'assigned_to':'lu_natural_east after He NE/NW'})
p=root/'review/lu_natural_walk_sample/build_final_review.py';t=p.read_text(encoding='utf-8');t=t.replace("parser.add_argument('--character',default='24_lu_dongbin');args=parser.parse_args()","parser.add_argument('--character',default='24_lu_dongbin');parser.add_argument('--source-root',default=r'E:\\work\\image\\qdao_chibi_roster_v12\\candidate-stable-body');args=parser.parse_args()").replace("ROOT=Path(r'E:\\work\\image\\qdao_chibi_roster_v12\\candidate-stable-body')/args.character","ROOT=Path(args.source_root)/args.character");p.write_text(t,encoding='utf-8')
print('25 evidence + preview published; 28 visual hold recorded; review supports explicit candidate root')

