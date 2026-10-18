from pathlib import Path
import json,subprocess,sys,hashlib
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
from assemble_tile import save_qa
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
stems=['r03_c01_upper_water_left_20261016_a01','r03_c01_upper_water_center_20261016_a01','r03_c01_north_water_20261016_a01','r03_c01_lower_cliff_edge_20261016_a01']
boxes=[[0,550,1254,1804],[1100,550,2354,1804],[2350,0,3604,1254],[2350,2750,3604,4004]]
pair=Z/'qa/r03_c01_upper_water_pair_masks_20261016_v1'
masks=[pair/f'{stems[0]}.mask.png',pair/f'{stems[1]}.mask.png',Z/'qa'/f'{stems[2]}_mask_v1/source_selection_mask.png',Z/'qa'/f'{stems[3]}_mask_v2/source_selection_mask.png']
reviews=[]
for i,s in enumerate(stems):
 cp=Z/'qa'/f'{s}_mask_v{2 if i==3 else 1}/combined_native_crop.png'
 reviews.append(dict(stem=s,combinedNativeCrop=info(cp),mask=info(masks[i]),rootNativeScaleVisual='PASS: specific seam removed, native source selection boundary continuous; complete standard crop recheck follows'))
rp=Z/'qa/r03_c01_second4_masks_root_review_20261016.json'
with rp.open('x',encoding='utf8') as f:json.dump(dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='root',reviews=reviews,waterOverlap=info(pair/'joined_overlap_100pct.png'),waterOverlapVisual='PASS',southExtraCombined=info(Z/'qa/r03_c01_south_water_20261016_a01_mask_v2/combined_current_v5_plus_extra_native_crop.png'),southExtraVisual='PASS: extended mask removes remaining lower water division and preserves bottom115',fullTileAccepted=False),f,indent=2)
base=Z/'tiles/r03_c01_candidate-v6_4096.png';rec=base.with_suffix('.native-repair.json')
for i,(s,box,mask) in enumerate(zip(stems,boxes,masks),start=7):
 out=Z/'tiles'/f'r03_c01_candidate-v{i}_4096.png'
 r=subprocess.run([sys.executable,str(Z/'apply_native_tile_repair.py'),'--base',str(base),'--base-record',str(rec),'--source',str(Z/'native'/f'{s}.png'),'--generation-record',str(Z/'native'/f'{s}.png.generation.json'),'--input',str(Z/'guides'/f'{s}.input.json'),'--mask',str(mask),'--crop-box',*map(str,box),'--output',str(out)],capture_output=True,text=True)
 assert r.returncode==0,r.stdout+r.stderr
 base=out;rec=out.with_suffix('.native-repair.json');print(json.dumps(dict(version=i,image=info(out),record=info(rec))),flush=True)
qa=Z/'qa/r03_c01_v10_internal_review';qa.mkdir()
index=save_qa(qa,Image.open(base).convert('RGB'));(qa/'qa_index.json').write_text(json.dumps(index,indent=2)+'\n')
prior=Z/'qa/r03_c01_v5_internal_review/root_review.json';old=json.loads(prior.read_text());by={Path(x['path']).name:x for x in old['crops']}
delta=[]
for entry in index['seamAndJunctionCrops']:
 before=by[Path(entry['path']).name];same=entry['sha256']==before['sha256'];delta.append(dict(**entry,unchanged=same,prior=before,status=before['status'] if same else 'PENDING_DELTA_NATIVE_REVIEW'))
(qa/'delta_index.json').write_text(json.dumps(dict(base=info(base),record=info(rec),priorReview=info(prior),crops=delta),indent=2)+'\n')
statepath=Z/'root-current-selection-20261012.json';state=json.loads(statepath.read_text(encoding='utf-8-sig'));entry=state['tiles']['r03_c01'];entry.update(candidate=info(base),record=info(rec),internalReview=info(prior),internalClosurePassed=False,formalAccepted=False,repairStatus='Eight native local edits adopted after original-scale mask views; v10 changed standard crop review pending; middle-cliff independent fix in progress.',currentDeltaIndex=info(qa/'delta_index.json'));statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(finalImage=info(base),deltaQa=info(qa/'delta_index.json'),changed=sum(not x['unchanged'] for x in delta))),flush=True)
