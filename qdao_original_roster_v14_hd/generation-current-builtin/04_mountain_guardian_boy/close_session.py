"""Archive already completed outputs and inventory only; no generation or import."""
import json,hashlib,shutil,importlib.util
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('provenance',ROOT/'tools/inspect_image_provenance.py');prov=importlib.util.module_from_spec(spec);spec.loader.exec_module(prov)
new=[]
for n in (8,10,11):
    b=HERE/f'NW{n:02d}-single-v1';r=json.loads((b/'generation-receipt.json').read_text(encoding='utf-8'));src=Path(r['original_generated_file']);dst=b/'raw.png'
    if dst.exists():assert sha(dst)==sha(src)
    else:shutil.copy2(src,dst)
    (b/'prompt.txt').write_text(r['actual_request']['prompt'],encoding='utf-8',newline='')
    info=prov.inspect_image(dst);(b/'provenance.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    new.append({'direction':'NW','frame':n,'directory':str(b),'native_size':info['native_size'],'raw_sha256':sha(dst),'prompt_exact':(b/'prompt.txt').read_text(encoding='utf-8')==r['actual_request']['prompt'],'status':'saved_not_imported'})
old=ROOT.parent/'qdao_original_roster_v13/candidate/04_mountain_guardian_boy';current=ROOT/'candidate/04_mountain_guardian_boy';directions={}
for d in ('N','NE','E','SE','S','SW','W','NW'):
    retained=[n for n in range(1,17) if (old/f'walk/{d}/{n:02d}.png').exists()]
    imported=[n for n in range(1,17) if (current/f'walk/{d}/{n:02d}.png').exists() and n not in retained]
    directions[d]={'retained_v13':retained,'imported_v14_missing_slots':imported,'missing_candidate_slots':[n for n in range(1,17) if n not in retained+imported]}
inventory={'schema':1,'at_utc':datetime.now(timezone.utc).isoformat(),'character_id':'04_mountain_guardian_boy','status':'paused_by_user_incomplete','directions':directions,'retained_walk_count':sum(len(x['retained_v13']) for x in directions.values()),'new_imported_walk_count':sum(len(x['imported_v14_missing_slots']) for x in directions.values()),'retained_idle_count':sum((old/f'idle/{d}.png').exists() for d in directions),'missing_candidate_walk_count':sum(len(x['missing_candidate_slots']) for x in directions.values()),'saved_not_imported':new,'new_generation_calls_this_session':8,'paid_api_calls':0,'visual_approval':False,'client_published':False,'all_owned_generation_and_import_processes_finished':True,'known_visual_issue_frames':['NW/04','NW/06','NW/07'],'known_visual_issue':'Independent reviewer observed bright purple/red 1-2px outline on hair, staff and attachments after processing. Full direction is not approved.'}
(HERE/'HANDOFF_STATE_20260919.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(inventory,ensure_ascii=False))
