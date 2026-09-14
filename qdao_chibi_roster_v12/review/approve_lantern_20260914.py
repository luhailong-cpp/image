from pathlib import Path
import json,hashlib,datetime,shutil,sys,subprocess
ROOT=Path(r'E:\work\image\qdao_chibi_roster_v12');p=ROOT/'candidate-stable-body/23_lantern_courier'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,x):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=json.loads((p/'manifest.json').read_text());assert sha(p/'manifest.json')=='385c3158106d5e5a9b439d2015a714a0e13c6c24c90dd9d801699f08c7bd72b6'
for kind,s in m['sources'].items():
 assert sha(s['path'])==s['sha256'],kind
 a=Path(s['path']).with_suffix('.assembly.json')
 if 'assembly_metadata_sha256' in s:assert sha(a)==s['assembly_metadata_sha256']
qc=json.loads((p/'qc.json').read_text());assert qc['errors']==[]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
qc.update(status='passed',visual_review='passed',visual_review_date_utc=now,visual_review_scope='Root independently reviewed all eight final nine-cell idle/walk contact boards after canonical phase rotation; direction author reviewed original identity, edited feet and head size, alternating near/far leg and arm phases.')
write(p/'qc.json',qc)
review={'status':'passed','date_utc':now,'reviewers':['root','lu_natural_west'],'evidence':[f'review/{d}-idle-walk.jpg' for d in ['N','NE','E','SE','S','SW','W','NW']],'phase_plan':'../../review/23_lantern_natural_fixes/phase-plan.json','scope':['Distinct twin-braid young lantern courier identity; warm red and ochre cloth, ivory trousers, cloth-wrapped boots and a single paper lantern in anatomicalLEFT hand. No magical aura or fantasy armor.','All64 authored walk poses and8 separately authored idle poses; anatomicalRIGHT contact phase01 throughout.','10 authored lower pre-contact poses in E/SE/S/SW/W remove front kicks; existing light courier strides, modest heel lift and rear-view foot depth retained.','9 walk heads rebuilt to match the same-direction idle; 19 total redrawn cells, 53 original pose cells and portrait preserved. All directions independently confirmed RIGHT-first in original order.','One common scale and v3 fixed-idle head anchors; no per-frame warping or synthesized motion.'],'limits':['Internal visual approval; user preference can still require revision.','Runtime gameplay tests of this exact import are recorded separately after publication.']}
write(p/'visual-review.json',review)
out=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\23-lantern-courier');out.mkdir(parents=True,exist_ok=True)
dest=Path(r'E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12\23_lantern_courier')
if not (out/'before-import.json').exists():
 if dest.exists():shutil.copytree(dest,out/'before-import/23_lantern_courier',dirs_exist_ok=True)
 prior=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\qdao-roster-v12-import.json')
 if prior.exists():shutil.copy2(prior,out/'previous-import.json')
 write(out/'before-import.json',{'date_utc':now,'target':str(dest),'previous_v12_directory_existed':dest.exists(),'fallback_before_import':'QdaoRosterV11/23_lantern_courier if no V12 appearance.json','v11_files_untouched':True})
subprocess.run([sys.executable,str(ROOT/'verify_delivery.py'),'--character-dir',str(p)],check=True)
subprocess.run([sys.executable,str(ROOT/'sync_to_client.py'),'--source-root',str(p.parent),'--character',p.name,'--plan-only'],check=True)
print('23 visually approved, verified, backed up and ready for import.')

