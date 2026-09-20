from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
root=Path(r'E:/work/image/qdao_city_tiles_4k_20260916')
p=root/'builtin_q64_production/tianyong_festival/quad_r10_c07_c10'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
review={'schemaVersion':1,'reviewedAtUtc':now,'status':'local_native_detail_and_join_review_complete_external_neighbors_and_runtime_pending','formalAcceptance':False,'pixels':[16384,4096],'reviewed':{'newTileNativeGenerations':16,'rejectedTransparentNative':1,'crossTileBoundarySegments':[0,1024,2048,2842],'allNewTileInternalSeamBands':['vertical1024','vertical2048','vertical3072','horizontal1024','horizontal2048','horizontal3072'],'bandPixelScale':1,'repairedContexts':['boundary_lower_context.jpg','stairs_boundary_context.jpg']},'findings':['New tile paving, rock, tree and rail line continuity reviewed at original pixel scale.','Initial c09/c10 lower step tone discontinuity and small edge offsets repaired using2 native generations; both composited contexts rechecked.','Previous c07/c08 and c08/c09 local review remains in linked parent evidence.'],'remaining':['All outer neighboring rows/columns incomplete.','Closest-camera and movement verification pending.','Foreground separation and navigation registration pending.','Subtle hand-painted joint waviness must be assessed at game camera scale.'],'evidenceParent':str(p.parent/'triple_r10_c07_c09/qa_v3/visual-review.json'),'sourceArtUpscaled':False,'limitedSubpixelRegistrationUsed':True,'assemblySha256':sha(p/'assembly_v2.json'),'runtimePublished':False}
(p/'qa_v2/visual-review.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
cfgfile=root/'builtin_q64_production/current-batch-config.json';cfg=json.loads(cfgfile.read_text(encoding='utf-8'))
others=[e for e in cfg['candidates'] if e['appearance']!='tianyong_festival']
tian=[]
for c in (7,8,9,10):
 base='builtin_q64_production/tianyong_festival/quad_r10_c07_c10/'
 tian.append({'appearance':'tianyong_festival','displayName':'天墉城节庆','tile':f'r10_c{c:02}','file':base+f'output_v2/r10_c{c:02}.png','assembly':base+'assembly_v2.json','qa':base+'qa_v2/visual-review.json','finalPixelRectXYWH':[(c-1)*4096,36864,4096,4096],'worldRect':{'x':50+(c-1)*18.75,'z':112.5,'width':18.75,'height':18.75}})
cfg['candidates']=tian+others
new=['builtin_q64_production/tianyong_festival/r10_c10/rejected/r02_c03.record.json']+[f'builtin_q64_production/tianyong_festival/quad_r10_c07_c10/repairs/v2/native/{n}.record.json' for n in ('boundary_lower','stairs_boundary')]
for r in new:
 if r not in cfg['repairRecords']:cfg['repairRecords'].append(r)
cfg['expectedRepairCount']=len(cfg['repairRecords']);cfgfile.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8')
sf=root/'status.json';s=json.loads(sf.read_text(encoding='utf-8'))
s['continuationWork']['tianyong']='r10_c07..c10 four-tile strip locally reviewed; extend upward to r09_c07 using same geometry and exact neighbor overlap.'
s['lastTransientInterruption']={'kind':'parallel_task_usage_error','resolved':True,'note':'Several parallel tasks reported usage limit; fresh ordinaryUsageAllowed=true and subsequent commands/native generations succeeded. No credits purchased or reset redeemed.','recordedAtUtc':now}
sf.write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
print('Tianyong4 unique coordinates registered; failed image counted only as retained source.')
