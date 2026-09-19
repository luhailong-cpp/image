"""Rebuild the production ledger from explicit candidates and verified native evidence."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime,timezone
import json,hashlib,shutil,math
ROOT=Path(__file__).resolve().parent
def read(f):return json.loads(f.read_text(encoding='utf-8-sig'))
def write(f,o):
    tmp=f.with_name(f.name+'.writing')
    tmp.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(f)
def sha(f):return hashlib.sha256(f.read_bytes()).hexdigest()
def rel(f):return f.resolve().relative_to(ROOT.resolve()).as_posix()
def verify_native(rf):
    r=read(rf)
    assert r.get('route') in ('builtin','builtin_image_gen'),rf
    src=Path(r['sourceOutputPath']);assert src.is_file(),src
    local=rf.with_name(rf.name.replace('.record.json','.png'))
    if not local.is_file():
        declared=Path(r.get('outputPath',r.get('outputFile','')))
        possible=[declared] if declared.is_absolute() else [a/declared for a in rf.parents if a==ROOT or ROOT in a.parents]
        found={v.resolve() for v in possible if v.is_file()}
        assert len(found)==1,(rf,found);local=next(iter(found))
    assert ROOT.resolve() in local.resolve().parents,local
    h=sha(local);assert h==r['outputSha256']==sha(src),rf
    with Image.open(local) as im:im.load();size=list(im.size);assert size==[1254,1254],local
    assert not r.get('finalArtUpscaled',False),rf
    return {'record':rel(rf),'recordSha256':sha(rf),'native':rel(local),'sha256':h,'pixels':size,'originalSource':str(src)}
cfg=read(ROOT/'builtin_q64_production/current-batch-config.json')
entries=[]
for item in cfg['candidates']:
    f=ROOT/item['file'];assert f.is_file(),f
    with Image.open(f) as im:im.load();assert im.size==(4096,4096),f
    e={**item,'sha256':sha(f),'pixels':[4096,4096],'accepted':False,'runtimePublished':False}
    for key in ('qa','assembly'):
        q=ROOT/e[key];assert q.is_file(),q;e[key+'Sha256']=sha(q)
    entries.append(e)
count=len(entries)
assert count==len({(e['appearance'],e['tile']) for e in entries}),'Duplicate candidate coordinate'
baseRecords=list((ROOT/'builtin_q64_r10_c07/native').glob('r*.record.json'))
for d in sorted((ROOT/'builtin_q64_production').glob('*/*')):
    baseRecords.extend(sorted((d/'native').glob('r*.record.json')))
sourceEvidence=[verify_native(rf) for rf in baseRecords]
repairPaths=cfg.get('repairRecords',[])
assert len(repairPaths)==len(set(repairPaths)),'Duplicate repair record'
repairEvidence=[verify_native(ROOT/p) for p in repairPaths]
baseHashes={e['sha256'] for e in sourceEvidence};repairHashes={e['sha256'] for e in repairEvidence}
assert len(baseHashes)==len(sourceEvidence),'Repeated base source'
assert len(repairHashes)==len(repairEvidence),'Repeated repair source'
assert baseHashes.isdisjoint(repairHashes),'Double-counted source'
baseCount=len(sourceEvidence);repairCount=len(repairEvidence)
cat=read(ROOT/'production_catalog.json')
keys=[v['city']+'_'+v['variant'] for v in cat['variants']]
assert len(keys)==len(set(keys))==7
assert set(e['appearance'] for e in entries).issubset(set(keys))
plans={};matched=0
for v in cat['variants']:
    key=v['city']+'_'+v['variant'];plan=read(ROOT/v['completeGridPlan']);plans[key]=plan
    assert len(plan['tiles'])==len({t['id'] for t in plan['tiles']})==256
    for e in [e for e in entries if e['appearance']==key]:
        tiles=[t for t in plan['tiles'] if t['id']==e['tile']]
        assert len(tiles)==1 and tiles[0]['finalPixelRect']==e['finalPixelRectXYWH'],e
        matched+=1
assert matched==count
total=sum(len(p['tiles']) for p in plans.values());assert total==1792
now=datetime.now(timezone.utc).isoformat()
s=read(ROOT/'status.json')
decision=s.get('scopeDecision',{})
assert decision.get('userResponseReceived') is True and decision.get('pending') is False,'Do not silently change confirmed scope'
batch={'schemaVersion':2,'updatedAtUtc':now,'scope':f'{count} unique local 4K candidates; 7 full64K appearances remain in production','plannedDeliveryTiles':total,'generated4KCandidateCount':count,'acceptedDeliveryTileCount':0,'wholeCityCompletedCount':0,'baseNativeDetailPatchCount':baseCount,'additionalNativeRepairCount':repairCount,'nativeDetailPatchCountIncludingRepairs':baseCount+repairCount,'referenceImagesExcludedFromDetailCount':True,'detailCountMeaning':'Verified retained generation sources, including superseded sources and recorded sources of in-progress tiles. Alternate assembly versions do not add coordinates.','sourceArtUpscaled':False,'candidates':entries,'baseNativeEvidence':sourceEvidence,'nativeRepairEvidence':repairEvidence,'scopeDecisionPending':False,'runtimePublished':False}
write(ROOT/'builtin_q64_production/current-batch.json',batch)
s.update({'schemaVersion':4,'updatedAtUtc':now,'status':'continuing_64K_production_user_confirmed_all_cities','scope':batch['scope'],'activePlan':'builtin_q64_production/current-batch.json','activeWorkingDirectory':'builtin_q64_production','generated4KCandidateCount':count,'baseNativeDetailPatchCount':baseCount,'additionalNativeRepairCount':repairCount,'nativeDetailPatchCount':baseCount+repairCount,'candidateFiles':[e['file'] for e in entries],'currentBatch':'builtin_q64_production/current-batch.json','completedCurrentDeliveryTiles':0,'completedWholeCityCount':0,'allSevenMapVariantsComplete':False,'runtimePublished':False,'candidatePreview':'builtin_q64_production/current-batch-overview.jpg','candidateVisualReview':'Local visual-review results are linked individually. Whole-city, all external neighbors, foreground and closest-camera acceptance remain incomplete.','completedDeliveryCountMeaning':'Only formally accepted production tiles. Generated candidates and assembly revisions are reported separately.','scopeDecision':decision})
for key in ['candidateFile','candidateSha256','candidatePixels']:s.pop(key,None)
write(ROOT/'status.json',s)
cat['updatedAtUtc']=now;cat['currentBatch']='builtin_q64_production/current-batch.json'
for v in cat['variants']:
    key=v['city']+'_'+v['variant'];es=[e for e in entries if e['appearance']==key]
    v.update({'state':'local_4K_candidates_generated_full_64K_production_incomplete','generated4KCandidateCount':len(es),'productionTilesAccepted':0,'runtimePublished':False,'activeWorkingDirectory':'builtin_q64_production/'+key,'currentCandidates':es})
    for k in ['currentCandidateFile','currentCandidateSha256']:v.pop(k,None)
    plan=plans[key];plan.update({'updatedAtUtc':now,'generated4KCandidateCount':len(es),'productionTilesAccepted':0,'runtimePublished':False,'wholeCityComplete':False})
    for tile in plan['tiles']:
        matches=[e for e in es if e['tile']==tile['id']]
        if matches:
            e=matches[0];tile.update({'state':'generated_candidate_pending_acceptance','candidateFile':'../'+e['file'],'candidateSha256':e['sha256'],'candidatePixels':[4096,4096],'qa':'../'+e['qa'],'accepted':False})
    write(ROOT/v['completeGridPlan'],plan)
write(ROOT/'production_catalog.json',cat)
rows=math.ceil(count/4);height=150+rows*655
board=Image.new('RGB',(2200,height),'#f5f3ed');draw=ImageDraw.Draw(board)
font=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',26);small=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',20);title=ImageFont.truetype(r'C:/Windows/Fonts/msyh.ttc',38)
draw.text((30,18),f'主城 Q 版重制 · {count} 个局部 4K 候选',font=title,fill='#182c36')
draw.text((32,75),'覆盖4城7套外观｜每张4096×4096｜完整64K主城：0/7｜正式验收：0/1792',font=small,fill='#8a4524')
for i,e in enumerate(entries):
    x=30+(i%4)*545;y=126+(i//4)*655
    with Image.open(ROOT/e['file']) as im:board.paste(im.convert('RGB').resize((510,510),Image.Resampling.LANCZOS),(x,y))
    draw.text((x,y+520),e['displayName']+' '+e['tile'],font=font,fill='#182c36')
    draw.text((x,y+562),'局部候选 · 完整主城与实机未验收',font=small,fill='#8a4524')
    draw.text((x,y+597),'整城网格坐标：'+e['tile'],font=small,fill='#4a5960')
board.save(ROOT/'builtin_q64_production/current-batch-overview.png')
board.save(ROOT/'builtin_q64_production/current-batch-overview.jpg',quality=82)
board.resize((1650,round(height*.75)),Image.Resampling.LANCZOS).save(ROOT/'builtin_q64_production/current-batch-overview-preview.jpg',quality=78)
table=['| 外观 | 图块坐标 | 4K候选 | 检查记录 |','| --- | --- | --- | --- |']
for e in entries:table.append(f"| {e['displayName']} | {e['tile']} | [无损PNG]({e['file']}) | [QA]({e['qa']}) |")
md=f"""# 主城64K / 单块4K重制

