from pathlib import Path
from PIL import Image
import json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf8')
def info(p):
 d={'file':str(p),'sha256':sha(p),'bytes':p.stat().st_size}
 if p.suffix.lower()=='.png':
  im=Image.open(p);d.update(pixels=list(im.size),mode=im.mode)
 return d
now=datetime.now(timezone.utc).isoformat();p=json.loads((B/'processing.json').read_text());scopes=json.loads((B/'qa/exported-scopes.json').read_text())
observations={
'north-commonedge-1.png':'Pale pillar, green shrub and warm paving joins continuous at core boundary; red cap is confined above current core. No new object or edge discontinuity.',
'north-commonedge-2.png':'Quiet warm paving and diagonal groove have no new seam stripe or abrupt geometric offset.',
'north-commonedge-3.png':'Warm paving and lower-right diagonal joint continue coherently; no spring edit within this scope.',
'north-commonedge-4.png':'Soft tree shadow, right green foliage and diagonal paving remain continuous; no new spring boundary.',
'northwest-corner.png':'North/current pillar and green leaves remain connected at the two-tile boundary. Four-way neighboring junction not assessed.',
'northeast-corner.png':'Dark leaves and soft pavement shadow join continuously. Four-way neighboring junction not assessed.',
'southwest-corner.png':'Own native leaf forms unchanged; adjacent south/west tile junction not yet assessed.',
'southeast-corner.png':'Own blue water and reflected shapes unchanged; adjacent south/east tile junction not yet assessed.',
'south-cap-detail1.png':'Red cap faces, gold bevels and original leaf-shadow shapes preserved. Cream masonry and overlapping leaves remain untouched.',
'south-cap-detail2.png':'Cap meets white column at original contact edge; narrow dark contact outline retained, no white stone recolor.',
'south-cap-detail3.png':'Safe source-surface polygons cover original orange speckles at joint; original lower dark contact edge retained.'}
for s in scopes:s.update(actuallyViewed=True,viewMethod='tools.view_image(detail=original)',observation=observations[Path(s['file']).name],requiresRepair=False)
for name,observation in [('candidate/southwest-composite1254.png','Entire final1254 composite viewed at1:1; existing faces red with fine golden bevels, fixed block silhouette, leaves and stone preserved.'),('qa/southwest-mask-overlay1254.png','Exact source entity mask visually checked; no white column, cream wall, leaves, trunk, water or bridge inclusion.'),('qa/north-cap-after128.png','Red clipped cap stays inside existing original orange entity in top halo, leaves and paving untouched.'),('selected/preview1254.png','Downsampled full-tile preview retains bright clean rounded painting, original red lantern, white-gray bridge and blue water. Overview only.')]:
 scopes.append({**info(B/name),'actuallyViewed':True,'viewMethod':'tools.view_image(detail=original)','nativeScale':name!='selected/preview1254.png','observation':observation,'requiresRepair':False})
write(B/'qa/final-visual-review.json',{'createdAtUtc':now,'tile':'r09_c10','appearance':'lanxian_spring','scopes':scopes,'styleReference':{'file':'D:/work/image/designs/gameplay-ui/04-guild.png','actuallyViewedAndAttachedBothCalls':True},'exactOutsideMaskEquality':p['outsideMaskByteEqual'],'coreHaloExact':p['coreMatchesExtended'],'northCoreUnchangedFromDay':True,'inheritedDayInternalSeams':'Unchanged outside compact surface mask; day actual QA and source provenance snapshots retained. No claim of newly regenerating those seams.','qualifiedComplete4KCandidate':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False})
inputs=[]
for name,src,op in [('southwest-cap1254.png','core4096.png',{'cropLTRB':[700,2800,1954,4054],'resampling':None}),('northwest1254.png','extended4326.png',{'cropLTRB':[0,0,1254,1254],'resampling':None}),('day-overview1254.png','core4096.png',{'resize':[1254,1254],'resampling':'LANCZOS downsample; reference overview only'})]:
 inputs.append({**info(B/'inputs'/name),'derivedFrom':info(B/'shared-geometry/day'/src),'operation':op,'generationRecord':'../shared-geometry/day/evidence/selected/delivery.manifest.json','newAIGeneration':False})
write(B/'inputs/source-crops.json',inputs)
nativeRecords=[info(B/'native/southwest-cap1254.png.generation.json'),info(B/'native/northwest-cap1254.png.generation.json')]
outputs={k:info(B/'selected'/f) for k,f in [('core','core4096.png'),('extended','extended4326.png'),('preview','preview1254.png'),('mask','surface-mask4326.png')]}
for k in ['core','extended','preview']:
 write(B/'selected'/(Path(outputs[k]['file']).name+'.generation.json'),{**outputs[k],'generatedAt':now,'operation':'derived shared-geometry surface composite'+('; LANCZOS downsample for preview only' if k=='preview' else ''),'newIndependentAIGeneration':False,'derivedFrom':[p['base'],*p['nativeEdits']],'processing':info(B/'processing.json'),'modelEvidenceRecords':nativeRecords,'actualModel':None,'actualQuality':None,'unverifiedReason':'Composite combines exact qualified day shared geometry with two builtin native1254 edits; actual model and quality are undisclosed. See per-image source records.','configSnapshot':json.loads((B/'config-snapshot.json').read_text())})
