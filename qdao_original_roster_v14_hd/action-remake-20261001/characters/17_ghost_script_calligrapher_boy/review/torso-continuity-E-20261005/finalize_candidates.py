from pathlib import Path
import json,hashlib,datetime
B=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
choices=[('04','run-E-04-v7'),('05','run-E-05-v5'),('06','run-E-06-v7'),('07','run-E-07-v6')]
details={
'run-E-04-v7':['以v6单主图继续仅缩小降低远卷袖隆起，使远袖从躯干后缘露出并接原卷上杆手。','近右笔肩及跨胸袖、胸襟和前腰白片保留；头腿与两手位置肉眼保留。','原生、等比原帧对照均已实际查看；无新增手/物；原生和1024四边alpha>128全部0。'],
'run-E-05-v5':['root已原生静态通过作为本轮基准；动态与整段合审仍由root进行。','近右笔袖跨胸遮住大半胸饰，远左卷臂后摆，白前襟及腰前衣片可见。'],
'run-E-06-v7':['近右笔袖跨胸、远左卷臂后摆身份保留；白前襟开口和前腰可读。','原始弯膝与两靴相位保留；轻微布褶和边缘重绘，画面位置微差不单独判失败。','1024右边仅1px透明余量，但alpha>128无触边；根端可结合实播与边界要求合审。'],
'run-E-07-v6':['近右笔袖跨胸、远左卷臂后摆，白前襟保持胸前家族。','原始两腿前后伸展相位和靴轴保留；轻微头发/布褶轮廓差异，无确证身份或相位退步。']
}
selected=[]
for frame,key in choices:
 p=B/'staging'/f'{key}.png'; rec=p.with_suffix('.png.generation.json'); d=json.loads(rec.read_text(encoding='utf-8'))
 d['review']={'status':'static_candidate_root_playback_pending','visualObservations':details[key],'formalAcceptance':False,'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 rec.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 selected.append({'direction':'E','frame':int(frame),'key':key,'file':f'staging/{key}.png','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'metrics':f'review/torso-continuity-E-20261005/{key}.metrics.json','observations':details[key],'formalAcceptance':False})
badkey='run-E-04-v5'; rec=B/'staging'/f'{badkey}.png.generation.json'; d=json.loads(rec.read_text(encoding='utf-8'))
d['review']={'status':'rejected','reasons':['AI copied E05 leg/scroll placement rather than preserving E04 phase.','Three hands: original top-scroll-rod grasp remains plus copied scroll-edge hand.'],'replacement':'run-E-04-v7','formalAcceptance':False}
rec.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
result={'status':'assigned_E04_E06_E07_candidates_complete_root_merge_pending','scope':'E04/E05/E06/E07 upper-torso continuity only; E08–10 cast_finish; E11 root','latestTimingTarget':{'frameCount':16,'frameMs':60,'cycleMs':960,'timingFilesChangedByThisAgent':False},'selectedCandidates':selected,'rejected':[{'key':badkey,'sha256':d['sha256'],'reasons':d['review']['reasons']}],'runtimeOrManifestChanged':False,'globalAcceptance':False,'remaining':'Root combines all E04–11 and W04–10 then performs actual 60ms playback; these static candidates are not final animation acceptance.'}
(O/'progress.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(O/'selection-E04-E07.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'selected':[{k:r[k] for k in ['key','sha256']} for r in selected],'rejected':badkey},ensure_ascii=False))
