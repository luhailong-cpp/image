from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime,timezone
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parent
def read(f): return json.loads(f.read_text(encoding='utf-8-sig'))
def write(f,obj):
 tmp=f.with_name(f.name+'.writing');tmp.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');tmp.replace(f)
def sha(f): return hashlib.sha256(f.read_bytes()).hexdigest()
def rel(f): return f.relative_to(ROOT).as_posix()
cfg=read(ROOT/'builtin_q64_production/current-batch-config.json')
entries=[]
for item in cfg['candidates']:
 f=ROOT/item['file'];assert f.is_file(),f
 with Image.open(f) as im: im.load();assert im.size==(4096,4096),f
 e={**item,'sha256':sha(f),'pixels':[4096,4096],'accepted':False,'runtimePublished':False}
 for key in ['qa','assembly']:
  q=ROOT/e[key];assert q.is_file(),q;e[key+'Sha256']=sha(q)
 entries.append(e)
assert len(entries)==8 and len({(e['appearance'],e['tile']) for e in entries})==8
baseRecords=list((ROOT/'builtin_q64_r10_c07/native').glob('r*.record.json'))
for d in (ROOT/'builtin_q64_production').glob('*/*'):
 baseRecords.extend((d/'native').glob('r*.record.json'))
assert len(baseRecords)==128,len(baseRecords)
sourceEvidence=[]
for rf in baseRecords:
 record=read(rf);native=rf.with_name(rf.name.replace('.record.json','.png'))
 assert native.is_file(),native
 with Image.open(native) as im: assert im.size==(1254,1254),native
 h=sha(native);assert h==record['outputSha256'],rf
 original=Path(record['sourceOutputPath']);assert original.is_file() and sha(original)==h,rf
 assert record.get('route') in ['builtin','builtin_image_gen'],rf
 assert not record.get('finalArtUpscaled',False),rf
 sourceEvidence.append({'record':rel(rf),'recordSha256':sha(rf),'native':rel(native),'sha256':h,'pixels':[1254,1254]})
repairEvidence=[]
for rp in cfg['repairRecords']:
 f=ROOT/rp;assert f.is_file(),f;record=read(f)
 assert record.get('route') in ['builtin','builtin_image_gen'],f
 src=Path(record['sourceOutputPath']);assert src.is_file(),src
 local=f.with_name(f.name.replace('.record.json','.png'))
 if not local.is_file():
  declared=Path(record.get('outputPath',record.get('outputFile','')))
  possible=[declared] if declared.is_absolute() else [a/declared for a in f.parents if a==ROOT or ROOT in a.parents]
  found={v.resolve() for v in possible if v.is_file()};assert len(found)==1,(f,found)
  local=next(iter(found));assert ROOT in local.parents,local
 assert local.is_file(),local
 assert sha(local)==sha(src)==record['outputSha256'],f
 assert Image.open(local).size==(1254,1254),local
 assert not record.get('finalArtUpscaled',False),f
 repairEvidence.append({'record':rp,'recordSha256':sha(f),'nativeSourceSha256':sha(src),'nativeSourcePixels':list(Image.open(src).size)})
repairCountExpected=cfg['expectedRepairCount']
assert len(repairEvidence)==repairCountExpected,len(repairEvidence)
assert len(set(cfg['repairRecords']))==repairCountExpected,'Duplicate repair record path'
baseHashes={e['sha256'] for e in sourceEvidence};repairHashes={e['nativeSourceSha256'] for e in repairEvidence}
assert len(baseHashes)==128,'Repeated base native source'
assert len(repairHashes)==repairCountExpected,'Repeated repair native source'
assert baseHashes.isdisjoint(repairHashes),'Repair source already counted among base patches'
# Validate all catalog/plan relationships before updating any status file.
preCatalog=read(ROOT/'production_catalog.json');assert len(preCatalog['variants'])==7
preKeys=[v['city']+'_'+v['variant'] for v in preCatalog['variants']];assert len(set(preKeys))==7
assert set(e['appearance'] for e in entries)==set(preKeys)
preTotal=0;preMatched=0
for v in preCatalog['variants']:
 key=v['city']+'_'+v['variant'];plan=read(ROOT/v['completeGridPlan']);tiles=plan['tiles']
 assert len(tiles)==256 and len({t['id'] for t in tiles})==256
 preTotal+=len(tiles)
 for e in entries:
  if e['appearance']==key:
   matches=[t for t in tiles if t['id']==e['tile']];assert len(matches)==1,(key,e['tile'])
   assert matches[0]['finalPixelRect']==e['finalPixelRectXYWH']
   preMatched+=1
