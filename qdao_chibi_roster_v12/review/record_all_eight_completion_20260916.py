from pathlib import Path
import json,hashlib,datetime,sys
ROOT=Path(r'E:\work\image\qdao_chibi_roster_v12')
PROJECT=Path(r'E:\work\mmorpg-client')
EVIDENCE=PROJECT/'Docs/ArtEvidence/v12-stable-roster/eight-natural-current-code-20260916-retry'
IDS=['23_lantern_courier','24_lu_dongbin','25_lion_drum_guard','26_osmanthus_healer','27_ink_kite_ranger','28_moon_rabbit_artificer','29_he_xiangu','30_han_xiangzi']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
browser_path=ROOT/'review/browser-qc/review-pages-result.json'
browser=read(browser_path);assert browser['status']=='passed' and browser['pages']['index']['exportedDirectionPairs']==64 and browser['pages']['index']['candidatesDisabled']==0 and not browser['errors']
summary=read(EVIDENCE/'summary.json');snapshot=read(EVIDENCE/'input-snapshot.json')
assert summary['status']=='passed' and summary['sourceMatchesSnapshotAtFinish'] is True
assert set(summary['characterIds'])==set(IDS)
results={r['platform']:r for r in summary['results']}
for mode in ['EditMode','PlayMode']:assert results[mode]['result']=='Passed' and results[mode]['failed']==0 and results[mode]['passed']>0
visual=read(EVIDENCE/'root-visual-runtime-review.json');assert visual['status']=='passed' and set(visual['reviewed_character_ids'])==set(IDS)
now=datetime.datetime.now(datetime.timezone.utc).isoformat();items=[]
for cid in IDS:
 p=ROOT/('candidate-natural-body' if cid=='29_he_xiangu' else 'candidate-stable-body')/cid
 m=read(p/'manifest.json');q=read(p/'qc.json');a=read(PROJECT/'Assets/Resources/World/Characters/QdaoRosterV12'/cid/'appearance.json')
 assert q['status']=='passed' and q['visual_review']=='passed'
 assert a['manifest_sha256']==sha(p/'manifest.json') and a['qc_sha256']==sha(p/'qc.json')
 assert a['alignmentVersion']==3 and a['frameCount']==8 and a['dedicatedIdle']
 pngs=[x for x in m['files'] if x['path'].endswith('.png')];assert len(pngs)==81
 for item in pngs:assert sha(PROJECT/'Assets/Resources/World/Characters/QdaoRosterV12'/cid/item['path'])==item['sha256']
 rec={'status':'published_and_verified','verified_utc':now,'target_project':str(PROJECT),'source_manifest_sha256':sha(p/'manifest.json'),'png_count':81,'alignment_version':3,'movement_frames':64,'independent_idle_frames':8,'runtime_evidence':str(EVIDENCE/'summary.json'),'visual_runtime_evidence':str(EVIDENCE/'root-visual-runtime-review.json'),'editmode_passed':results['EditMode']['passed'],'playmode_passed':results['PlayMode']['passed'],'validation_scope':{'code':'current saved source snapshot; matching at start and finish','csharp_files':len(snapshot['matchingCSharpFiles']),'resource_files':len(snapshot['resourceFiles'])}}
 old=p/'client-integration.json'
 if old.exists() and not (EVIDENCE/'prior-client-integration'/f'{cid}.json').exists():write(EVIDENCE/'prior-client-integration'/f'{cid}.json',read(old))
 write(old,rec);items.append({'character_id':cid,'source':str(p),'manifest_sha256':sha(p/'manifest.json'),'png_count':81})
he=ROOT/'review/he_xiangu_natural_walk/STATUS.json';h=read(he);h.update(status='published_and_runtime_verified',updated_utc=now,runtime_evidence=str(EVIDENCE/'summary.json'),runtime_evidence_pending=False);write(he,h)
completion={'status':'complete','completed_utc':now,'characters':items,'walk_frames':512,'independent_idle_frames':64,'portraits':8,'png_files':648,'runtime_results':summary['results'],'runtime_evidence':str(EVIDENCE/'summary.json'),'visual_runtime_evidence':str(EVIDENCE/'root-visual-runtime-review.json'),'browser_evidence':str(browser_path),'browser_direction_pairs':64,'preview':'http://127.0.0.1:8871/','earlier_compile_failures':'Historical Guild/Trade failures are retained under prior evidence folders; current eight-character run passed.'}
write(ROOT/'completion-20260916.json',completion)
print(json.dumps({'status':'complete','characters':len(items),'png_files':648,'walk_frames':512,'idle_frames':64,'results':summary['results']},ensure_ascii=False))
