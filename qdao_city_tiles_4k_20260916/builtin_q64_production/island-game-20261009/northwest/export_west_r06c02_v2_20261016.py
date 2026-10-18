from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
import apply_native_tile_repair as repair
Z=Path(__file__).resolve().parent
def info(p):return {'path':p.as_posix(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
v=Z/'tiles/r06_c02_candidate-v2_4096.png';rec=v.with_suffix('.native-repair.json');oldq=Z/'qa/assembly_r06_c02_candidate-v1_4096/qa_index.json';q=json.loads(oldq.read_text());im=Image.open(v).convert('RGB')
folder=Z/'qa/r06_c02_v2_internal_review';folder.mkdir(exist_ok=False)
changed=[];same=[]
for x in q['seamAndJunctionCrops']:
 crop=im.crop(x['tileCropBoxHalfOpen'])
 if np.array_equal(np.asarray(crop),np.asarray(Image.open(x['path']).convert('RGB'))):
  same.append(Path(x['path']).name)
  x['reuseBasis']='Identical unmodified native pixels to v1 crop, checked against current v2 image.'
 else:
  p=folder/Path(x['path']).name;crop.save(p);x.update(info(p));changed.append(p.name)
q['candidate']=info(v);q['record']=info(rec);q['priorIndex']=info(oldq);q['status']='changed_native_crops_pending_review_unchanged_hashes_reusable';q['changedNames']=changed;q['unchangedNames']=same
index=folder/'qa_index.json';index.write_text(json.dumps(q,indent=2)+'\n')
pixels,proof=repair.validate_base(v,rec);audit=Z/'qa/r06_c02_v2_strict_native_replay_20261016.json';audit.write_text(json.dumps({'base':info(v),'record':info(rec),'proof':proof,'all16777216PixelsReplayed':True,'visualAcceptance':False},indent=2)+'\n')
s=Z/'west-current-selection-20261012.json';sel=json.loads(s.read_text());sel['currentTile'].update(candidate=info(v),record=info(rec),qaIndex=info(index),strictReplay=info(audit),status='native16_repair_v2_changed_QA_pending')
next(x for x in sel['partialTiles'] if x['tileId']=='r06_c02')['inflightStems']=[]
s.write_text(json.dumps(sel,indent=2)+'\n')
print(json.dumps({'qa':info(index),'changed':changed,'reusedCount':len(same),'audit':info(audit)}))

