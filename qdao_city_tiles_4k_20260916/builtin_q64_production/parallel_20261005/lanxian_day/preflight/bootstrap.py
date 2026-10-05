from pathlib import Path
from datetime import datetime, timezone
import json, hashlib

ROOT = Path(__file__).resolve().parents[1]
REPO = Path('D:/work/image')
def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(name, data):
    p = ROOT / name
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

h = load(ROOT/'handoff.json')
now = datetime.now(timezone.utc).isoformat()
plan = load(h['plan']['file'])
candidates = {x['tile'] for x in h['baselineCandidates']}
queue = sorted((t for t in plan['tiles'] if t['id'] not in candidates), key=lambda t: (abs(t['row']-8)+max(0,6-t['column'],t['column']-8), abs(t['row']-8), -t['column']))
queue.sort(key=lambda t: (0 if t['id']=='r08_c09' else 1))
base = {'schemaVersion':1,'appearance':'lanxian_day','updatedAtUtc':now,'targetTiles':256,'targetTilePixels':[4096,4096],'wholeCityPixels':[65536,65536],'readyForProduction':h['readyForProduction'],'handoffSha256':sha(ROOT/'handoff.json'),'route':'builtin_image_gen','paidApiAllowed':False,'wholeCityComplete':False,'runtimePublished':False,'formalAccepted':0,'newComplete4KCandidates':0,'nativeDetailPatchesGenerated':0,'baselineCandidateCount':len(candidates),'baselineCurrent':h['baselineCurrent'],'status':'preflight_waiting_for_handoff' if not h['readyForProduction'] else 'ready_for_adjacent_native_production'}
write('progress.json',base)
write('current-work.json',dict(base,currentTile='r08_c09',currentPhase='handoff_gate',nextAction='Re-read handoff ready flag; once true verify selected source SHA and prepare west-constrained regional guide.',pixelRectXYWH=[32768,28672,4096,4096],core=1024,halo=115,patchPixels=1254,requiredNativePatches=16,sourceAudit='preflight/source-audit.json',productionCountPolicy='Only complete 4096x4096 native-pixel composites with explicit inspection coverage count; fragments and layout guides do not.',officialModelVerification={'checkedAtUtc':now,'target':load(REPO/'config/image-generation.json'),'sources':['https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','https://openai.com/index/introducing-chatgpt-images-2-5/'],'finding':'Official page lists Sunburst as most capable; max quality supported. Builtin tool exposes no model/quality selectors. Root config unchanged in shared task.','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None}))
write('production-queue.json',{'schemaVersion':1,'updatedAtUtc':now,'planSha256':sha(h['plan']['file']),'numbering':'one-based row/column; origin top-left','baselineCandidates':h['baselineCandidates'],'tiles':[{'id':t['id'],'pixelRectXYWH':t['finalPixelRect'],'worldRect':t['worldRect'],'state':'missing_native_complete_tile'} for t in queue],'next':'r08_c09','note':'Provisional nearest-neighbor expansion queue; re-evaluate frontier after each fully inspected tile. Baseline candidates are not formally accepted.'})
print(json.dumps({'ready':h['readyForProduction'],'queue':len(queue),'next':'r08_c09'}))
