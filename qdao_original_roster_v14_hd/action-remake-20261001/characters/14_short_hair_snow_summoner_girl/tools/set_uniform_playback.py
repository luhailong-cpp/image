"""Current authoritative timing: 16 frames x 75ms; retain art review state."""
from pathlib import Path
from datetime import datetime, timezone
import json
R=Path(__file__).resolve().parents[1]
now=datetime.now(timezone.utc).isoformat()
timing={'schemaVersion':2,'updatedAt':now,'defaultCycleMs':1200,'frameCount':16,'frameDurationMs':75,'uniform':True,'availablePlaybackRates':[1,0.25],'scope':'offline sprite playback; client movement speed not modified','selectionReason':'用户指定1200ms完整循环，16帧均匀75ms；移除旧快档和相位权重。','status':'user_selected_uniform_timing','directions':{}}
for d in ['N','NE','E','SE','S','SW','W','NW']:
    p=R/'run'/d/'grounding-review.json'
    j=json.loads(p.read_text(encoding='utf-8-sig'))
    for key in ['oldCycleMs','comparedUniformCycleMs','comparedCycleMs']:j.pop(key,None)
    j.update(selectedCycleMs=1200,durationsMs=[75]*16,timingUpdatedAt=now,timingReason=timing['selectionReason'])
    for row in j['frames']:row['durationMs']=75
    p.write_text(json.dumps(j,ensure_ascii=False,indent=2),encoding='utf-8')
    timing['directions'][d]={'cycleMs':1200,'durationsMs':[75]*16,'phaseReview':p.relative_to(R).as_posix(),'status':'uniform_75ms_user_selected'}
(R/'run-timing.json').write_text(json.dumps(timing,ensure_ascii=False,indent=2),encoding='utf-8')
for name in ['build_manifest_preview.py','build_previews.py']:
    p=R/'tools'/name
    t=p.read_text(encoding='utf-8').replace("16,30),'hit'","16,75),'hit'").replace('[45]*16','[75]*16')
    p.write_text(t,encoding='utf-8')
p=R/'tools/build_direction_review.py'
t=p.read_text(encoding='utf-8').replace('每圈720ms','每圈1200ms · 75ms/帧').replace('480/640/720/800对照','节奏与逐帧检查').replace('逐向按实图承重配时','各方向16帧均匀75ms')
p.write_text(t,encoding='utf-8')
p=R/'tools/verify_delivery.py'
t=p.read_text(encoding='utf-8').replace("assert len(g['durationsMs'])==16 and sum(g['durationsMs'])==720","assert g['durationsMs']==[75]*16 and g['cycleMs']==1200")
p.write_text(t,encoding='utf-8')
p=R/'bamboo-reference.html'
t=p.read_text(encoding='utf-8').replace('两组各720ms','两组在本页均以1200ms播放').replace('t%720','t%1200').replace('Array(16).fill(45)','Array(16).fill(75)').replace(')%16)*45',')%16)*75')
p.write_text(t,encoding='utf-8')
p=R/'tools/finalize_review_metadata.py'
t=p.read_text(encoding='utf-8').replace('480/640/720/800 comparison; final720ms run','uniform 75ms x 16 = 1200ms run').replace("'N03/11 wider compression accepted at normal size after direction review.',",'')
p.write_text(t,encoding='utf-8')
(R/'tools/update_run_timing.py').write_text("import runpy\nfrom pathlib import Path\nrunpy.run_path(str(Path(__file__).with_name('set_uniform_playback.py')), run_name='__main__')\n",encoding='utf-8')
(R/'tools/update_timing_comparison.py').write_text("from pathlib import Path\nR=Path(__file__).resolve().parents[1]\n(R/'timing-grounding.html').write_text((R/'tools/timing_template.html').read_text(encoding='utf-8'),encoding='utf-8')\n",encoding='utf-8')
(R/'timing-grounding.html').write_text((R/'tools/timing_template.html').read_text(encoding='utf-8'),encoding='utf-8')
print('Eight run directions: 16 x 75 ms = 1200 ms. Combat timing unchanged.')
