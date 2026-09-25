from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('attempt');p.add_argument('--contact',required=True);p.add_argument('--issue',default='Full-loop and actual composite edge approval pending root review.');p.add_argument('--decision',default='provisional_phase');p.add_argument('--leading',default='');p.add_argument('--support',default='');p.add_argument('--select',action='store_true');a=p.parse_args()
path=HERE.parents[1]/'10-generation'/a.attempt/'raw.png'
review_path=HERE/'visual-review-20260923.json';doc=json.loads(review_path.read_text(encoding='utf-8'));row={'attempt':a.attempt,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'anatomicalLeadingLeg':a.leading or None,'supportLeg':a.support,'contactState':a.contact,'decision':a.decision,'issue':a.issue,'edgeLight':'pending_root_composite_review','edgeDark':'pending_root_composite_review','loop30ms':'not_tested_by_subagent','reviewedAt':datetime.now(timezone.utc).isoformat(),'method':'actual generatedImage or view_image'}
doc['rows']=[r for r in doc['rows'] if r['attempt']!=a.attempt]+[row];doc['reviewedAt']=row['reviewedAt']
# Keep each new review independently durable even if another window temporarily locks the aggregate.
entry=HERE/('visual-review-'+a.attempt+'.json');entry.write_text(json.dumps(row,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
try:review_path.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
except OSError as exc:print('Aggregate review pending: '+str(exc))
if a.select:
 slot=a.attempt.split('-v')[0];dest=HERE/'selection.json';sel=json.loads(dest.read_text(encoding='utf-8'));sel[slot]={'archive':a.attempt,'review':a.decision+': '+a.contact+' '+a.issue};dest.write_text(json.dumps(sel,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(row))