累计生成 **{count}个独立坐标的4096×4096局部候选**。**完整64K整城0/7套，正式验收0/1792块**。同一坐标的返修版本不重复计数。用户已确认继续全部主城至完成，维持原64K目标，无待确认的范围问题。

累计核验{baseCount}张基础原生1254×1254细节图及{repairCount}张原生返修图，保留原始字节和来源记录；正在制作的图块中已核验原图也计入源图数量。布局参考、预览和机械处理版本不计为新增原生图。高清细节采用分区生成、重叠拼接后裁成4K；没有将低清图直接放大冒充高清。小幅机械接缝配准会重采样边缘像素，位移与色彩校正另存记录。

[本批总览](builtin_q64_production/current-batch-overview.jpg) · [来源与数量核验](builtin_q64_production/current-batch.json) · [状态JSON](status.json)

"""+'\n'.join(table)+"""

## 目标与制作状态

每套65536×65536、16×16块、每块4096×4096；7套共1792块。旧图和1254²整城参考只约束布局，不计为高清成品。按当前每块16张原生细节图的流程，全部基础细节需要28672张生成图，另需参考与接缝修复。当前仍在逐块制作，未完成总量。

## 路线与检查

后续生图从[统一模型配置](../config/image-generation.json)读取型号与画质，并遵循[模型策略](../docs/IMAGE_MODEL_POLICY.md)，优先使用内置image_gen；API备用路径仍需独立授权。已有图片的请求、实际型号与画质以对应来源记录为准，不能用当前配置回填历史；实际图片尺寸、来源与提示词逐张保存。

