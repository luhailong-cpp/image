"""Bind root-selected pending SW/NW paths and exact SHAs, preserving all V13 slots."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];CHAR='04_mountain_guardian_boy'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
nw_path=ROOT/'recovery-20260921/04-tools/NW-diagnostic-v4/diagnostic-manifest.json'
nw=read(nw_path);selections={'schema':1,'status':'root_selected_review_pending_not_approved','character_id':CHAR,'preserve_every_existing_v13_action':True,'overrides':{},'expected_sources':{},'known_rework_slots':['walk/NW/15.png'],'review_notes':{'walk/NW/15.png':'下降相位仍待修订，本快照为待审稿，未通过素材验收。'},'selection_evidence':{'nw_diagnostic_manifest':str(nw_path),'nw_diagnostic_manifest_sha256':sha(nw_path)}}
for row in nw['frames']:
 key=f'walk/NW/{row["frame"]:02d}.png';source=Path(row['path']).resolve();assert sha(source)==row['sha256'],'NW selection changed: '+key
 selections['expected_sources'][key]={'path':str(source),'sha256':row['sha256']}
 old=ROOT.parent/f'qdao_original_roster_v13/candidate/{CHAR}'/key
 if old.exists():assert old.resolve()==source;continue
 canonical=ROOT/f'candidate/{CHAR}'/key
 if canonical.resolve()==source:continue
 origin=next(p for p in source.parents if p.name==CHAR);record=read(origin/'processing/frame-sources.json')[key];batch=record['source']['path'].split('/')[1]
 selections['overrides'][key]={'path':str(source),'sha256':row['sha256'],'selected_revision':batch,'visual_status':'root_selected_unapproved'}
for frame in (14,15,16):
 source=(ROOT/f'recovery-20260921/04-sw-staging/candidate/{CHAR}/walk/SW/{frame:02d}.png') if frame!=16 else (ROOT/f'recovery-20260921/04-generation/SW16-pose-v3/staging/candidate/{CHAR}/walk/SW/16.png')
 if frame==16:assert sha(source)=='376b8dde932a546c1accb9133d106918afd62797468fad055045db21eec5324f'
 key=f'walk/SW/{frame:02d}.png';selections['overrides'][key]={'path':str(source.resolve()),'sha256':sha(source),'selected_revision':f'SW{frame:02d}-single-v1' if frame!=16 else 'SW16-pose-v3','visual_status':'root_selected_unapproved'}
 selections['expected_sources'][key]={'path':str(source.resolve()),'sha256':sha(source)}
dest=HERE/'selections-review-set-v2.json';assert not dest.exists();dest.write_text(json.dumps(selections,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selection':str(dest),'overrides':len(selections['overrides']),'nw_manifest_sha256':sha(nw_path),'known_rework_slots':selections['known_rework_slots']},ensure_ascii=False))
