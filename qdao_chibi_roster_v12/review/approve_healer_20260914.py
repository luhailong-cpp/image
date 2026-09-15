from pathlib import Path
import json,hashlib,datetime,shutil,sys,subprocess
ROOT=Path(r'E:\work\image\qdao_chibi_roster_v12');p=ROOT/'candidate-stable-body/26_osmanthus_healer'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,x):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=json.loads((p/'manifest.json').read_text());assert sha(p/'manifest.json')=='7533eebc4aa49229611f3a4d61b467dcef6744fc31c16ba6c18bcabce75576e2'
for kind,s in m['sources'].items():
 assert sha(s['path'])==s['sha256'],kind
 a=Path(s['path']).with_suffix('.assembly.json')
 if 'assembly_metadata_sha256' in s:assert sha(a)==s['assembly_metadata_sha256']
qc=json.loads((p/'qc.json').read_text());assert qc['errors']==[]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
qc.update(status='passed',visual_review='passed',visual_review_date_utc=now,visual_review_scope='Root independently reviewed all eight final nine-cell idle/walk contact boards after canonical phase rotation; direction author reviewed original identity, edited feet and head size, alternating near/far leg and arm phases.')
write(p/'qc.json',qc)
review={'status':'passed','date_utc':now,'reviewers':['root','lu_natural_west'],'evidence':[f'review/{d}-idle-walk.jpg' for d in ['N','NE','E','SE','S','SW','W','NW']],'phase_plan':'../../review/26_healer_natural_fixes/phase-plan.json','scope':['Distinct smiling elderly female herbalist identity, straw hat, gray low bun with yellow flowers, dark blue and ivory cloth tunic, dark loose trousers, black cloth shoes, wicker herb basket and waist gourds; no magical light or fantasy armor.','All64 authored walk poses and8 separately authored idle poses; anatomicalRIGHT contact phase01 throughout.','30 authored lower-leg corrections across8 directions remove high precontact knees and exaggerated rear hooks. Preserved contacts and low passing poses retain the original small herbalist stride and appropriate back-view foot depth.','All8 idle and34 original walk source cells plus portrait preserved. N/NE/S/SW/W/NW cycles rotate05..08,01..04; E/SE stay original order. Root reviewed all8 final nine-cell boards: hat/face proportions, alternating legs, arm opposition and basket attachment remain consistent.','One common scale and v3 fixed-idle head anchors; no per-frame warping or synthesized motion.'],'limits':['Internal visual approval; user preference can still require revision.','Runtime gameplay tests of this exact import are recorded separately after publication.']}
write(p/'visual-review.json',review)
out=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\26-healer');out.mkdir(parents=True,exist_ok=True)
dest=Path(r'E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12\26_osmanthus_healer')
if not (out/'before-import.json').exists():
 if dest.exists():shutil.copytree(dest,out/'before-import/26_osmanthus_healer',dirs_exist_ok=True)
 prior=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\qdao-roster-v12-import.json')
 if prior.exists():shutil.copy2(prior,out/'previous-import.json')
 write(out/'before-import.json',{'date_utc':now,'target':str(dest),'previous_v12_directory_existed':dest.exists(),'fallback_before_import':'QdaoRosterV11/26_osmanthus_healer if no V12 appearance.json','v11_files_untouched':True})
subprocess.run([sys.executable,str(ROOT/'verify_delivery.py'),'--character-dir',str(p)],check=True)
subprocess.run([sys.executable,str(ROOT/'sync_to_client.py'),'--source-root',str(p.parent),'--character',p.name,'--plan-only'],check=True)
print('26 visually approved, verified, backed up and ready for import.')

