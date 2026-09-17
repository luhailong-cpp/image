from pathlib import Path
import json,hashlib,shutil,sys,subprocess
R=Path(r'E:\work\image\qdao_chibi_roster_v12');B=R/'review/27_ranger_natural_fixes';C=R/'candidate-stable-body/27_ink_kite_ranger';S=C/'source'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=B/'first-final-attempt-before-alpha-cleanup';p.mkdir(exist_ok=True)
for rel in ['qc.json','manifest.json','processing/s_e/v12-sheet-qc.json']:
 a=C/rel;b=p/rel
 if a.exists() and not b.exists():b.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(a,b)
f=B/'six-direction-gait/S/final-sheet.png';record={'source':str(f),'sha256':sha(f),'assembly_sha256':sha(f.with_suffix('.assembly.json')),'phase01':'RIGHT contact','phase05':'LEFT contact','order':list(range(1,9)),'rotation':0,'no_mirroring':True,'alpha_noise_cleanup_maximum_removed_alpha':3,'original_rgb_and_alpha_gt3_unchanged':True}
for name,key in [('final-phase-plan.json','directions'),('final-unified-provenance.json','direction_sources')]:
 a=B/name;m=json.loads(a.read_text());m[key]['S']=record;a.write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
cmd=[sys.executable,'-X','utf8',str(R/'process_roster.py'),'--character-dir',str(C),'--alignment-version','3','--common-scale','0.997624703087886','--component-padding','0','--despill-magenta-edge','--despill-radius','4','--portrait-raw',str(R/'27_ink_kite_ranger/source/portrait-daoist.png'),'--idle',str(R/'27_ink_kite_ranger/source/idle.png')]
for k in ['s_e','n_w','ne_sw','nw_se']:cmd+=['--'+k.replace('_','-'),str(S/f'pair-{k}-final.png')]
subprocess.run(cmd,check=True)
subprocess.run([sys.executable,'-X','utf8',str(R/'verify_delivery.py'),'--character-dir',str(C),'--allow-pending-visual'],check=True)
subprocess.run([sys.executable,'-X','utf8',str(R/'review/lu_natural_walk_sample/build_final_review.py'),'--character',C.name,'--source-root',str(C.parent)],check=True)
print('27 READY FOR ROOT VISUAL REVIEW: '+sha(C/'manifest.json'),flush=True)
