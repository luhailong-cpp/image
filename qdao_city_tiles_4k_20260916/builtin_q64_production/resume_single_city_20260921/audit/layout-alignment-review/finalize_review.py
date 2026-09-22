from pathlib import Path
import hashlib,json,datetime

OUT=Path(__file__).resolve().parent
SESSION=OUT.parents[1]
manifest=json.loads((OUT/'comparison-manifest.json').read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
checks=[]
for group in ['sourceFiles','evidence']:
 for item in manifest[group]:
  actual=sha(item['file'])
  checks.append({'file':item['file'],'expected':item['sha256'],'actual':actual,'matches':actual==item['sha256']})
assert all(x['matches'] for x in checks)

observations=[
 {'id':'L01','category':'road_and_fixed_landmark','evidence':['plaza_geometry_overview.jpg','master_navigation_overlay.jpg','plaza_navigation_overlay.jpg'],
  'masterApproximateInspectionRegionsLTRB':{'northStairAndPassage':[2870,2090,3270,2490],'southStairOpening':[2580,3750,3560,3980],'circleAndFourRadialAxes':[2420,2470,3740,3420],'southwestPot':[2640,3540,2810,3750],'southeastPot':[3340,3540,3510,3750]},
  'observation':'原 6144 中央裁区与历史 plaza 中，太极环、四向铺装轴、南北实际台阶开口、南侧两盆景基座和岸边固定结构整体位置近似重合。此抽样未看到整片大幅平移、道路截断、台阶开口换位或建筑新增/消失。',
  'limit':'坐标为从同坐标分析板读取的近似检查区域，不是地标中心的精密测量值，也没有证明所有边界逐像素相同。中央裁区以外未进行旧 plaza 对照。'},
 {'id':'D01','category':'decorative_paving','tile':'r09_c09','evidence':['r09_c09_geometry.jpg'],'candidateVersion':'repair_v6','candidateLocalInspectionLTRB':[0,1750,1000,3100],
  'masterEquivalentLTRB':[3072,3236.0625,3165.75,3362.625],
  'observation':'环形广场南侧黑色径向铺装/卦纹的位置及条带组仍在原区域；v6 的明暗边、浅色横条和分缝变粗，局部宽度及分缝形态与原图不同。它属于环面装饰，不应仅据局部外观把它认定为另一个实际楼梯或导航阻挡。',
  'impact':'未在此处观察到新增道路障碍或通道拓扑改变；不得据此声称几何精确一致。'},
 {'id':'D02','category':'decorative_paving','tile':'r09_c09','evidence':['r09_c09_geometry.jpg'],'candidateVersion':'repair_v6','candidateLocalInspectionLTRB':[1700,2150,2850,2800],
  'masterEquivalentLTRB':[3231.375,3273.5625,3339.1875,3334.5],
  'observation':'外环嵌板云纹变得更圆、更厚，底框阴影与边宽改变；下方外侧石板缝也经过重排。嵌板及环形轴线的位置仍接近原图。',
  'impact':'此处可确认装饰重绘；没有看到建筑、出入口或岸线被移动。'},
 {'id':'D03','category':'decorative_paving','tile':'r09_c10','evidence':['r09_c10_geometry.jpg'],'candidateVersion':'initial r09_c10.candidate.png, NOT later internal-v4 or neighbor join','candidateLocalInspectionLTRB':[2400,600,4096,2550],
  'masterEquivalentLTRB':[3681,3128.25,3840,3311.0625],
  'observation':'右侧云形地面纹样保留原大轮廓与位置，但内卷线变粗、更规则；外围浅色石板的格缝重描，宽度和交点有变化。左侧圆环外轮廓及下方斜向铺装带在三图中仍连续经过相同区域。',
  'impact':'本板能支持初版的大结构近似；不能替最新版 internal-v4 或后续邻块拼接做导航/接缝验收。'},
 {'id':'D04','category':'future_tile_decorative_reference','tile':'r08_c09','evidence':['r08_c09_geometry.jpg'],'masterInspectionLTRB':[3072,2688,3456,3072],
  'observation':'原图与 plaza 中的黑色太极盘、金色弧边、白色鱼眼和外围刻花带位置近似；黑面云纹轮廓、刻花和石缝已经重新描画。此区域没有观察到建筑、门洞、桥栏或水岸；仍是中央环面。',
  'impact':'可优先继续原生细化，但需以原 6144 的太极/弧边位置约束几何，并对照现 r09_c09 的上边。plaza 仅作细部风格和局部配准参考。'},
 {'id':'R01','category':'road_waterbank_obstacle_risk','tile':'r09_c11','evidence':['r09_c11_geometry.jpg'],'masterInspectionLTRB':[3840,3072,4224,3456],
  'missingPlazaMasterLTRB':[4096,3072,4224,3456],'missingPlazaCandidateXStart':2730.6666666666665,'missingCandidateWidth':1365.3333333333333,
  'approximateMasterLandmarks':{'uprightRailingPostAndFinial':[4080,3245,4140,3390],'treeCanopyAtBottom':[3920,3310,4090,3456],'curvingRailingAndWaterbank':[4096,3220,4224,3456]},
  'observation':'原图右下实际有弧形护栏、栏杆立柱、树冠和蓝色水面；plaza 仅覆盖其左 512/768 分析像素，右 256 像素无来源，紫色为明确空缺。空缺恰跨护栏/水岸，不能当作全是可行走地砖向右补画。',
  'impact':'先从原 6144 裁取包括岸线及固定立柱的布局上下文，再原生重绘。不得延伸 plaza 图边替代布局来源，不得修改导航以迁就推测岸线。'},
 {'id':'N01','category':'navigation_evidence_boundary','evidence':['master_navigation_overlay.jpg','plaza_navigation_overlay.jpg'],
  'observation':'实际看过两张同坐标导航叠图：已列出的南侧盆景/树木、北侧景物与原障碍区域总体仍位于相同区域，中心及通道未见明显被新实体占据。红/绿多边形来自同一既有 navigation.json，因此它们相同只说明叠图使用了同一个布局坐标来源。',
  'impact':'不等于 Q64 新候选导航通过；没有在客户端运行走位、碰撞、遮挡或最近镜头检查，也未逐边量测全部道路/岸线。保留正式导航验收未通过/未完成。'}
]
report={
 'reviewedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'scope':'Independent visual layout comparison only. No new image generation, candidate edit, client edit, root record edit, or seam QA.',
 'basis':{'layoutSourceAudit':str(SESSION/'tools/layout-source-audit.json'),'layoutSourceAuditSha256':sha(SESSION/'tools/layout-source-audit.json'),'comparisonManifest':str(OUT/'comparison-manifest.json')},
 'sourceAndBoardHashReverification':checks,
 'actuallyViewedBoards':[Path(x['file']).name for x in manifest['evidence']],
 'coordinateConvention':{'rectangles':'LTRB, right/bottom exclusive where exact; visually read landmark inspection boxes are approximate and not measurement of displacement', 'master':'original 6144x6144', 'candidate':'4096x4096 tile-local', 'tileToMaster':'master=(384*(col-1)+localX*3/32,384*(row-1)+localY*3/32)','previewScale':'Deliberately resized geometry comparisons; no claim of native pixel quality or new production asset'},
 'observations':observations,
 'conclusion':{'severeHistoricalPlazaGlobalDriftObservedInReviewedCentralRegion':False,'pixelExactGeometryIdentityProven':False,'roadBuildingEntranceTopologyChangeObservedInReviewedCandidates':False,'decorativePavingChangesObserved':True,'fullNavigationAcceptance':False,'clientRuntimeAcceptance':False,'formalArtAcceptance':False,'fullCityAcceptance':False},
 'continuationRecommendation':{'priority':'r08_c09 before r09_c11','r08_c09':'原布局/太极及同心弧控制点约束 + 当前 r09_c09 上边接续；plaza 为参考，不授权导航漂移。','r09_c11':'必须先补齐原 6144 权威上下文；重点锁定立柱、弧形护栏、水岸和树木基底。右三分之一不可从 plaza 外推。','candidateVersionBoundary':'r09_c09 reviewed repair_v6; r09_c10 reviewed only initial candidate hash listed in manifest. Later internal-v4/external-join versions are outside this geometry comparison.'}
}
(OUT/'layout-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'shaChecks':len(checks),'allMatch':all(x['matches'] for x in checks),'observations':len(observations)},ensure_ascii=False))
