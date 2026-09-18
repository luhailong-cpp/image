from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib
root=Path(r'E:/work/image/qdao_city_tiles_4k_20260916');prod=root/'builtin_q64_production'
doc=root/'跨窗口交接-全主城高清重制-20260917.md';assert doc.is_file()
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,o:p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
expected=[f'r{r:02}_c{c:02}' for r in range(1,5) for c in range(1,5)]
targets=[('tianyong_festival','r09_c08',3),('penglai_day','r09_c12',16),('penglai_mid_autumn','r09_c12',4),('lanxian_day','r08_c08',0),('lanxian_spring','r08_c08',0),('donghai_day','r08_c10',0),('donghai_lantern','r08_c10',0)]
snap=[]
for app,tile,count in targets:
 p=prod/app/tile;records=sorted((p/'native').glob('r*.record.json')) if p.exists() else []
 done=[]
 for rf in records:
  ident=rf.name.removesuffix('.record.json');im=p/'native'/f'{ident}.png';r=read(rf)
  assert im.is_file() and sha(im)==r['outputSha256']
  with Image.open(im) as v: assert v.size==(1254,1254)
  done.append(ident)
 assert len(done)==count,(app,tile,done)
 snap.append({'appearance':app,'tile':tile,'path':str(p),'directoryExists':p.exists(),'registeredNativeCount':len(done),'registeredIds':done,'missingIds':[i for i in expected if i not in done],'promptIds':[f.name.removesuffix('.prompt.txt') for f in sorted((p/'prompts').glob('*.prompt.txt'))] if p.exists() else []})
s=read(root/'status.json');assert s['generated4KCandidateCount']==17 and s['baseNativeDetailPatchCount']==295 and s['additionalNativeRepairCount']==85
now=datetime.now(timezone.utc).isoformat()
handoff={'createdAtUtc':now,'userRequestedHandoff':True,'handoffDocument':str(doc),'documentSha256':sha(doc),'registered4KCandidates':17,'additionalUnregisteredSingleTileCandidates':[{'appearance':'penglai_day','tile':'r09_c12','file':str(prod/'penglai_day/r09_c12/output/penglai_day_r09_c12_4k_candidate.png'),'status':'single_tile_assembly_done_visual_and_neighbor_join_pending'}],'baseNativeSources':295,'additionalNativeSources':85,'whole64KCompleted':0,'formalAcceptedTiles':0,'runtimePublished':False,'activeProductionTargets':snap,'pendingScopeQuestion':False}
write(prod/'handoff-snapshot-20260917.json',handoff)
s['status']='handoff_ready_for_user_selected_window';s['updatedAtUtc']=now
s['handoff']={'requestedByUser':True,'document':doc.relative_to(root).as_posix(),'snapshot':'builtin_q64_production/handoff-snapshot-20260917.json','preparedAtUtc':now,'newWindowNotCreatedByAssistant':True,'currentWindowProductionStoppedForHandoff':True}
s['continuationWork']={'tianyong':'r09_c08 has r01_c01,c02,c04 recorded;13 native patches missing, then join left+bottom and inspect four-way junction.','penglai':'day r09_c12 has16 and single assembly pending QA;mid_autumn has4,missingrows2-4;then triple join.','lanxian':'c07 full-seam corrections v6 merged;day c08 guides ready0native;spring c08 plan must update v5 to v6 and prepare guides after day.','donghai':'day c10 guides ready0native;lantern c10 not yet created;use selected c09 contexts and day geometry.'}
write(root/'status.json',s)
ref='[跨窗口详细交接](跨窗口交接-全主城高清重制-20260917.md)'
rd=root/'README.md';text=rd.read_text(encoding='utf-8')
if ref not in text: text=text.replace('# 主城64K / 单块4K重制','# 主城64K / 单块4K重制\n\n'+ref+' · [续作精确快照](builtin_q64_production/handoff-snapshot-20260917.json)',1)
text=text.replace('累计生成 **17个独立坐标','总清单已登记 **17个独立坐标')
rd.write_text(text,encoding='utf-8')
grid=root/'q64_production_plans/README.md';t=grid.read_text(encoding='utf-8').replace('个坐标未生成候选','个坐标未登记为当前候选');grid.write_text(t,encoding='utf-8')
print(json.dumps({'handoff':str(doc),'snapshot':str(prod/'handoff-snapshot-20260917.json'),'registeredCandidates':17,'nativeSources':380,'targetNativeCounts':[(e['appearance'],e['tile'],e['registeredNativeCount']) for e in snap],'noGenerationPerformedDuringHandoff':True},ensure_ascii=False))
