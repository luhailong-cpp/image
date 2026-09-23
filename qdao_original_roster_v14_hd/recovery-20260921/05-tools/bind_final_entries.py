from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[3];C=R/'qdao_original_roster_v14_hd/recovery-20260921';P=C/'05-delivery-preview';F=P/'final'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((F/'manifest.json').read_text(encoding='utf-8'))
for p in (F/'preview').iterdir():
 if p.suffix.lower() not in ('.png','.gif'): continue
 d=p.name.split('-')[0]
 inputs=[{'path':'runtime/'+r['path'],'sha256':r['sha256']} for r in m['files'] if r['path'].startswith('walk/'+d+'/')]
 out={'schema':'qdao-derived-preview-v1','operation':'deterministic_preview_composite_only_no_AI','source_pngs':inputs,'output':p.relative_to(F).as_posix(),'sha256':sha(p),'display_only_not_runtime_asset':True,'frame_duration_ms':30 if p.suffix=='.gif' else None,'cycle_ms':480 if p.suffix=='.gif' else None}
 p.with_suffix(p.suffix+'.generation.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for name in ['FINAL-PACKAGE-CHECK-20260923.json','FINAL-PACKAGE-CHECK-20260923.md']:
 (F/name).write_bytes((C/'05-audit'/name).read_bytes())
selection=P/'selected-overrides.json'
s=json.loads(selection.read_text(encoding='utf-8-sig'));s['status']='historical_selection_retired_after_final_delivery';s['current_delivery']='final/manifest.json';s['historical_source_paths_may_be_deleted']=True
selection.write_text(json.dumps(s,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
for p in (P/'revisions').glob('*/index.html'):
 p.write_text('<!doctype html><meta charset="utf-8"><p>05历史预览图片已按保留规则清理。<a href="../../final/index.html">打开最终八方向预览</a></p>',encoding='utf-8')
(C/'05-audit/preview.html').write_text('<!doctype html><meta charset="utf-8"><p>05旧NE审阅已完成。<a href="../05-delivery-preview/final/index.html">打开最终八方向预览</a></p>',encoding='utf-8')
current={'character_id':'05_celestial_musician_girl','status':'offline_accepted_with_nonblocking_notes','final_manifest':str(F/'manifest.json'),'final_manifest_sha256':sha(F/'manifest.json'),'runtime':str(F/'runtime'),'preview':str(F/'index.html'),'walk':128,'idle':8,'portrait':1,'client_integration':False,'raw_sources':'historical_source_records_only_after_authorized_cleanup'}
for p in [P/'current.json',R/'qdao_original_roster_v14_hd/candidate/05_celestial_musician_girl/CURRENT-DELIVERY.json',R/'qdao_original_roster_v13/candidate/05_celestial_musician_girl/CURRENT-DELIVERY.json']:
 p.write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('Current entries rebound, derived previews recorded')