qa={'production':info(B/'qa/final-visual-review.json'),'northIndependent':info(B/'qa-north-independent/review.json')}
if (B/'qa-north-independent/final-review.json').exists():qa['finalIndependent']=info(B/'qa-north-independent/final-review.json')
manifest={'schemaVersion':1,'createdAtUtc':now,'appearance':'lanxian_spring','tile':'r09_c10','status':'qualified_complete_4k_candidate_pending_remaining_adjacent_edges_and_formal_acceptance','qualifiedComplete4KCandidate':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False,'runtimePublished':False,'geometry':{'wholeCityPixels':[65536,65536],'grid':[16,16],'corePixels':[4096,4096],'extendedPixels':[4326,4326],'haloPerSide':115,'coreInExtendedLTRB':[115,115,4211,4211],'wholeCityCoreLTRB':[36864,32768,40960,36864],'navigationFootprintsChanged':False},'outputs':outputs,'processing':info(B/'processing.json'),'sourceChain':{'pinAudit':info(B/'shared-geometry/provenance.json'),'exactDaySelectedEvidence':info(B/'shared-geometry/day/evidence/selected/delivery.manifest.json'),'northSpringEvidence':info(B/'shared-geometry/north-spring/evidence/selected/delivery.manifest.json'),'nativeEditRecords':nativeRecords,'config':info(B/'config-snapshot.json'),'officialVerification':info(B/'official-verification.json')},'processingDeclaration':{'sharedGeometryReuse':True,'newGeometryGeneration':False,'nativeAIEdits':2,'nativeSizes':[[1254,1254],[1254,1254]],'sameCoordinateMaskedPaste':True,'resampling':None,'warp':None,'upscale':False,'changedCorePixels':p['coreChangedPixels'],'changedExtendedPixels':p['changedPixels'],'outsideMaskByteIdentical':True,'coreMatchesHalo':True},'qa':qa,'remaining':['Adjacent west, east and south joint acceptance remains pending.','Four-way corners, formal art acceptance, client navigation/loading and whole-city completion remain unverified.'],'retention':{'status':'pending_cleanup_after_independent_review','policy':'Keep selected final images, technical masks and all text/source/model/QA records; remove superseded source snapshots, generated drafts and QA crops after checked export. Source paths in historical text remain provenance, not live dependency promises.'}}
write(B/'selected/delivery.manifest.json',manifest)
readme='''# 兰仙镇春节 r09_c10

交付为完整 4096 核心图、4326 外扩图与1254总览的合格候选；正式美术验收、客户端验证和整城完成均为 false。

仅将已有花坛压顶与顶部 halo 中的极小帽面改为朱红漆面、原倒角细金色；桥梁、白石、植被、水面与其他非表面像素按共享日景保留。没有新增物件、占地或通行变化，没有放大、几何变形或整块4K AI 重绘。两次内置 image_gen 实际原生输出均为1254×1254，再按同坐标实体遮罩合成。

- 正式候选：[core4096.png](selected/core4096.png)、[extended4326.png](selected/extended4326.png)、[preview1254.png](selected/preview1254.png)
- [交付清单](selected/delivery.manifest.json)、[加工记录](processing.json)、[视觉复查](qa/final-visual-review.json)
- [南侧压顶逐图模型记录](native/southwest-cap1254.png.generation.json)、[北侧帽面逐图模型记录](native/northwest-cap1254.png.generation.json)
- [南侧完整提示词](southwest-cap.prompt.txt)、[北侧完整提示词](northwest-cap.prompt.txt)、对应 receipt JSON 保存工具回执。
- [配置快照](config-snapshot.json)、[官方核对](official-verification.json)、[共享结构来源](shared-geometry/provenance.json)

实际型号／质量：宿主管理，工具未披露，均记为 null；配置目标不代替实际返回证据。派生交付图旁 *.generation.json 分别索引来源链。

北侧四段正式接缝及两角已按1:1查看；下方两角是本块原像素检查，未代表尚未完成的邻块接缝通过。继承的日景内部接缝沿用既有验证。源图与过程 PNG 清理后，文字中旧路径仅作为来源身份，不能宣称仍可读取或完全重建。
'''
(B/'README.md').write_text(readme,encoding='utf8')
print(json.dumps({'manifest':info(B/'selected/delivery.manifest.json'),'core':outputs['core'],'extended':outputs['extended']}))
