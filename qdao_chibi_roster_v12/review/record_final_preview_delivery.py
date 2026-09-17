from pathlib import Path
import json,hashlib,datetime,re,argparse
p=argparse.ArgumentParser();p.add_argument('--root-city-review-passed',action='store_true',required=True);args=p.parse_args()
root=Path(r'E:\work\image\qdao_chibi_roster_v12');site=root/'review/site';e=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\eight-natural-current-code-20260916-retry')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
s=read(e/'summary.json');snap=read(e/'input-snapshot.json');preview=read(site/'preview-source-verification.json');browser=read(root/'review/browser-qc/review-pages-result.json');retry=read(root/'review/browser-qc/image-retry-result.json')
assert s['status']=='passed' and len(s['characterIds'])==8
assert len(snap['matchingCSharpFiles'])==394 and len(snap['resourceFiles'])==656
assert s['originalOpenUnityUntouched'] and snap['originalOpenUnityUntouched']
for platform,count in [('EditMode',127),('PlayMode',8)]:
 r=next(r for r in s['results'] if r['platform']==platform);assert r['total']==count and r['passed']==count and r['failed']==0 and r['skipped']==0 and r['exitCode']==0
assert preview['status']=='passed' and len(preview['characters'])==8 and not preview['pending']
assert browser['status']=='passed' and browser['pages']['index']['exportedDirectionPairs']==64 and browser['pages']['index']['candidatesDisabled']==0 and not browser['errors']
assert retry['status']=='passed'
pins={x['characterId']:x['manifest_sha256'] for x in snap['approvals']}
for c in preview['characters']:assert pins[c['character_id']]==c['manifest_sha256'] and c['png_count']==81
for cid in s['characterIds']:assert (e/f'tianyong-{cid}.png').is_file()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
status='2026-09-17 03:28 UTC 完成状态：八位道家 Q 版角色的造型、自然步态和游戏素材接入已完成。每人 64 张真实行走、8 张独立站立、1 张肖像及 8 张行走条带，每人 81 张、八人共 648 张 PNG；全部按对齐 v3 发布，预览与游戏逐文件 SHA 一致。独立 Unity 副本的 127/127 EditMode、8/8 PlayMode 通过，八人主城外观已逐一视审。测试结论对应 03:18 UTC 保存的代码与资源快照；内部验收不代表用户已经认可美术。'
current='八位角色为灯穗小使、年轻吕洞宾、狮鼓护卫、桂香药婆、墨鸢游侠、月兔机关师、何仙姑、韩湘子，均已启用 V12。吕洞宾、何仙姑、韩湘子保留各自八仙身份与器物，造型按道家 Q 版制作。'
section='''## 本轮八人交付与验证（2026-09-17 UTC）

- 最终美术源：`candidate-stable-body/<角色ID>`；何仙姑使用 `candidate-natural-body/29_he_xiangu`，为素色道袍与长裤版本。原始生成图、来源记录和此前版本保留。
- 运行证据：[summary.json](../../mmorpg-client/Docs/ArtEvidence/v12-stable-roster/eight-natural-current-code-20260916-retry/summary.json)。394 个 C#、648 张 PNG 与 8 个启用文件在启动前逐一匹配。运行期间其他任务修改了 6 个社交/地图相关 C#，因此结论针对该保存快照。原打开 Unity 场景未操作。
- 首轮同一检查因测试超时未完成；只为原有测试增加 `[Timeout(600000)]`，断言未改。重试的 127 项 EditMode 与 8 项 PlayMode 均通过，历史失败记录保留。
- [预览源校验](review/site/preview-source-verification.json)与[浏览器验收](review/browser-qc/review-pages-result.json)通过：8 人 × 8 方向共 64 组，没有禁用角色；逐帧、循环、独立站立、半速、390px 移动端均可用。一次图片请求失败后重新选择同方向的恢复检查也通过。
- [八人新版总览](review/site/roster-final.jpg)、[新旧肖像对照](review/site/portrait-comparison.jpg)、[本地交互预览](http://127.0.0.1:8871/)。恢复本地服务可运行 `python review/serve_final_preview.py`，只提供 `review/site` 目录。
'''
for filename in ['README.md','CLIENT_CONTRACT.md']:
 f=root/filename;t=f.read_text(encoding='utf-8');parts=t.split('\n\n');assert '当前状态：' in parts[1] or '完成状态：' in parts[1];parts[1]=status;parts[2]=current;t='\n\n'.join(parts)
 assert '## 本轮八人交付与验证（2026-09-17 UTC）' not in t
 t=t.replace(current+'\n\n',current+'\n\n'+section+'\n',1)
 t=t.replace('本轮 7 位已接入。其余角色继续收尾。','本轮八位已全部接入。')
 t=t.replace('当前资源版本及暂停状态以上述说明为准。','当前资源版本和运行范围以上述完成记录为准。')
 t=t.replace('当前停步修复证据：','历史停步修复证据：').replace('当前停步修复定向运行记录：','历史停步修复定向运行记录：')
 t=t.replace('新吕洞宾已完成本轮修正与接入；其余角色按最新用户继续指令逐项推进。','这是早期停步修复记录；本轮八人完整结果见开头。')
 f.write_text(t,encoding='utf-8')
f=site/'index.html';t=f.read_text(encoding='utf-8');t=re.sub(r'<p class="deployment">.*?</p>','<p class="deployment">已完成 8 / 8 位：每人八方向，每方向 8 张行走帧，另有独立站立图。独立 Unity 副本 127 项 EditMode、8 项 PlayMode 通过；运行结论对应 2026-09-17 03:18 UTC 保存快照。</p>',t,count=1);f.write_text(t,encoding='utf-8')
f=site/'sample.html';t=f.read_text(encoding='utf-8').replace('右边是这次完整候选。','右边是这次已接入的完整修正版本。').replace('其余角色仍需继续验收。','本轮八位角色均已完成素材接入与独立副本运行验收。');f.write_text(t,encoding='utf-8')
receipt={'status':'complete','recorded_utc':now,'characters':8,'png_count':648,'walk_frames':512,'independent_idle_frames':64,'runtime_summary':str(e/'summary.json'),'runtime_summary_sha256':sha(e/'summary.json'),'source_code_snapshot_count':394,'resource_snapshot_count':656,'editmode_passed':127,'playmode_passed':8,'root_city_visual_review':'passed','runtime_scope':'2026-09-17T03:18 UTC saved snapshot in isolated Unity clone','source_matches_snapshot_at_finish':s['sourceMatchesSnapshotAtFinish'],'source_changed_files':s['sourceChangedFiles'],'browser_64_directions':'passed','image_request_recovery':'passed','original_open_unity_untouched':True}
(site/'delivery-status.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