检查包括原像素细节、内部接缝和相邻图块衔接。节庆版应沿用同城结构。仍需完整外围邻接、导航对齐、独立前景、最近镜头、跨块移动与设备验收，尚未替换客户端地图，未发布生产manifest。

客户端按可见范围加周围一圈加载，目标外观齐备后整体切换；既有验证21/21通过、运行时代码编译0错误，见[客户端验证](E:/work/mmorpg-client/Docs/VerificationEvidence/city-tiles4k-atomic-20260917/summary.json)。客户端代码验证不代表新美术完成实机验收。

## 统一需求话术

所有主城地图按更Q版、圆润饱满、明亮干净的方向重制，使用内置GPT Image路线的最高可用画质。每套目标65536×65536，按16×16切成256张4096×4096图块；各区重新制作清晰细节，保持道路、建筑、台阶、水岸、出入口和镜头角度一致，重叠拼接后再裁切，逐条检查接缝。同城节庆版保持结构一致。客户端按视野加载并预载邻块。原生图、拼接图、切图清单和验收记录必须可追溯，未通过验收的不计为完成。

[主城地图切图规范](E:/work/image/主城地图切图规范.md)只规定主城切图和美术交付规则；客户端实现见[CityTiles4K](E:/work/mmorpg-client/Docs/CityTiles4K.md)。

## 保留的历史资料

- [七套Q版整城布局参考（1254²）](builtin_q64_all_city_references/README.md)
- [1792块离线坐标计划](q64_production_plans/README.md)
- [最初天墉Q版4K局部候选](builtin_q64_r10_c07/README.md)
- [旧4K试作](builtin_4x4/plan.json)、[32K密度试作](builtin_density32k_r05_c04/plan.json)
- [停用的GPT Image2.5 API执行包](q64_gpt25/执行包.md)，本轮不使用。
"""
hist=ROOT/'history';hist.mkdir(exist_ok=True);backup=hist/'README-before-local-batch-20260917.md'
if not backup.exists():shutil.copyfile(ROOT/'README.md',backup)
(ROOT/'README.md').write_text(md,encoding='utf-8')
(ROOT/'builtin_q64_production/README.md').write_text(f'# 主城4K局部候选\n\n累计{count}个独立坐标候选；完整64K整城0套，正式验收0块。继续原定全部主城范围。\n\n[制作说明与逐图链接](../README.md) · [来源核验](current-batch.json) · [总览](current-batch-overview.jpg)\n',encoding='utf-8')
(ROOT/'q64_production_plans/README.md').write_text(f'# 全主城64K离线分块计划\n\n每套16×16共256块4096×4096，7套共1792块。这是离线坐标计划，不是客户端生产manifest。\n\n当前登记{count}个独立坐标4K候选，其余{1792-count}个坐标尚未登记为当前候选，其中部分已有进行中的原生细节或未审拼接；正式验收0块，完整整城0套。见[制作总览](../README.md)。\n\n'+'\n'.join(f"- [{v['displayName']}]({Path(v['completeGridPlan']).name})：{v['generated4KCandidateCount']}/256个局部候选。" for v in cat['variants'])+'\n',encoding='utf-8')
write(ROOT/'builtin_q64_production/summary-verification.json',{'updatedAtUtc':now,'unique4KCandidateCount':count,'candidatePixelsVerified':True,'candidateHashesRecorded':True,'originalNativeSourceByteIdentityVerified':baseCount+repairCount,'baseNativeSourcesVerified':baseCount,'repairRecordsVerified':repairCount,'nativePatchPixelsVerified':[1254,1254],'totalPlannedTiles':total,'acceptedCount':0,'wholeCityCompletedCount':0,'confirmedScopePreserved':True})
print(json.dumps({'candidates':count,'baseNativePatches':baseCount,'repairNativePatches':repairCount,'whole64KCities':0,'acceptedTiles':0},ensure_ascii=False,indent=2))

