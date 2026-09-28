import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
p=Path(__file__).resolve().parent
def sha(f): return hashlib.sha256(Path(f).read_bytes()).hexdigest()
v=json.loads((p/'native-verification.json').read_text(encoding='utf-8'))
boards={b['id']:b for b in v['verifiedBoards']}
findings={
 'vertical-x1024': ['米色铺地有细长垂直明暗跳变，弧形金边附近也能追踪到同一直线。','中央直线贯穿米色石面，两条横向金边在 x1024 处出现错台/色阶。','大石砖与横槽均有沿 x1024 的突变。','多条金边及白色描边在 x1024 处出现错台，下半石面仍有直线色差。'],
 'vertical-x2048': ['中央直线横穿两条斜槽，槽线有细小错台。','金边及米色长条中央存在垂直色阶，底部金边也错台。','暗石面 x2048 左右纹理与色阶明显不同，贯穿全段。','暗石面到米色条处持续存在垂直色阶。'],
 'vertical-x3072': ['斜向石框/槽线与米色面在 x3072 处有直线跳变。','雕刻/长框斜边在 x3072 处有垂直色阶。','暗石面与米色框的局部连续较好，但不能抵消其他段失败。','下半部米色面有垂直色阶，与斜向框边相交。'],
 'horizontal-y1024': ['石面在 y1024 有细水平色差，右侧斜槽出现小错台。','左侧斜槽及面色在 y1024 断续，右侧金边附近可追踪。','y1024 水平色带穿过金边、灰色框及米色雕刻区。','y1024 在 x3072..4096 有强水平明暗跳变，斜框也错台。'],
 'horizontal-y2048': ['大块米色石面在 y2048 出现整段水平色阶。','y2048 横穿多条斜向金边和石框，色差及错台明显。','中央接近天然框边，仍有局部色阶；未独立判通过。','y2048 横跨米色面与斜向框线，出现直线明暗/几何错台。'],
 'horizontal-y3072': ['x0..1024 的已修区域未见与其他段同等明显的中心水平切断，但靠近 x1024 的竖色差保留。','y3072 横跨金条与石框，线条有错台。','暗石面有强水平色阶，竖白框在 y3072 突然横移。','多条竖向米色框在 y3072 错台，石面有整行色差。']
}
seams=[]
for id,notes in findings.items():
    b=boards[id]
    seams.append({'id':id,'viewed':True,'viewTool':'view_image','detail':'original','evidence':{'file':b['file'],'sha256':b['sha256']},'fullLengthPixels':4096,'coveredRanges':[[0,1024],[1024,2048],[2048,3072],[3072,4096]],'nativeSourcePixelsVerified':True,'status':'failed','failureKind':['straight_grid_tone_discontinuity','local_contour_steps'],'segmentObservations':[{'range':[i*1024,(i+1)*1024],'note':n} for i,n in enumerate(notes)]})
jnotes={
 (1024,1024):'米色石面呈十字分区色阶，右侧斜槽受横缝影响。',
 (2048,1024):'斜金边和长条面在中心横缝处断续，竖向色阶同时可见。',
 (3072,1024):'雕刻上有十字分区色阶，右侧斜边同样受横缝影响。',
 (1024,2048):'竖色阶穿过水平金边并形成错台，米色面水平色差可见。',
 (2048,2048):'米色/暗石交接区呈强烈矩形明暗分区。',
 (3072,2048):'上方米色长框有竖色阶，交点附近材质过渡不连续。',
 (1024,3072):'原水平修复区局部连续，但中央竖色阶仍贯穿米色面及金边。',
 (2048,3072):'暗石面在中心呈明显十字拼块色阶，邻侧白框横缝错台。',
 (3072,3072):'暗石与白框均被水平拼缝切断，存在几何错台和色差。'
}
jb=boards['internal-junctions-nine']
junctions=[{'pixelXY':list(xy),'viewed':True,'evidenceFile':jb['file'],'evidenceSha256':jb['sha256'],'sourceRectLTRB':[xy[0]-192,xy[1]-192,xy[0]+192,xy[1]+192],'status':'failed','note':n} for xy,n in jnotes.items()]
south=boards['south-r08_c07--r09_c07']
ext=[{'edge':'south','viewed':True,'status':'failed','neighbor':'r09_c07','fullLengthPixels':4096,'evidenceFile':south['file'],'evidenceSha256':south['sha256'],'segmentObservations':[{'range':[0,1024],'note':'边界 y4096 有横向色阶，斜石槽轻微断续。'},{'range':[1024,2048],'note':'边界存在明显亮度/材质变化与金边、槽线错位。'},{'range':[2048,3072],'note':'灰框及米色雕刻底面有明显水平明暗跳变。'},{'range':[3072,4096],'note':'边界横向色差持续，斜框可见断续。'}]},
 {'edge':'east','viewed':True,'status':'failed_diagnostic_with_unselected_neighbor','neighbor':'r08_c08','neighborCandidateSelected':False,'fullLengthPixels':4096,'evidence':v['newDiagnosticBoards'][0],'note':'四个1024段全部实看。前两段明显垂直色阶并有斜框错台；后两段金色槽及白边接缝也有直线断续。正式东边验收仍待邻块选用。'},
 {'edge':'north','viewed':False,'status':'pending_missing_selected_neighbor','neighbor':'r07_c07'},
 {'edge':'west','viewed':False,'status':'pending_missing_selected_neighbor','neighbor':'r08_c06'}]
