from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
B=Path(__file__).resolve().parents[1];out=B/'pipeline-tools/internal-lower-left-allocation-20261016-v01.json';assert not out.exists()
tiles=[f'r{r:02d}_c{c:02d}' for r in range(13,17) for c in range(1,5)]
audit=[]
for tile in tiles:
 t=B/tile;found=[]
 for sub in ['native','refinement','pipeline/receipts','pipeline/returned-native']:
  d=t/sub
  if d.exists():found.extend(str(p) for p in d.rglob('*') if p.is_file() and (p.suffix.lower()=='.png' or 'generation.json' in p.name or 'receipt' in p.name or 'tool-result' in p.name))
 audit.append({'tile':tile,'currentNativeOrReturnedEvidence':found})
assert not any(x['currentNativeOrReturnedEvidence'] for x in audit),'Actual source/returned conflict; do not allocate'
d={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'scope':'internal subagent redistribution only; main-city Southwest64 remains root responsibility','worker':'/root/sw_col5_resume_20261016','previousWorker':'/root/sw_left_resume_20261016','tiles':tiles,'status':'allocated_after_actual_empty_source_check_and_original_worker_exclusion','startAfter':'Finish r15_c05 full16 native QA and provide candidate/review paths, then begin r13_c01','originalWorkerConfirmation':'Live sw_left_resume_20261016 confirmed no native, no selected source and no in-flight generation in these16; explicitly excluded these16 from further production. Root verified current actual files independently.','outputRule':'Write only these exact Southwest tile directories and existing own col5 directories. Do not write root catalog/progress, other tiles, shared Git or global manifest. Preserve all originals/new versions.','audit':audit,'firstTile':'r13_c01','externalAnchors':'Use actual current native context only when available and geometrically sound; truthful missing-neighbor declaration otherwise. Never infer passed external QA.','formalAccepted':False}
out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'allocation':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'tiles':tiles,'conflicts':0}))

