"""Verify byte preservation and GIF timing; record static notes without visual approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib
from PIL import Image
import numpy as np
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--revision',required=True);parser.add_argument('--historical-snapshot',action='store_true',help='Verify pinned snapshot bytes and report subsequent mutable source drift separately.');args=parser.parse_args()
out=(HERE/'revisions'/args.revision).resolve();assert out.is_relative_to(HERE.resolve())
manifest=json.loads((out/'manifest.json').read_text(encoding='utf-8'))
results=[]
for row in manifest['files']:
 source=Path(row['source']);target=out/'runtime'/row['path'];assert sha(target)==row['sha256']
 current_source_sha=sha(source) if source.exists() else None
 source_matches=current_source_sha==row['sha256']
 assert args.historical_snapshot or source_matches, 'Source changed since snapshot: '+row['path']
 assert row['copied_byte_exact'] is True
 im=Image.open(target);assert list(im.size)==row['size'] and im.mode=='RGBA'
 a=np.array(im)[:,:,3];assert int(a.min())==0 and int(a.max())==255
 results.append({'path':row['path'],'snapshot_matches_pinned_sha256':True,'copied_bytes_equal_at_build':True,'current_source_matches_snapshot':source_matches,'current_source_sha256':current_source_sha,'pinned_sha256':row['sha256'],'source_size':row['size'],'alpha_boundary_touched':any(np.any(edge) for edge in (a[0],a[-1],a[:,0],a[:,-1]))})
checks=[]
for row in manifest['gif_checks']:
 p=out/row['path'];assert sha(p)==row['sha256'];im=Image.open(p);duration=[]
 for n in range(im.n_frames):im.seek(n);duration.append(im.info['duration'])
 assert im.n_frames==16 and duration==[30]*16
 checks.append({'path':row['path'],'sha256':sha(p),'frames':16,'durations_ms':duration,'cycle_ms':480})
notes=json.loads((HERE/'six-directions-static-notes.json').read_text(encoding='utf-8'))
report={'checked_at_utc':datetime.now(timezone.utc).isoformat(),'revision':args.revision,'status':'integrity_checked_static_notes_recorded_not_formally_approved','manifest_sha256':sha(out/'manifest.json'),'copied_actions':len(results),'snapshot_matches_pinned_sha256_actions':len(results),'current_source_byte_equal_actions':sum(r['current_source_matches_snapshot'] for r in results),'source_drift_slots':[r['path'] for r in results if not r['current_source_matches_snapshot']],'alpha_boundary_touch_count':sum(r['alpha_boundary_touched'] for r in results),'files':results,'gif_checks':checks,'six_old_complete_direction_notes':notes,'formal_approval':False,'browser_dynamic_review':False,'unity_runtime_review':False,'remaining_selection_slots':manifest['missing'],'known_rework_slots':manifest.get('known_rework_slots',[]),'review_notes':manifest.get('review_notes',{})}
(out/'audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'snapshot_matches_pinned_sha256':len(results),'current_source_byte_equal':report['current_source_byte_equal_actions'],'source_drift_slots':report['source_drift_slots'],'gif_checks':len(checks),'alpha_boundary_touches':report['alpha_boundary_touch_count'],'formal_approval':False}))
