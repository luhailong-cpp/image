"""Explicitly bind every staged 06-work PNG for an immutable mixed review-set."""
from pathlib import Path
import argparse,hashlib,json
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
WORK=HERE.parent/'06-work/candidate/06_thunder_caster_boy'
OLD=ROOT.parent/'qdao_original_roster_v13/candidate/06_thunder_caster_boy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--known-issue',action='append',default=[]);a=p.parse_args()
assert not a.output.exists(),'Preserve each prior selection JSON.'
records=json.loads((WORK/'processing/frame-sources.json').read_text(encoding='utf-8'))
overrides={};expected={}
for path in sorted((WORK/'walk').glob('*/*.png')):
    key=path.relative_to(WORK).as_posix()
    assert not (OLD/key).exists(),'Cannot override retained V13 action: '+key
    rec=records[key]
    assert sha(path)==rec['output_sha256']
    overrides[key]={'path':str(path.resolve()),'sha256':sha(path),'selected_revision':Path(rec['source']['path']).parts[1],
                    'visual_status':'root_selected_unapproved'}
    expected[key]={'path':str(path.resolve()),'sha256':sha(path)}
out={'overrides':overrides,'expected_sources':expected,'known_rework_slots':a.known_issue,
     'selection_evidence':{'action':'Explicit invocation binds all current 06-work slots; file count is not art approval.'}}
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected_work_frames':len(overrides),'selection':str(a.output)}))
