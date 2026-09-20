from pathlib import Path
import json,hashlib,datetime
import numpy as np
from PIL import Image
ROOT=Path(r'E:/work/image/qdao_city_tiles_4k_20260916');P=ROOT/'builtin_q64_production';D=P/'lanxian_batch_r08_c06_c07';D.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def j(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def rel(p):return Path(p).relative_to(ROOT).as_posix()
def write(p,x):Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
repairs=[];bases=[]
for v in ('lanxian_day','lanxian_spring'):
 repairs+=sorted((P/v/'r08_c06/repairs/v3/native').glob('*.record.json'))
 repairs+=sorted((P/v/'r08_c07/repairs').glob('*/native/*.record.json'))
 repairs+=sorted((P/v/'pair_r08_c06_c07/repairs').glob('*/native/*.record.json'))
 bases+=sorted((P/v/'r08_c07/native').glob('r*.record.json'))
repairs+=[P/'lanxian_day/r08_c07/rejected/r04_c02-transparent-v1/native.record.json']
assert len(repairs)==17 and len(bases)==32
verified=[]
for p in bases+repairs:
 r=j(p)
 for pathkey,hashkey in [('outputPath','outputSha256'),('sourceOutputPath','sourceOutputSha256'),('promptPath','promptSha256'),('guidePath','guideSha256'),('actualSubmittedReferencePath','actualSubmittedReferenceSha256')]:
  assert sha(r[pathkey])==r[hashkey],(str(p),pathkey)
 assert r['outputSha256']==r['sourceOutputSha256']
 assert list(Image.open(r['outputPath']).size)==r['actualNativePixels']==[1254,1254]
 assert not r['finalArtUpscaled'] and not r['resizedAfterGeneration']
 verified.append({'record':rel(p),'recordSha256':sha(p),'sourceOutputPath':r['sourceOutputPath'],'sourceOutputSha256':r['sourceOutputSha256'],'role':'new_base_native' if p in bases else ('rejected_native_not_used' if 'rejected' in p.as_posix() else 'repair_native')})
assert len({e['sourceOutputSha256'] for e in verified})==49
entries=[]
for v,display,version in [('lanxian_day','揽仙镇日景','v4'),('lanxian_spring','揽仙镇春景','v5')]:
 d=P/v/'pair_r08_c06_c07';out=d/'output';qa=d/'qa';ass=out/f'pair-{version}-assembly.json';m=j(ass)
 pair=np.array(Image.open(m['pair']).convert('RGB'));assert pair.shape==(4096,8192,3)
 assert sha(m['pair'])==m['pairSha256']
 for i,c in enumerate(m['candidates']):
  im=np.array(Image.open(c['file']).convert('RGB'));assert im.shape==(4096,4096,3)
  assert np.array_equal(im,pair[:,i*4096:(i+1)*4096]) and sha(c['file'])==c['sha256']
  ex=np.array(Image.open(c['extendedContext']).convert('RGB'));assert ex.shape==(4326,4326,3)
  assert np.array_equal(im,ex[115:4211,115:4211]) and sha(c['extendedContext'])==c['extendedContextSha256']
 q={
 'appearance':v,'reviewedAtUtc':now,'selectedVersion':'pair-'+version,'selectedPair':rel(m['pair']),'selectedPairSha256':m['pairSha256'],
 'scope':'Local two-tile candidate: r08_c06 and r08_c07. Inspected listed exact-pixel crops plus overview; not an exhaustive full-city or runtime review.',
 'formalAcceptance':False,'wholeCityAccepted':False,'nearestGameplayCameraAccepted':False,'externalNeighborSeamsAccepted':False,'crossAppearancePixelGeometryAccepted':False,
 'status':'local_candidate_reviewed_known_targeted_P2_defects_repaired',
 'sourceRoute':'builtin_image_gen','requestedModel':'GPT Image 2.0 highest available through builtin route','backendModelVerified':False,
 'sourceResampling':'subpixel alignment only; native dimensions retained; local color matching',
 'registrationLimits':'Flow bounded to 8 pixels independently in X and Y at selected patch edges. Exact flow and RGB correction fields saved. Interior native pixels and zero-mask context asserted unchanged. No final-image upscaling.',
 'reviewedEvidence':[
  {'file':rel(qa/f'pair-{version}-overview.jpg'),'kind':'overview_only','pixels':[1600,800]},
  {'files':rel(P/v/'r08_c07/qa')+'/seam_x{1024,2048,3072}_y{1024,2048,3072}_100pct.png','kind':'nine initial internal intersections, each viewed at original 900 pixels; targeted failures subsequently repaired'},
  {'files':rel(qa)+'/boundary-v1-{0,1,2,3,4}_100pct.png','kind':'five initial cross-4K boundary crops, each original 900 pixels'},
  {'file':rel(qa/'curve-return-v4-full_100pct.png'),'rectInPairXYXY':[6838,300,8192,1744],'kind':'final curve patch with all in-image return margins, original pixels'},
 ],
 'resolvedFindings':[
  'Existing r08_c06 paving dead ends repaired with original native patches and recorded small registration; spring duplicate roof joint repaired.',
  'r08_c07 curved paving broken joints and the internal right return step replaced by a native patch extending to the current right tile edge; final original-pixel crop showed continuous grooves.',
 ],
 'residualObservations':[
  {'priority':'P3','area':'older r08_c06 painted paving versus new r08_c07 clean paving','observation':'Painterly grain and bevel width vary locally; not a uniform material-texture pass.'},
  {'priority':'P3','area':'selected grout intersections in final curve crop','observation':'Small local bevel/dark-groove width variations remain, with no observed repeat of the previously located large dead ends in this inspected crop.'},
 ],
 'limitations':[
  'Adjacent r08_c08 and all top/bottom/left outer neighbors are unmade or unreviewed in this batch; the 115-pixel outer halo is working context, not accepted delivery art.',
  'Day/spring new tree planter and roads use the common footprint; existing c06 architecture/roof ornaments and paving microgeometry differ between appearances. No pixel-aligned interchangeable-layer or navigation approval.',
  'Nearest gameplay-camera view, collisions, streaming integration and client publication were not tested here.',
  '4096 dimensions and byte-identity checks are mechanical evidence, not formal art acceptance.'
 ]}
 if v=='lanxian_day':
  q['reviewedEvidence'] += [{'files':rel(qa)+'/boundary_{1,2,3}-after_100pct.png','kind':'three full native-sized boundary repair areas viewed; same boundary art retained in v4'}]
  q['resolvedFindings'] += ['Half-cut lower hanging red lantern at pair approximately x4200,y3700 restored as one complete hanging ornament with its cord and tassel; original-size repair inspection performed.']
 else:
  q['reviewedEvidence'] += [
   {'files':rel(qa)+'/boundary-full-v3-{0,1}_100pct.png','kind':'top and middle 1254-pixel boundary crops viewed; same artwork retained outside later strip repair'},
   {'file':rel(qa/'strip-return-v5-full_100pct.png'),'rectInPairXYXY':[3250,1880,4704,2700],'kind':'final exact-pixel strip repair with 100-pixel margins'},
  ]
  q['resolvedFindings'] += ['The v3/v4 hard horizontal cutoff at pair y2278 was actually observed on final checking and rejected. A new 1254 native repair was cropped to its central 1254x620 pavement band and registered into [3350,1980,4604,2600]; v5 original-size review shows continuous diagonal grooves across that location. Roof, leaves and red ornament below this band remain from v4.']
  q['residualObservations'] += [{'priority':'P3','area':'r08_c07 around x1024,y2048','observation':'Tree/planter ground shadow has faceted color transitions; silhouette stays connected in the viewed crop.'}]
 write(qa/'visual-review.json',q)
 text=f'''# {display} r08_c06–r08_c07 局部候选审核\n\n选定版本：**pair-{version}**。两块各4096×4096，共同8192×4096图先完成边界修补，再原样裁成相邻块。正式验收、整城完成、最近游戏镜头和客户端发布均为否。\n\n## 实际检查范围\n\n查看最终1600×800总览；本轮两套各9张新块内部交点900×900裁图、各5张跨4K边界900×900裁图；逐张查看原生返修，再查看最终弧形砖带1354×1444原像素裁图。日景查看3张完整边界补片，春景查看上中段1254裁图及最终1454×820横接线修补裁图。JPEG预览只用于显示，裁剪保持原像素尺寸，不能用缩略图代替局部审核。\n\n## 修复结果\n\n旧c06砖缝断头/重复窄条已局部重绘，春景屋面重复瓦唇已修正；c07弧形铺砖原来的断口及右回接处错口已修复。最终曲线裁图中，已定位的断头缝不再可见。日景下方约pair(4200,3700)半截灯笼已恢复完整的悬绳、灯体和穗。\n\n'''
 if v=='lanxian_spring':text+='春景pair y≈2278处，v3/v4固定拼接线曾造成多条砖缝横向截断，保留为失败历史；v5新增原生修补只贴地面中央带[3350,1980,4604,2600]，原尺寸查看四周回接后，已观察到的截断线消除。没有覆盖下方屋顶、叶簇或红色饰物。\n\n'
 text+='''## 剩余观察与限制\n\n仍有P3级局部砖缝宽度、明暗和笔触差异；春景树池阴影局部色面较明显。现有日/春建筑、屋饰与地砖微观布局并不逐像素一致，不能据此验收无漂移换肤。所看范围未再出现已定位的大段断砖线；这不是对整块每一像素或全城无缝的承诺。\n\n左右外邻、上下外邻和游戏最近镜头未验收，4326上下文外圈仅供后续工作约束，不算正式图块。原生图均1254×1254，16张基础原生以1024核心组成4K；局部补片配准有亚像素重采样，X/Y各自最多8px，并进行局部色调匹配。所有原生PNG保持不动，位移/颜色场与遮罩均留档，没有把旧图放大成4K。内置宿主管理后端，型号未核实。\n\n详细坐标、证据路径和限制见[visual-review.json](visual-review.json)。最终组装及来源证据见对应output中的pair版本assembly.json。\n'''
 (qa/'visual-review.md').write_text(text,encoding='utf-8')
 m['visualQA']='local_candidate_reviewed_known_targeted_P2_defects_repaired';m['visualReview']=str(qa/'visual-review.json');m['visualReviewSha256']=sha(qa/'visual-review.json');write(ass,m)
 for c in m['candidates']:
  entries.append({'appearance':v,'displayName':display,'tile':c['tile'],'file':rel(c['file']),'sha256':c['sha256'],'assembly':rel(ass),'qa':rel(qa/'visual-review.json'),'finalPixelRectXYWH':c['finalPixelRectXYWH'],'worldRect':c['worldRect']})
 # Preserve historical v1/v2 conclusions and append a clearly dated superseding note.
 old=P/v/'r08_c06/qa/visual-review.md';s=old.read_text(encoding='utf-8')
 marker='## 继续生产：c06返修及c07邻块联合审核'
 if marker not in s:old.write_text(s+'\n\n'+marker+'\n\n此前v2为历史阶段选择。继续生产中，c06已完成局部原生返修并保留v3/v4记录；最终选定改为相邻两块联合图pair-'+version+'中的c06裁片。详情见[联合QA](../../pair_r08_c06_c07/qa/visual-review.md)。外邻、最近镜头、整城及正式验收仍未通过。\n',encoding='utf-8')
write(D/'source-verification.json',{'verifiedAtUtc':now,'newBaseNativeCount':32,'newRepairAndRejectedNativeCount':17,'successfulRepairNativeCount':16,'rejectedNativeCount':1,'newReferenceNativeCountExcludedFromBaseRepairCounts':2,'uniqueSourceHashes':49,'dimensions':[1254,1254],'allNativeCopiesByteIdenticalToGeneratedSource':True,'allPromptGuideAndSubmittedReferenceHashesVerified':True,'candidateCoreAndExtendedContextPixelIdentityVerified':True,'sources':verified})
ledger={'updatedAtUtc':now,'scope':'Lanxian day/spring r08_c06 repair + new r08_c07 adjacent batch only','candidates':entries,'repairRecords':[rel(p) for p in repairs],'counts':{'uniqueCoordinatesByAppearance':4,'new4KCoordinates':2,'updatedPrior4KCoordinates':2,'newBaseNativeCount':32,'newRepairAndRejectedNativeCount':17,'successfulRepairNativeCount':16,'rejectedNativeCount':1,'regionalReferenceNativesExcluded':2,'wholeCitiesCompleted':0,'formallyAcceptedTiles':0},'verification':rel(D/'source-verification.json'),'nextSuggestedCoordinate':'r08_c08 in both appearances; constrain from final c07 right-edge pixels, not an unaccepted old halo','formalAcceptance':False,'clientPublished':False}
write(D/'ledger-update.json',ledger)
write(D/'resume-checkpoint.json',{'updatedAtUtc':now,'boundedBatch':'completed_candidates_with_limited_visual_QA','ledger':rel(D/'ledger-update.json'),'unfinishedCoordinatesInThisBatch':[],'nextSuggestedCoordinates':['lanxian_day/r08_c08','lanxian_spring/r08_c08'],'wholeCityStillIncomplete':True,'externalNeighborQAStillIncomplete':True,'requiresPaidAPI':False})
print(json.dumps({'ledger':str(D/'ledger-update.json'),'counts':ledger['counts'],'candidates':[{'appearance':e['appearance'],'tile':e['tile'],'sha256':e['sha256']} for e in entries]},ensure_ascii=True,indent=2))