assert preTotal==1792 and preMatched==8
now=datetime.now(timezone.utc).isoformat()
batch={'schemaVersion':1,'updatedAtUtc':now,'scope':'Eight unique local 4K candidates, covering seven appearances; no complete 64K city','plannedDeliveryTiles':1792,'generated4KCandidateCount':8,'acceptedDeliveryTileCount':0,'wholeCityCompletedCount':0,'baseNativeDetailPatchCount':128,'additionalNativeRepairCount':len(repairEvidence),'nativeDetailPatchCountIncludingRepairs':128+len(repairEvidence),'referenceImagesExcludedFromDetailCount':True,'detailCountMeaning':'All generated base and repair sources retained, including base patches superseded in later candidates; not only final selected contributors','sourceArtUpscaled':False,'candidates':entries,'baseNativeEvidence':sourceEvidence,'nativeRepairEvidence':repairEvidence,'scopeDecisionPending':True,'runtimePublished':False}
write(ROOT/'builtin_q64_production/current-batch.json',batch)
s=read(ROOT/'status.json')
s.update({'schemaVersion':3,'updatedAtUtc':now,'status':'eight_unique_local_4K_candidates_generated_seven_full_64K_cities_incomplete','scope':batch['scope'],'activePlan':'builtin_q64_production/current-batch.json','activeWorkingDirectory':'builtin_q64_production','generated4KCandidateCount':8,'baseNativeDetailPatchCount':128,'additionalNativeRepairCount':len(repairEvidence),'nativeDetailPatchCount':128+len(repairEvidence),'candidateFiles':[e['file'] for e in entries],'currentBatch':'builtin_q64_production/current-batch.json','completedCurrentDeliveryTiles':0,'completedWholeCityCount':0,'allSevenMapVariantsComplete':False,'runtimePublished':False,'candidatePreview':'builtin_q64_production/current-batch-overview.jpg','candidateVisualReview':'Each candidate reviewed locally; known seam issues recorded in linked QA. Whole-city, external-neighbor, foreground and closest-camera acceptance incomplete.','completedDeliveryCountMeaning':'Accepted production tiles only. Eight unique generated local candidates remain unaccepted; alternate assembly versions do not add to the count.','scopeDecision':{'pending':True,'reason':'Observed native output1254 square despite higher requested dimensions. Current16-detail-patches-per4K scheme requires28672 detail generations across1792 planned tiles, plus references and seam repairs.','requestedWholeCityPixels':[65536,65536],'requestedTilePixels':[4096,4096],'minimumBaseGenerationsUnderCurrentScheme':28672,'userResponseReceived':False}})
for key in ['candidateFile','candidateSha256','candidatePixels']:s.pop(key,None)
write(ROOT/'status.json',s)
cat=read(ROOT/'production_catalog.json');cat['updatedAtUtc']=now;cat['currentBatch']='builtin_q64_production/current-batch.json'
for v in cat['variants']:
 key=v['city']+'_'+v['variant'];es=[e for e in entries if e['appearance']==key]
 assert es,key
 v.update({'state':'local_4K_candidates_generated_full_64K_production_incomplete','generated4KCandidateCount':len(es),'productionTilesAccepted':0,'runtimePublished':False,'activeWorkingDirectory':'builtin_q64_production/'+key,'currentCandidates':es})
 for k in ['currentCandidateFile','currentCandidateSha256']:v.pop(k,None)
 planFile=ROOT/v['completeGridPlan'];plan=read(planFile)
 plan.update({'updatedAtUtc':now,'generated4KCandidateCount':len(es),'productionTilesAccepted':0,'runtimePublished':False,'wholeCityComplete':False})
 for tile in plan['tiles']:
  matches=[e for e in es if e['tile']==tile['id']]
  if matches:
   e=matches[0];tile.update({'state':'generated_candidate_pending_acceptance','candidateFile':'../'+e['file'],'candidateSha256':e['sha256'],'candidatePixels':[4096,4096],'qa':'../'+e['qa'],'accepted':False})
 assert len(plan['tiles'])==256
 write(planFile,plan)
