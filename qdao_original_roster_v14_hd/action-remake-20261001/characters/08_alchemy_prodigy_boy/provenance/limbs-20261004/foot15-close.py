from pathlib import Path
import json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
p=ROOT/'generation/limbs-20261004/foot-ne15/NE15-v2.png';r=Path(str(p)+'.generation.json')
record=json.loads(r.read_text(encoding='utf-8-sig'));sha=hashlib.sha256(p.read_bytes()).hexdigest();assert record['sha256']==sha
reason='左下支撑靴由宽侧向横钩收为窄后视NE纵深，白鞋头只留细远端边缘；髋膝踝延伸与鞋掌长轴衔接，保留自然抬跟及前掌末段推蹬。'
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat()
record.update(visualStatus='static_reviewed',staticReviewed=True,reviewedAt=stamp,reviewNotes=reason,dynamicAccepted=False,exported=False)
r.write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
selection={'run/NE/15':{'source':p.relative_to(ROOT).as_posix(),'reason':reason,'staticReviewed':True,'sha256':sha,'generationRecord':r.relative_to(ROOT).as_posix(),'inputRuntimeSHA256':hashlib.sha256((ROOT/'runtime/run/NE/15.png').read_bytes()).hexdigest()}}
(OUT/'foot15-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding='utf-8')
review={'reviewedAt':stamp,'slot':'run/NE/15','selected':'generation/limbs-20261004/foot-ne15/NE15-v2.png','result':'static_reviewed','reason':reason,'comparison':'Current NE15 versus selected whole-canvas1254->1024 offset0; final neighbor review used NE14-v4, NE15-v2 and current NE16.','neighborEvidence':'provenance/limbs-20261004/foot15-neighbor-contact.jpg','comparisonEvidence':'provenance/limbs-20261004/foot15-v2-compare.jpg','upper650AlphaIoU':0.9832868031909457,'supportBottomYCurrent':954,'supportBottomYCandidate':949,'notes':['5px contact-depth difference; no whole-body shift, no bbox fit.','Small far toe-cap rim retained as perspective; broad horizontal hook removed.','Current frame numbering and75ms unchanged; no cyclic renumbering.'],'unresolvedOwnedItems':[],'clientValidated':False,'writeStatus':'stopped_after_this_record'}
(OUT/'foot15-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'selected':1,'sha256':sha,'stoppedWriting':True}))
