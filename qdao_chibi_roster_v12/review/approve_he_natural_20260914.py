from pathlib import Path
import json,hashlib,datetime,shutil,sys,subprocess
ROOT=Path(r'E:\work\image\qdao_chibi_roster_v12');p=ROOT/'candidate-natural-body/29_he_xiangu'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,x):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
m=json.loads((p/'manifest.json').read_text());assert sha(p/'manifest.json')=='1a6ea359e1b8b5d99653b624ceb197d204ab11300c6ce67824c301a18994070e'
for kind,s in m['sources'].items():
 assert sha(s['path'])==s['sha256'],kind
 a=Path(s['path']).with_suffix('.assembly.json')
 if 'assembly_metadata_sha256' in s:assert sha(a)==s['assembly_metadata_sha256']
qc=json.loads((p/'qc.json').read_text());assert qc['errors']==[]
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
qc.update(status='passed',visual_review='passed',visual_review_date_utc=now,visual_review_scope='Root independently reviewed all eight final nine-cell idle/walk contact boards after canonical phase rotation; direction author reviewed original identity, edited feet and head size, alternating near/far leg and arm phases.')
write(p/'qc.json',qc)
review={'status':'passed','date_utc':now,'reviewers':['root','lu_natural_east'],'evidence':[f'review/{d}-idle-walk.jpg' for d in ['N','NE','E','SE','S','SW','W','NW']],'phase_plan':'candidate-source-review.json','scope':['New plain-cloth He Xiangu identity: youthful dark low bun, ivory crosscollar tunic, pale sage overrobe, dark green sash, full-length pale trousers and ivory flats. White lotus pin on anatomicalRIGHT, single small closed lotus behind anatomicalLEFT shoulder. New portrait uses same costume. No glow, petal skirt or fantasy armor.','All64 authored walk poses and8 separately authored idle poses; anatomicalRIGHT contact phase01 throughout.','64 newly authored low walking poses across8 directions, real opposing contacts/passing/precontacts and natural arm opposition. Root reviewed every full direction before final idle correction and all6 corrected idle directions afterward; NE/NW independently authored and reviewed by east.','Six neutral idles redrawn to match authored walks;NE/NW independent idle retained. Final same-direction mean dark-head width difference at most2.3percent; source raw silhouette metric is diagnostic and not used to resize.64 walk intrinsic alpha/G/geometry remain identical after new idle references and4px edge cleanup.','One common scale and v3 fixed-idle head anchors; no per-frame warping or synthesized motion.'],'limits':['Internal visual approval; user preference can still require revision.','Runtime gameplay tests of this exact import are recorded separately after publication.']}
write(p/'visual-review.json',review)
out=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\29-he-xiangu-natural');out.mkdir(parents=True,exist_ok=True)
dest=Path(r'E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12\29_he_xiangu')
if not (out/'before-import.json').exists():
 if dest.exists():shutil.copytree(dest,out/'before-import/29_he_xiangu',dirs_exist_ok=True)
 prior=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\qdao-roster-v12-import.json')
 if prior.exists():shutil.copy2(prior,out/'previous-import.json')
 write(out/'before-import.json',{'date_utc':now,'target':str(dest),'previous_v12_directory_existed':dest.exists(),'fallback_before_import':'QdaoRosterV11/29_he_xiangu if no V12 appearance.json','v11_files_untouched':True})
subprocess.run([sys.executable,str(ROOT/'verify_delivery.py'),'--character-dir',str(p)],check=True)
subprocess.run([sys.executable,str(ROOT/'sync_to_client.py'),'--source-root',str(p.parent),'--character',p.name,'--plan-only'],check=True)
print('29 visually approved, verified, backed up and ready for import.')

