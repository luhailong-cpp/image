from pathlib import Path
from datetime import datetime, timezone
import hashlib, json

SESSION = Path(__file__).resolve().parent
ART = SESSION.parents[1]
sha = lambda b: hashlib.sha256(b).hexdigest()
audit = json.loads((SESSION/'audit/current_input_inventory.json').read_text(encoding='utf-8'))
inputs = [(ART/e['recordedPath'],e) for e in audit['inputRecords']]
for p,e in inputs:
    assert sha(p.read_bytes()) == e['actualSha256'], f'Concurrent record edit: {p}'
history = SESSION/'history/shared-records-before-active-focus'
assert not history.exists()
history.mkdir(parents=True)
now = datetime.now(timezone.utc).isoformat()
updates = []
for p,e in inputs:
    before = p.read_bytes()
    saved = history/p.relative_to(ART)
    saved.parent.mkdir(parents=True,exist_ok=True)
    saved.write_bytes(before)
    data = json.loads(before)
    data['activeProductionRun'] = {
        'id':'resume_single_city_20260921','updatedAtUtc':now,
        'appearance':'tianyong_festival','displayName':'天墉城节庆',
        'priority':'finish_one_appearance_before_other_cities_or_skins',
        'targetMapPixels':[65536,65536],'targetTilePixels':[4096,4096],
        'targetRows':16,'targetColumns':16,'targetTileCount':256,
        'sessionState':'builtin_q64_production/resume_single_city_20260921/session-state.json',
        'modelEvidence':'builtin_q64_production/resume_single_city_20260921/model-capability.json',
        'actualBackendModel':None,'actualQuality':None,'backendModelVerified':False,
        'historicalPathMapping':{'E:/work/':'D:/luyuan/wuxingqitan/'},
        'baselineCandidatesRemainSelected':True,'newWorkInProgressIsNotProductionDelivery':True,
        'formalAcceptedTileCount':0,'deliveryReady':False,
        'clientIntegrationOwner':'separate user window',
        'historicalContinuationTextSupersededByThisRun':True}
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    updates.append({'file':p.relative_to(ART).as_posix(),'beforeSha256':sha(before),
                    'afterSha256':sha(p.read_bytes()),'backup':saved.relative_to(SESSION).as_posix()})
readme = ART/'README.md'
before = readme.read_bytes()
(history/'README.md').write_bytes(before)
notice = '> 2026-09-21 本窗口集中制作 **天墉城节庆** 一套。新增原生图、返修和未验收候选见 [本轮实时制作记录](builtin_q64_production/resume_single_city_20260921/session-state.json)；下文24块/502原生是接手时已合并批次快照，不包含该续作目录的新来源。正式64K交付仍为0套，客户端接入由另一窗口负责。\n\n'
readme.write_text(notice+before.decode('utf-8-sig'),encoding='utf-8')
(SESSION/'shared-record-update.json').write_text(json.dumps({
    'createdAtUtc':now,'updates':updates,'candidateSelectionsChanged':False,
    'productionAcceptanceChanged':False,'historyBytesPreserved':True},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'updatedRecordCount':len(updates),'candidateSelectionsChanged':False,'history':str(history)}))