corners=[{'corner':'northwest','viewed':False,'status':'pending_missing_selected_neighbors','missing':['r07_c06','r07_c07','r08_c06']}, {'corner':'northeast','viewed':False,'status':'pending_missing_selected_neighbors','missing':['r07_c07','r07_c08','r08_c08']}, {'corner':'southwest','viewed':False,'status':'pending_missing_selected_neighbors','missing':['r08_c06','r09_c06']}, {'corner':'southeast','viewed':True,'status':'pending_neighbor_selection','diagnosticOnly':True,'evidence':v['newDiagnosticBoards'][1],'note':'以未选用 c08 masked-result 组成512原像素四块交点，局部未见明显十字几何切断。此局部观察不能抵消南/东全长缝失败，不计正式通过。'}]
ledger=p.parents[1]/'current-coverage-ledger.json'
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c07','source':v['source'],'scope':'fresh native-pixel review of six 4096 internal seams, nine junctions, available full outer boundaries and available diagnostic four-tile corner','inspectionEvents':[{'sequence':1,'tool':'view_image','detail':'original','ids':['vertical-x1024'],'completedBeforeUtc':'2026-09-28T08:58:11Z'}, {'sequence':2,'tool':'view_image','detail':'original','ids':['vertical-x2048','vertical-x3072','horizontal-y1024'],'completedBeforeUtc':'2026-09-28T08:58:11Z'},{'sequence':3,'tool':'view_image','detail':'original','ids':['horizontal-y2048','horizontal-y3072','internal-junctions-nine','south-r08_c07--r09_c07'],'completedBeforeUtc':'2026-09-28T08:58:11Z'}, {'sequence':4,'tool':'view_image','detail':'original','ids':['east-unselected','southeast-unselected'],'completedBeforeUtc':'2026-09-28T09:00:04Z'}],'timeNote':'Completion bounds are actual clock-tool readings after the corresponding views; exact per-image call times were not exposed. No invented timestamp or inherited visual pass.','nativeVerification':{'file':str(p/'native-verification.json'),'sha256':sha(p/'native-verification.json')},'coverageLedgerAtReview':{'file':str(ledger),'sha256':sha(ledger)},'internalSeams':seams,'internalJunctions':junctions,'outerEdges':ext,'fourTileCorners':corners,'repairGuides':v['repairGuides'],'counts':{'internalFullSeamsViewed':6,'internalFullSeamsFailed':6,'internalJunctionsViewed':9,'internalJunctionsFailed':9,'selectedOuterEdgesViewed':1,'selectedOuterEdgesFailed':1,'unselectedNeighborOuterEdgesViewed':1,'unselectedNeighborCornersViewed':1,'formalAccepted':0},'overallStatus':'failed_requires_repair','formalArtAcceptancePassed':False,'clientRuntimeAccepted':False,'wholeCitySeamsPassedAdded':0,'wholeCityJunctionsPassedAdded':0,'generatedImagesByThisAgent':0,'sharedRecordsModified':False,'sourceShaVerifiedAtEnd':sha(v['source']['file'])}
(p/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'report':str(p/'visual-review.json'),'sha256':sha(p/'visual-review.json'),'counts':report['counts']},ensure_ascii=False))
