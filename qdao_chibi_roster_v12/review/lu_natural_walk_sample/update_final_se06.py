from pathlib import Path
from PIL import Image
import json,hashlib,subprocess,sys
root=Path(r'E:\work\image\qdao_chibi_roster_v12');here=root/'review/lu_natural_walk_sample';out=root/'candidate-stable-body/24_lu_dongbin/source'
p=out/'walk-SE-raw.png';im=Image.open(p).convert('RGBA');fix=here/'directions/SE/fix06-arm/candidate06-cell.png';cell=Image.open(fix).convert('RGBA');assert cell.size==(627,627);im.paste(cell,(627,627));im.save(p)
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
a=p.with_suffix('.assembly.json');meta=json.loads(a.read_text());meta['output_sha256']=sha(p);meta['sources'][5]={'path':str(fix),'sha256':sha(fix),'native_size':[627,627],'source_box':[0,0,627,627],'output_phase':6,'upstream_raw':str(fix.with_name('candidate06-raw.png')),'upstream_raw_sha256':sha(fix.with_name('candidate06-raw.png')),'whole_native_cell_scale':0.5,'review_file':str(fix.with_name('review.json'))};a.write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
script=here/'assemble_stable_candidate.py';s=script.read_text(encoding='utf-8-sig').replace("D/'SE/fix06/candidate06-cell.png'","D/'SE/fix06-arm/candidate06-cell.png'");script.write_text(s,encoding='utf-8')
subprocess.run([sys.executable,str(root/'assemble_raw.py'),'--kind','nw_se','--first',str(out/'walk-NW-raw.png'),'--second',str(p),'--first-rows','2','--first-cols','4','--second-rows','2','--second-cols','4','--output',str(out/'nw_se-raw.png')],check=True)
r=out.parent/'candidate-source-review.json';m=json.loads(r.read_text());m['direction_inputs']['SE']['sha256']=sha(p);m['direction_inputs']['SE']['upstream']['sha256']=sha(a);m['direction_inputs']['SE']['upstream']['data']=meta;m['reviewed_fix06_arm']={'path':str(fix.with_name('review.json')),'sha256':sha(fix.with_name('review.json'))};r.write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8')
print('SE06 final reviewed arm correction integrated into raw source, no per-body compositing')
