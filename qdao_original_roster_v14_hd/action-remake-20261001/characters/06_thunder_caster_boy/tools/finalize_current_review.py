"""Bind completed offline work to the exact 196 current frames; never infer approval from counts."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
from current_run_pairs import current_run_pairs,SOURCES
R=Path(__file__).resolve().parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda name:json.loads((R/name).read_text(encoding='utf-8-sig'))
native=read('review/native_export_verification_20261004.json')
tech=read('review/technical.json')
playback=read('review/current_playback_evidence_20261004.json')
assert native['passed'] and native['runtimeFrames']==196 and native['uniqueNativeSources']==196
assert tech['technical_ok_slot_count']==196 and not tech['missing_slot_count'] and not tech['unexpected_runtime_files']
assert not any(a['technical_issues'] or a['provenance_issues'] for a in tech['assets'])
assert playback['completed'] and playback.get('passed') and not playback['errors']
assert len(playback['runs'])==14
pairs=current_run_pairs();assert len(pairs)==128
combat=read('review/combat_final_independent_20261004.json')
combat_rows=combat.get('frames',[])
assert len(combat_rows)==68,'Independent combat report must cover current68'
assert not combat.get('unresolvedBlockingIssues',[]),'Combat issues unresolved'
indexed={f.get('file',f.get('path')):f for f in combat_rows}
observed={f['file']:f for f in native['records']}
playback_sources={f.get('path',f.get('file')):f['sha256'] for f in playback['sourceFrames']}
frames=[]
for rel,f in sorted(observed.items()):
    digest=sha(R/rel);assert digest==f['sha256']==playback_sources[rel]
    if '/run/' in rel:
        c=pairs[rel];assert c['sha256']==digest
        source=c['sourceReview']
    else:
        c=indexed[rel];assert c['sha256']==digest
        source='review/combat_final_independent_20261004.json'
    frames.append({'file':rel,'sha256':digest,'staticReview':source,'reviewResult':'当前手脚/方向与持物逐帧检查完成','nativeVerification':'review/native_export_verification_20261004.json'})
out={'recordedAt':datetime.now(timezone.utc).isoformat(),'character':'06_thunder_caster_boy','localWorkComplete':True,'completionScope':'本机196张素材、手脚/方向修正、离线正常慢放逐帧预览、来源与合并交接','frames':frames,'staticReviewedFrames':196,'staticReports':['review/'+s for s in SOURCES]+['review/combat_final_independent_20261004.json'],'playbackEvidence':'review/current_playback_evidence_20261004.json','offlinePlaybackVerifiedSequences':14,'userFinalApproved':False,'clientIntegrated':False,'clientRuntimeVerified':False,'modelTarget':{'model':'gpt-image-2.5-sunburst','quality':'max'},'actualSubmittedModel':None,'actualSubmittedQuality':None,'actualReturnedModel':None,'actualReturnedQuality':None,'remainingAcceptance':['客户端根点和位移速度标定','游戏内滑步与触地/命中/释放时刻','用户最终动态观感确认'],'knownUnresolvedSpriteDefects':[],'limits':'静态实际看图与真实浏览器播放功能分别记录；不把自动采样当成用户美术批准。'}
(R/'review/CURRENT_REVIEW.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'currentReviewedFrames':len(frames),'localWorkComplete':True,'clientIntegrated':False}))
