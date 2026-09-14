from pathlib import Path
import json,hashlib,sys,subprocess,shutil
ROOT=Path(r'E:\work\image\qdao_chibi_roster_v12');old=ROOT/'26_osmanthus_healer';out=ROOT/'candidate-stable-body/26_osmanthus_healer'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
if out.exists() and not (out/'alignment-only-provenance.json').exists():raise SystemExit('Existing candidate requires inspection: '+str(out))
m=json.loads((old/'manifest.json').read_text());t=json.loads((old/'processing/frame-transforms.json').read_text());scale=t['walk']['N'][0]['shared_scale']
out.mkdir(parents=True,exist_ok=True)
for k,s in m['sources'].items():assert sha(s['path'])==s['sha256'],k
record={'purpose':'independent v3 alignment of unchanged existing healer artwork for visual inspection','formal_manifest_sha256':sha(old/'manifest.json'),'scale':scale,'sources':m['sources'],'portrait_sha256':sha(old/'portrait.png'),'original_pixels_changed':False,'phase_rotation_pending_review':True}
(out/'alignment-only-provenance.json').write_text(json.dumps(record,indent=2)+'\n')
cmd=[sys.executable,'-X','utf8',str(ROOT/'process_roster.py'),'--character-dir',str(out),'--alignment-version','3','--common-scale',str(scale),'--portrait',str(old/'portrait.png')]
for k,s in m['sources'].items():cmd+=['--'+k.replace('_','-'),s['path']]
subprocess.run(cmd,check=True)
subprocess.run([sys.executable,str(ROOT/'verify_delivery.py'),'--character-dir',str(out),'--allow-pending-visual'],check=True)
subprocess.run([sys.executable,str(ROOT/'review/lu_natural_walk_sample/build_final_review.py'),'--character',out.name],check=True)
print('Healer unchanged-art v3 candidate prepared; visual review and phase audit still required.')

