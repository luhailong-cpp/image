from pathlib import Path
import json,hashlib,datetime,shutil,sys,subprocess
ROOT=Path(r'E:\work\image\qdao_chibi_roster_v12');p=ROOT/'candidate-stable-body/30_han_xiangzi'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,x):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=json.loads((p/'manifest.json').read_text());assert sha(p/'manifest.json')=='c625eb54989646761d4150ffe6ab6bb572ae7fbbaf1ea1c375ebee304a17ed62'
for kind,s in m['sources'].items():
 assert sha(s['path'])==s['sha256'],kind
 a=Path(s['path']).with_suffix('.assembly.json')
 if 'assembly_metadata_sha256' in s:assert sha(a)==s['assembly_metadata_sha256']
qc=json.loads((p/'qc.json').read_text());assert qc['errors']==[]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
qc.update(status='passed',visual_review='passed',visual_review_date_utc=now,visual_review_scope='Root independently reviewed all eight final nine-cell idle/walk contact boards after canonical phase rotation; direction author reviewed original identity, edited feet and head size, alternating near/far leg and arm phases.')
write(p/'qc.json',qc)
review={'status':'passed','date_utc':now,'reviewers':['root','lu_natural_north'],'evidence':[f'review/{d}-idle-walk.jpg' for d in ['N','NE','E','SE','S','SW','W','NW']],'phase_plan':'../../review/han_xiangzi_natural_gait_fixes/review/phase-mapping-right-first.json','scope':['Distinct young Han Xiangzi identity, black small bun and blue cloth ribbon, blue and ivory cross-collar tunic, dark cloth trousers, white wraps and blue cloth shoes, one bamboo flute secured at anatomicalLEFT waist. No magical light or fantasy armor.','All64 authored walk poses and8 separately authored idle poses; anatomicalRIGHT contact phase01 throughout.','32 authored leg corrections lower exaggerated precontacts and high rear heel curls across all8 directions; original contact stride lengths and appropriate rear-view depth retained.','Six earlier authored head corrections preserved; original portrait,8idle and32other walk source cells retained. All8 direction cycles rotated together05..08,01..04 to canonicalRIGHT first. Root reviewed all8 nine-cell final boards; after explicit4px edge cleanup72/72 alpha,G,geometry and protected reds are verified unchanged, with N/SE final edge spot checks.','One common scale and v3 fixed-idle head anchors; no per-frame warping or synthesized motion.'],'limits':['Internal visual approval; user preference can still require revision.','Runtime gameplay tests of this exact import are recorded separately after publication.']}
write(p/'visual-review.json',review)
out=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\30-han-xiangzi');out.mkdir(parents=True,exist_ok=True)
dest=Path(r'E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12\30_han_xiangzi')
if not (out/'before-import.json').exists():
 if dest.exists():shutil.copytree(dest,out/'before-import/30_han_xiangzi',dirs_exist_ok=True)
 prior=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\qdao-roster-v12-import.json')
 if prior.exists():shutil.copy2(prior,out/'previous-import.json')
 write(out/'before-import.json',{'date_utc':now,'target':str(dest),'previous_v12_directory_existed':dest.exists(),'fallback_before_import':'QdaoRosterV11/30_han_xiangzi if no V12 appearance.json','v11_files_untouched':True})
subprocess.run([sys.executable,str(ROOT/'verify_delivery.py'),'--character-dir',str(p)],check=True)
subprocess.run([sys.executable,str(ROOT/'sync_to_client.py'),'--source-root',str(p.parent),'--character',p.name,'--plan-only'],check=True)
print('30 visually approved, verified, backed up and ready for import.')

