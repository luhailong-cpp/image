from pathlib import Path
import json,hashlib,datetime,shutil,subprocess,sys,argparse
parser=argparse.ArgumentParser();parser.add_argument('--manifest-sha',required=True);args=parser.parse_args()
ROOT=Path(r'E:\work\image\qdao_chibi_roster_v12');p=ROOT/'candidate-stable-body/27_ink_kite_ranger'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,x):f.parent.mkdir(parents=True,exist_ok=True);f.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
assert sha(p/'manifest.json')==args.manifest_sha
m=json.loads((p/'manifest.json').read_text());qc=json.loads((p/'qc.json').read_text());assert not qc['errors']
review=json.loads((p/'root-visual-review.json').read_text());assert review['status']=='passed' and len(review['directions_reviewed'])==8
for s in m['sources'].values():
 assert sha(s['path'])==s['sha256']
 if 'assembly_metadata_sha256' in s:assert sha(Path(s['path']).with_suffix('.assembly.json'))==s['assembly_metadata_sha256']
now=datetime.datetime.now(datetime.timezone.utc).isoformat();ev=Path(r'E:\work\mmorpg-client\Docs\ArtEvidence\v12-stable-roster\27-ink-kite-ranger');ev.mkdir(parents=True,exist_ok=True)
if not (ev/'qc-before-approval.json').exists():shutil.copy2(p/'qc.json',ev/'qc-before-approval.json')
qc.update(status='passed',visual_review='passed',visual_review_date_utc=now,visual_review_scope='Root reviewed all8 final idle+walk contact boards. Source author and root independently audited SW01/05 hip, knee and cloth overlap continuity.')
write(p/'qc.json',qc);write(p/'visual-review.json',review)
dest=Path(r'E:\work\mmorpg-client\Assets\Resources\World\Characters\QdaoRosterV12')/p.name
if not (ev/'before-import.json').exists():
 if dest.exists():shutil.copytree(dest,ev/'before-import'/p.name,dirs_exist_ok=True)
 write(ev/'before-import.json',{'date_utc':now,'target':str(dest),'previous_v12_directory_existed':dest.exists(),'v11_files_untouched':True})
subprocess.run([sys.executable,str(ROOT/'verify_delivery.py'),'--character-dir',str(p)],check=True)
subprocess.run([sys.executable,str(ROOT/'sync_to_client.py'),'--source-root',str(p.parent),'--character',p.name],check=True)
subprocess.run([sys.executable,str(ROOT/'sync_to_client.py'),'--source-root',str(p.parent),'--character',p.name,'--verify-only'],check=True)
print('27 approved and published; immutable manifest SHA',sha(p/'manifest.json'))
