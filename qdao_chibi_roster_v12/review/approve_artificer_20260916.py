from pathlib import Path
import json,hashlib,datetime,shutil,subprocess,sys
ROOT=Path(r'E:\work\image\qdao_chibi_roster_v12');p=ROOT/'candidate-stable-body/28_moon_rabbit_artificer'
def sha(f): return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,x): f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(p/'manifest.json')=='16bd72b1ebe9f070704dcaae361b34fd90d8db3e71b9c91b38043b6f9ccb0387'
m=json.loads((p/'manifest.json').read_text());qc=json.loads((p/'qc.json').read_text());assert not qc['errors']
for s in m['sources'].values():
 assert sha(s['path'])==s['sha256']
 if 'assembly_metadata_sha256' in s: assert sha(Path(s['path']).with_suffix('.assembly.json'))==s['assembly_metadata_sha256']
for name in ['assembly-validation.json','export-preservation-checks.json']: assert json.loads((ROOT/'review/28_low_walk_fixes'/name).read_text())['status']=='passed'
now=datetime.datetime.now(datetime.timezone.utc).isoformat();evidence=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\28-moon-rabbit-artificer');evidence.mkdir(parents=True,exist_ok=True)
for name in ['visual-followup.json','REVIEW.md','qc.json']:
 dest=evidence/'before-final-review'/name
 if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p/name,dest)
qc.update(status='passed',visual_review='passed',visual_review_date_utc=now,visual_review_scope='Root reviewed all eight final idle plus eight-walk contact boards, including retained NW02/06 heel lift and original hip/arm phase audit.')
write(p/'qc.json',qc)
write(p/'visual-review.json',{'status':'passed','date_utc':now,'reviewers':['root'],'evidence':[f'review/{d}-idle-walk.jpg' for d in ['N','NE','E','SE','S','SW','W','NW']],'scope':['Distinct bob-haired child craftsperson, rabbit hairpin, plain lilac cloth work robe, ivory cuffs, apricot trousers, green cloth shoes and wooden tool box; no glow or fantasy effects.','22 authored low-gait replacement cells;42 walk,8 idle and portrait exports byte-identical to selected baseline.','All eight complete cycles visually reviewed. Low forward pre-contact steps, opposing arm swings and alternating support legs retained. NW02/06 retained rear heel lift reads as back-view depth and compact child stride, consistent with existing hip/arm continuity audit.','All64 authored walk cells plus8 separate neutral idle cells, no mirrored or interpolated movement. Common scale, fixed idle head anchor and genuine foot depth retained.','N/SW/W/NW original LEFT-first cycles rotate by4 as complete cycles; other directions retain source order.'],'limits':['Internal visual acceptance; user preference may still lead to revision.','Exact current game runtime verification follows publication.']})
write(p/'visual-followup.json',{'status':'resolved','date_utc':now,'previous_hold_preserved':str(evidence/'before-final-review/visual-followup.json'),'resolution':'22 source-authored low-gait cells resolved prior high precontact and rear hook findings; root reviewed final eight-direction boards.','remaining_findings':[]})
with (p/'REVIEW.md').open('a',encoding='utf-8') as f:f.write('\n\n## 2026-09-16 最终复核更新\n\n上文为重绘前历史交接。新增22格真实低抬脚步态，42格行走、8格站立和头像输出逐字节保留。根任务已检查全部8方向最终联系图，包括NW02/06原有后脚透视与摆臂；最终视觉审核通过。数值与来源记录见 review/28_low_walk_fixes；后续导入和运行结果见 client-integration.json。\n')
dest=Path(r'E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12')/p.name
if not (evidence/'before-import.json').exists():
 if dest.exists():shutil.copytree(dest,evidence/'before-import'/p.name,dirs_exist_ok=True)
 write(evidence/'before-import.json',{'date_utc':now,'target':str(dest),'previous_v12_directory_existed':dest.exists(),'v11_files_untouched':True})
subprocess.run([sys.executable,str(ROOT/'verify_delivery.py'),'--character-dir',str(p)],check=True)
subprocess.run([sys.executable,str(ROOT/'sync_to_client.py'),'--source-root',str(p.parent),'--character',p.name],check=True)
subprocess.run([sys.executable,str(ROOT/'sync_to_client.py'),'--source-root',str(p.parent),'--character',p.name,'--verify-only'],check=True)
print('28 approved and published; immutable manifest SHA',sha(p/'manifest.json'))
