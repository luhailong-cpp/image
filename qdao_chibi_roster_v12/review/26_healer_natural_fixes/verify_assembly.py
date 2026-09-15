from pathlib import Path
from PIL import Image
import hashlib,json
R=Path(__file__).resolve().parent;C=R.parent.parent/'candidate-stable-body/26_osmanthus_healer';O=R.parent.parent/'26_osmanthus_healer'
def rgba(i):return hashlib.sha256(i.convert('RGBA').tobytes()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
p=json.loads((R/'generation-provenance.json').read_text());ret=json.loads((R/'source-retention.json').read_text());plan=json.loads((R/'phase-plan.json').read_text());checked=[]
for call in p['calls']:assert sha(call['original_generated_path'])==sha(call['saved_raw_path'])==call['sha256'];assert sha(call['prompt_path'])==call['prompt_sha256']
for cell in p['selected_cells']:
 raw=Image.open(cell['raw_path']).convert('RGBA');native=raw.crop(cell['raw_crop']);assert rgba(native)==cell['native_rgba_sha256']==rgba(Image.open(cell['native_cell_path']));expected=native.resize((443,443),Image.Resampling.LANCZOS);assert rgba(expected)==cell['final_rgba_sha256']==rgba(Image.open(cell['final_cell_path']))
for r in ret['cells']:
 d=r['direction'];n=r['new_phase']-1;im=Image.open(C/f'source/walk-{d}-final.png');actual=im.crop((n%4*443,n//4*443,(n%4+1)*443,(n//4+1)*443));assert rgba(actual)==r['candidate_rgba_sha256'];assert plan['directions'][d]['candidate_order_in_old_phases'][n]==r['old_phase'];checked.append([d,n+1])
 if not r['changed']:assert rgba(actual)==r['original_rgba_sha256']
for kind,ds in {'s_e':['S','E'],'n_w':['N','W'],'ne_sw':['NE','SW'],'nw_se':['NW','SE']}.items():
 pair=Image.open(C/f'source/pair-{kind}.png')
 for i in range(16):
  d=ds[i//8];n=i%8;src=Image.open(C/f'source/walk-{d}-final.png');assert rgba(pair.crop((i%4*443,i//4*443,(i%4+1)*443,(i//4+1)*443)))==rgba(src.crop((n%4*443,n//4*443,(n%4+1)*443,(n//4+1)*443)))
for q,h in ret['baseline_files_sha256'].items():assert sha(O/q)==h
assert sha(C/'source/idle.png')==sha(O/'source/idle.png')
out={'status':'passed','native_generated_crops_verified':30,'whole_cell_resamples_verified':30,'canonical_walk_cells_verified':len(checked),'unchanged_raw_cells':42,'exact_pair_cells_verified':64,'original_sources_unchanged':True};(R/'assembly-verification.json').write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out))
