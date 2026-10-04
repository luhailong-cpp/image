from pathlib import Path
import json
root=Path(__file__).resolve().parent
p=root/'FIXED_REGISTRATION_CANDIDATE.json';r=json.loads(p.read_text(encoding='utf8'));r.pop('weights',None);r.update(frameMs=75,cycleMs=1200,phaseWeightsApplied=False,timing='Latest user instruction:16 uniform frames x75ms=1200ms; no former current options; combat unchanged');p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
p=root.parent/'cast-work'/'SEQUENCE_REVIEW.json';r=json.loads(p.read_text(encoding='utf8'));r['nativeIssueHistory']=r.pop('issues',[])
for e in r['nativeIssueHistory']:
 e['currentResolution']='targeted native repair selected; see SELECTED_REPAIRS_20261003.json' if e['frames']!=['all'] else 'root exported constant per-direction registration; full dynamic pass remains unclaimed'
r['currentOutstanding']=['root full fixed-registration playback verification','some native head/body drift may remain; only evidenced local corrections permitted, no per-frame scaling/lowest-foot snapping']
r['additionalRepairs']=['E05/E07 rear toe direction corrected; stance width retained','W15 recovered ground support through native leg extension; small returned head shift recorded']
r['fullSequencePassed']=False;p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print('Current timing and cast resolution records refreshed; historical generation records untouched')