write(ROOT/'production_catalog.json',cat)
# QA contact sheet. Only thumbnails are downsampled; no delivered artwork is changed.
board=Image.new('RGB',(2200,1460),'#f5f3ed');draw=ImageDraw.Draw(board)
font=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',26);small=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',20);title=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',38)
draw.text((30,18),'主城 Q 版重制 · 8 个局部 4K 候选',font=title,fill='#182c36')
draw.text((32,75),'覆盖 4 城 7 套外观｜每张4096×4096｜完整64K主城：0/7｜正式验收：0/1792',font=small,fill='#8a4524')
for i,e in enumerate(entries):
 x=30+(i%4)*545;y=126+(i//4)*655
 im=Image.open(ROOT/e['file']).convert('RGB').resize((510,510),Image.Resampling.LANCZOS);board.paste(im,(x,y))
 draw.text((x,y+520),e['displayName']+' '+e['tile'],font=font,fill='#182c36')
 draw.text((x,y+562),'局部候选 · 接缝与实机验收未完成',font=small,fill='#8a4524')
# Grid-coordinate label only; these are local crops, not full-city previews.
 draw.text((x,y+597),'整城网格坐标：'+e['tile'],font=small,fill='#4a5960')
board.save(ROOT/'builtin_q64_production/current-batch-overview.png');board.save(ROOT/'builtin_q64_production/current-batch-overview.jpg',quality=82)
preview=board.resize((1650,1095),Image.Resampling.LANCZOS);preview.save(ROOT/'builtin_q64_production/current-batch-overview-preview.jpg',quality=78)
table=['| 外观 | 图块坐标 | 4K候选 | 检查记录 |','| --- | --- | --- | --- |']
for e in entries:table.append(f"| {e['displayName']} | {e['tile']} | [无损PNG]({e['file']}) | [QA]({e['qa']}) |")
md='# 主城64K / 单块4K重制\n\n'
md+='本批累计生成 **8个独立坐标的4096×4096局部候选**，覆盖天墉、蓬莱、东海、揽仙4城7套外观。**完整64K整城为0/7套，正式验收图块为0/1792块**。候选数量不包括同一坐标的旧版、返修版、布局参考或过程裁图。\n\n'
md+=f"累计保留128张基础原生1254×1254细节图，另有{len(repairEvidence)}张原生局部返修图。最终美术未放大；先拼合重叠区域，再裁为4096×4096。天墉相邻两块先在8192×4096画面中共同处理，再切回4K，重拼像素一致。候选仍有局部接缝问题，具体见各自QA，尚未替换客户端地图。\n\n"
md+='[本批总览](builtin_q64_production/current-batch-overview.jpg) · [逐图来源与数量核验](builtin_q64_production/current-batch.json) · [状态JSON](status.json)\n\n'+'\n'.join(table)+'\n\n'
md+='## 目标与可行性\n\n用户目标仍为每套65536×65536、16×16块、每块4096×4096。旧图和1254²整城参考只约束布局，不计为高清成品。按当前每块需要16张原生细节图的方案，1792块共需28672张原生细节图，另需参考和接缝返修；本批没有完成这一总量。已向用户说明规模并询问继续64K分批制作，或调整为先完成全部7套整城4K/8K；尚未收到范围变更答复。\n\n'
md+='## 路线与检查\n\n本批使用内置image_gen，按用户选择的GPT Image2.0路线和最高可用质量要求出图，未调用单独计费API。工具没有可指定的模型、尺寸或质量参数；实际新图均逐张量尺寸并保存来源与提示词，不把请求尺寸当作输出尺寸，不把未核实型号作为确认结论。\n\n'
md+='清晰度与接缝检查包括局部总览、原像素细节、内部交点；部分候选补查了内部接缝全长。天墉保留v1、v2、v3及返修失败/残留缺陷记录。完整外围相邻图块、导航对齐、独立前景、最近镜头、跨块移动与设备表现尚未验收，因此未发布生产manifest。\n\n'
md+='客户端按可见范围加周围一圈加载、目标外观图块齐备后整体切换的实现已经完成；既有验证21/21通过、运行时代码编译0错误，见[客户端验证](E:/work/mmorpg-client/Docs/VerificationEvidence/city-tiles4k-atomic-20260917/summary.json)。本批未修改客户端代码，以上不代表新美术已完成实机验收。\n\n'
md+='## 统一需求话术\n\n所有主城地图统一按更Q版、圆润饱满、明亮干净的方向重制，使用内置GPT Image路线的最高可用画质。当前目标为每套整城65536×65536，按16×16切成256张4096×4096图块；每块重新制作真实高清细节，保持道路、建筑、台阶、水岸、出入口和镜头角度一致，重叠拼接后再裁切，逐条检查所有接缝。客户端按视野加载并预载邻块。完成的原生图、拼接图、切图清单和验收记录必须可追溯，未通过验收的不计为完成。\n\n'
md+='[主城地图切图规范](E:/work/image/主城地图切图规范.md)只规定主城切图和美术交付规则；客户端实现见[CityTiles4K](E:/work/mmorpg-client/Docs/CityTiles4K.md)。\n\n'
md+='## 保留的历史资料\n\n- [七套Q版整城布局参考（1254²，不是64K成品）](builtin_q64_all_city_references/README.md)\n- [1792块离线坐标计划](q64_production_plans/README.md)\n- [最初天墉Q版4K局部候选](builtin_q64_r10_c07/README.md)\n- [旧4K试作](builtin_4x4/plan.json)、[32K密度试作](builtin_density32k_r05_c04/plan.json)\n- [停用的GPT Image2.5 API执行包](q64_gpt25/执行包.md)，不用于本轮、不等待Key。\n'
hist=ROOT/'history';hist.mkdir(exist_ok=True);backup=hist/'README-before-local-batch-20260917.md'
if not backup.exists():shutil.copyfile(ROOT/'README.md',backup)
(ROOT/'README.md').write_text(md,encoding='utf-8')
(ROOT/'builtin_q64_production/README.md').write_text('# 本批主城4K局部候选\n\n累计8个独立坐标候选，覆盖4城7套外观；完整64K整城0套，正式验收0块。\n\n[完整制作说明与逐图链接](../README.md) · [原生来源与候选清单](current-batch.json) · [本批总览](current-batch-overview.jpg)\n',encoding='utf-8')
grid=ROOT/'q64_production_plans/README.md'
grid.write_text('# 全主城64K离线分块计划\n\n每套16×16共256块4096×4096，7套共1792块。这里是离线坐标计划，不是客户端生产manifest。\n\n当前已登记8个独立坐标的局部4K候选，正式验收0块、完整整城0套。候选及其来源、返修和QA见[制作总览](../README.md)。其余1784个坐标仍未生成候选；已有候选还需接缝与完整实机验收。\n\n'+ '\n'.join(f"- [{v['displayName']}]({Path(v['completeGridPlan']).name})：{v['generated4KCandidateCount']}/256个局部候选，正式验收0。" for v in cat['variants'])+'\n',encoding='utf-8')
write(ROOT/'builtin_q64_production/summary-verification.json',{'updatedAtUtc':now,'unique4KCandidateCount':8,'candidatePixelsVerified':True,'candidateHashesRecorded':True,'originalNativeSourceByteIdentityVerified':128,'nativePatchPixelsVerified':[1254,1254],'repairRecordsVerified':len(repairEvidence),'totalPlannedTiles':sum(len(read(ROOT/v['completeGridPlan'])['tiles']) for v in cat['variants']),'acceptedCount':0,'wholeCityCompletedCount':0})
print(json.dumps({'candidates':8,'baseNativePatches':128,'repairNativePatches':len(repairEvidence),'whole64KCities':0,'acceptedTiles':0,'overview':str(ROOT/'builtin_q64_production/current-batch-overview.jpg')},ensure_ascii=False,indent=2))
