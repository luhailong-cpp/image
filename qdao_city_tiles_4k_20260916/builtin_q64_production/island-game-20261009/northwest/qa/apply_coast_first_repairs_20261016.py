from pathlib import Path
import json,subprocess,sys,hashlib
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parents[1];sys.path.insert(0,str(Z))
from assemble_tile import save_qa
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:dict(path=Path(p).as_posix(),sha256=sha(p))
stems=['r03_c01_leaf_junction_20261016_a01','r03_c01_mid_water_left_20261016_a01','r03_c01_mid_water_center_20261016_a01','r03_c01_south_water_20261016_a01']
boxes=[[2500,1400,3754,2654],[0,1350,1254,2604],[1100,1350,2354,2604],[350,2842,1604,4096]]
reviews=[]
for stem in stems:
 d=Z/'qa'/f'{stem}_mask_v1'
 reviews.append(dict(stem=stem,combinedNativeCrop=info(d/'combined_native_crop.png'),mask=info(d/'source_selection_mask.png'),rootNativeScaleVisual='PASS: specific target improved and binary selection perimeter continuous; unrelated tile issues still pending'))
pair=Z/'qa/r03_c01_water_pair_masks_20261016_v1';review=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),reviewer='root',reviews=reviews,waterOverlap=info(pair/'joined_overlap_100pct.png'),waterOverlapVisual='PASS: fine waves continuous; no straight color division at joined overlap',pairMaskDerivation=info(pair/'derivation.json'),fullTileAccepted=False)
reviewpath=Z/'qa/r03_c01_first4_masks_root_review_20261016.json'
with reviewpath.open('x',encoding='utf8') as f:json.dump(review,f,indent=2)
base=Z/'tiles/r03_c01_candidate-v1_4096.png';rec=base.with_suffix('.assembly.json')
for i,(stem,box) in enumerate(zip(stems,boxes),start=2):
 mask=pair/f'{stem}.mask.png' if i in [3,4] else Z/'qa'/f'{stem}_mask_v1/source_selection_mask.png'
 out=Z/'tiles'/f'r03_c01_candidate-v{i}_4096.png'
 result=subprocess.run([sys.executable,str(Z/'apply_native_tile_repair.py'),'--base',str(base),'--base-record',str(rec),'--source',str(Z/'native'/f'{stem}.png'),'--generation-record',str(Z/'native'/f'{stem}.png.generation.json'),'--input',str(Z/'guides'/f'{stem}.input.json'),'--mask',str(mask),'--crop-box',*map(str,box),'--output',str(out)],capture_output=True,text=True)
 assert result.returncode==0,result.stdout+result.stderr
 base=out;rec=out.with_suffix('.native-repair.json');print(json.dumps(dict(version=i,image=info(out),record=info(rec))),flush=True)
qa=Z/'qa/r03_c01_v5_internal_review';assert not qa.exists();qa.mkdir()
index=save_qa(qa,Image.open(base).convert('RGB'));(qa/'qa_index.json').write_text(json.dumps(index,indent=2)+'\n')
old=json.loads((Z/'qa/r03_c01_v1_internal_review_20261016.json').read_text());oldby={Path(x['path']).name:x for x in old['reviewedCrops']}
delta=[]
for entry in index['seamAndJunctionCrops']:
 prior=oldby[Path(entry['path']).name];same=entry['sha256']==prior['sha256']
 delta.append(dict(**entry,unchanged=same,prior=prior,status=prior['status'] if same else 'PENDING_DELTA_NATIVE_REVIEW'))
(qa/'delta_index.json').write_text(json.dumps(dict(base=info(base),record=info(rec),priorReview=info(Z/'qa/r03_c01_v1_internal_review_20261016.json'),crops=delta),indent=2)+'\n')
statepath=Z/'root-current-selection-20261012.json';state=json.loads(statepath.read_text(encoding='utf-8-sig'));entry=state['tiles']['r03_c01'];entry.update(candidate=info(base),record=info(rec),internalClosurePassed=False,formalAccepted=False,repairStatus='Four native local repairs adopted after original-scale mask views; v5 changed standard crop review pending.',currentDeltaIndex=info(qa/'delta_index.json'));statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(finalImage=info(base),deltaQa=info(qa/'delta_index.json'),changed=sum(not x['unchanged'] for x in delta))),flush=True)
