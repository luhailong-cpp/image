from pathlib import Path
import json,datetime
T=Path("D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/southeast/r13_c12")
v="p01_04_v20261016T150221_2dc6c609"
q=json.loads((T/'review'/('quick-'+v)/'evidence.json').read_text(encoding='utf-8-sig'))
q.update(reviewStatus="root_actual_native_and_both_core_joins_viewed",layoutStatus="improved_ground_only",geometryStatus="failed",formalAccepted=False,issues=["Right stone edge and grout shifted upward about 100 px.","Bottom grout shifted about 150-200 px, with brightness discontinuity."],decision="retain_best_layout_native_unselected; continue_independent_missing_patches; native_correction_target_prepared_separately")
p=T/"review"/("quick-"+v)/"root-visual-qa.json"
with p.open("x",encoding="utf-8") as f: json.dump(q,f,ensure_ascii=False,indent=2)
p=T/"active-native-map.json"; a=json.loads(p.read_text(encoding="utf-8-sig"))
assert a.get("p01_04")==v
with (T/"review"/("quick-"+v)/"active-before-unselect.json").open("x",encoding="utf-8") as f: json.dump(a,f,indent=2)
del a["p01_04"];p.write_text(json.dumps(a,indent=2),encoding="utf-8")
p=T/"progress.json";d=json.loads(p.read_text(encoding="utf-8-sig"))
d.update(activeNativeCount=len(a),status="p01_04_two_attempts_failed_retained_pending_native_edit; continuing_p03_04",formalAccepted=False)
p.write_text(json.dumps(d,indent=2),encoding="utf-8")
receipt=T/"records"/(v+".receipt.json")
record={"version":v,"status":"completed_saved_reviewed_failed_retained","completedAt":datetime.datetime.now(datetime.timezone.utc).isoformat(),"nativeSha256":q["nativeSha256"],"formalAccepted":False,"supersedesHistoricalInflightRecord":str(T/"records"/(v+".inflight.json"))}
with (T/"records"/(v+".completion.json")).open("x",encoding="utf-8") as f:json.dump(record,f,indent=2)
print(json.dumps({"activeCount":len(a),"active":a,"failedVersion":v}))

