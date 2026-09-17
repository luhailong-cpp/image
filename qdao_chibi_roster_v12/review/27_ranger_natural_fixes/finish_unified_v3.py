"""Unify reviewed authored ranger cells, with transparent source alpha retained."""
from pathlib import Path
import json,hashlib,shutil,subprocess,sys
from PIL import Image
R=Path(r'E:\work\image\qdao_chibi_roster_v12');C=R/'candidate-stable-body/27_ink_kite_ranger';B=R/'review/27_ranger_natural_fixes';S=C/'source';S.mkdir(exist_ok=True,parents=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
backup=B/'before-final-unified-v3';backup.mkdir(exist_ok=True)
for rel in ['manifest.json','qc.json','validation.json','processing/frame-transforms.json']:
 p=C/rel;q=backup/rel
 if p.exists() and not q.exists():q.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,q)
inputs={d:B/'six-direction-gait'/d/'final-sheet.png' for d in ['N','E','SE','S','SW','W']}
inputs.update({d:S/f'walk-{d}-final.png' for d in ['NE','NW']})
phase={}
for d,p in inputs.items():
 m=json.loads(p.with_suffix('.assembly.json').read_text(encoding='utf-8-sig'));assert sha(p)==m['output_sha256'];assert Image.open(p).size==(1772,886)
 phase[d]={'source':str(p),'sha256':sha(p),'assembly_sha256':sha(p.with_suffix('.assembly.json')),'phase01':'RIGHT contact','phase05':'LEFT contact','order':list(range(1,9)),'rotation':0,'no_mirroring':True}
phase['SW']['anatomical_audit']='At SW01 the near anatomical LEFT hip on screen-right, under the belt pouch and weapon, connects to the right/rear boot; the far RIGHT leg from the screen-left side of the ivory central lapel connects to the left/front boot. At SW05 near LEFT leg connects to the lower-right foreground boot; far RIGHT retreats to upper-left. Screen position or apparent pants width alone does not identify anatomical leg.'
phase['W']['anatomical_audit']='W01 near LEFT arm swings forward while far RIGHT leg reaches forward; W05 near LEFT leg reaches forward and near arm swings back.'
phase['NE']['anatomical_audit']='Original 03 retained exactly; opposite contact hips preserved in authored reconstruction. No horizontal flips.'
write(B/'final-phase-plan.json',{'canonical_contact':'RIGHT first; LEFT fifth','root_and_agent_anatomical_review':'all directions already RIGHT-first; no cycle rotation needed','directions':phase})
for k,(a,b) in {'s_e':('S','E'),'n_w':('N','W'),'ne_sw':('NE','SW'),'nw_se':('NW','SE')}.items():
 cmd=[sys.executable,'-X','utf8',str(R/'assemble_raw.py'),'--kind',k,'--first',str(inputs[a]),'--second',str(inputs[b]),'--first-rows','2','--first-cols','4','--second-rows','2','--second-cols','4','--output',str(S/f'pair-{k}-final.png')]
 subprocess.run(cmd,check=True)
idle=R/'27_ink_kite_ranger/source/idle.png';portrait=R/'27_ink_kite_ranger/source/portrait-daoist.png'
write(B/'final-unified-provenance.json',{'status':'candidate_pending_processing_and_root_visual_review','direction_sources':phase,'idle':{'path':str(idle),'sha256':sha(idle),'unchanged':True},'portrait':{'path':str(portrait),'sha256':sha(portrait),'unchanged':True},'total_authored_replacements':37,'source_phase_replacements':{'N':[2,4,6,8],'E':[2,4,6,8],'SE':[2,4,6,8],'S':[4,8],'SW':[2,4,6,8],'W':[2,4,6,8],'NE':[1,2,4,5,6,7,8],'NW':list(range(1,9))},'preserved_walk_source_cells':27,'new_idle_art':False,'alignment_version':3,'common_scale':0.997624703087886,'component_padding':0,'despill_radius':4,'no_warp_or_bbox_fit':True,'published':False})
cmd=[sys.executable,'-X','utf8',str(R/'process_roster.py'),'--character-dir',str(C),'--alignment-version','3','--common-scale','0.997624703087886','--component-padding','0','--despill-magenta-edge','--despill-radius','4','--portrait-raw',str(portrait),'--idle',str(idle)]
for k in ['s_e','n_w','ne_sw','nw_se']:cmd+=['--'+k.replace('_','-'),str(S/f'pair-{k}-final.png')]
result=subprocess.run(cmd);print('processor_exit',result.returncode,flush=True)
if result.returncode:raise SystemExit(result.returncode)
subprocess.run([sys.executable,'-X','utf8',str(R/'verify_delivery.py'),'--character-dir',str(C),'--allow-pending-visual'],check=True)
subprocess.run([sys.executable,'-X','utf8',str(R/'review/lu_natural_walk_sample/build_final_review.py'),'--character',C.name,'--source-root',str(C.parent)],check=True)
print('Unified candidate ready for root visual review. Manifest '+sha(C/'manifest.json'),flush=True)
