from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
OUT=Path(__file__).resolve().parent
RESUME=OUT.parents[1]
JOIN=RESUME/'tools/neighbor_join_v5'
V6=RESUME/'tools/repairs/versions/r09_c09_repair_v6'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
p=json.loads((OUT/'verification.json').read_text(encoding='utf-8'))
a=json.loads((JOIN/'assembly-v5.json').read_text(encoding='utf-8'))
r=json.loads((V6/'repair.json').read_text(encoding='utf-8'))
mask_crops=json.loads((OUT/'v6-mask-return-crops.json').read_text(encoding='utf-8'))
qa=[]
for e in a['qa']:
    e=dict(e);before='_before_v4_' in Path(e['file']).name
    e['viewedFreshThisRound']=not before
    e['reviewRole']='historical before board: hash verified, not counted as fresh viewing' if before else 'actually viewed through view_image detail=original; all four panels read for full-strip boards'
    qa.append(e)
v5={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'sourceCandidate':p['v5Candidate'],'sourceSha256':p['v5Sha256'],
 'status':'reviewed_existing_neighbor_and_treatment_return_continuity_passed_candidate_only',
 'localBoundaryContinuityPassed':True,'formalArtAccepted':False,'productionAccepted':False,'runtimePublished':False,
 'scope':'Only the existing left/bottom delivery neighbors, their complete treatment-return lines, one four-delivery-tile corner and registration-cap risk locations. Not missing top/right neighbors, whole city, navigation or runtime.',
 'coverage':{'fullExternalBoundariesFreshlyViewed':2,'fullTreatmentReturnLinesFreshlyViewed':2,
   'nativeFullLineSegmentsViewed':16,'fourTileCornerFreshlyViewed':1,'treatmentReturnCornerFreshlyViewed':1,
   'previousProblemDetailCropsFreshlyViewed':4,'nearCapClusterCropsFreshlyViewed':4,
   'providedQaFilesHashVerified':12,'providedCurrentQaFilesFreshlyViewed':10,
   'historicalBeforeQaFilesNotCountedAsFreshlyViewed':2,'resizedEvidenceImages':0},
 'findings':[
  {'id':'left_existing_neighbor','result':'pass_scoped_local_visual_review',
   'detail':'All4096 pixels across r09_c08/r09_c09 were read as four native segments, plus prior problem crops y640/y1376. The previous narrow tone split and small rim offsets no longer form a definite hard seam. General stone texture variation remains, but no broken slab contour was observed across the reviewed boundary.'},
  {'id':'bottom_existing_neighbor','result':'pass_scoped_local_visual_review',
   'detail':'All4096 pixels across r09_c09/r10_c09 were read with the transposed axes explicitly accounted for, plus x1408/x1856 crops. The previous groove step and horizontal tone line are not visibly discontinuous in these current v5 images.'},
  {'id':'treatment_returns','result':'pass_scoped_local_visual_review',
   'detail':'The full x215 return line and full y3880 return line were viewed in four native segments each, with the southwest return corner. No new clipped rim, hard color band or blurred return line was observed.'},
  {'id':'four_delivery_tile_corner','result':'pass_scoped_local_visual_review',
   'detail':'The actual r09c08/r09c09/r10c08/r10c09 corner was viewed. Stone joints and highlights remain joined, with gradual painted surface variation rather than the former abrupt quadrant split.'},
  {'id':'near_eight_pixel_cap','result':'pass_scoped_local_visual_review_with_resampling_disclosure',
   'detail':'All four effective near-cap clusters were viewed in additional512px native support crops. No definitive distortion, doubled contour or new edge break was observed at those locations. Reaching8px and matching hashes were not treated as visual pass evidence by themselves.'}
 ],
 'independentMechanicalEvidence':{'sourceOutputQaHashChecks':len(p['v5Checks']),'failedChecks':p['v5FailedChecks'],
  'interiorPixelsEqualV4':p['v5InteriorEqualsV4'],'interiorRectLTRB':[215,0,4096,3881],
  'nineInternalJunctionsEqualV4':all(x['v5PixelsEqualV4'] for x in p['v5InternalJunctionInheritance'])},
 'internalCoverageInheritance':'V4 internal review is retained only for unchanged pixels. The interior rectangle and all9 internal junction crops were independently compared at raw pixel level; altered left/bottom strips are covered by current full boundary and return boards.',
 'nearCapDisclosure':p['v5NearCap'],
 'resamplingDisclosure':'Recorded bounded subpixel registration max8px and local RGB correction max18 on the left/bottom treatment bands. No artwork enlargement; not a no-resampling claim.',
 'qaEvidence':qa,'extraEvidence':[e for e in p['extraEvidence'] if 'near_cap_' in Path(e['file']).name],
 'remaining':['upper material OBS01 in v5 is evaluated separately on v6','top/right future neighbors','full256 tiles and all external seams/junctions','foreground/navigation/entrances','closest game camera and movement','device performance'],
 'sourceUnchanged':sha(Path(p['v5Candidate']))==p['v5Sha256']}
(OUT/'visual-review-v5.json').write_text(json.dumps(v5,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
v6={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'latestReviewedCandidate':p['v6Candidate'],'candidateSha256':p['v6Sha256'],
 'status':'local_reviewed_candidate_v6_scoped_continuity_passed_not_formal_city_acceptance',
 'scopedLocalContinuityPassed':True,'formalArtAccepted':False,'productionAccepted':False,'runtimePublished':False,
 'v5BoundaryEvidence':str(OUT/'visual-review-v5.json'),'v5BoundaryEvidenceSha256':sha(OUT/'visual-review-v5.json'),
 'v6MaterialFinding':'The previously identified OBS01 target region on the upper slab now uses broad sparse painted variation. The dense streak/flake patch in that target region is removed. Neighboring natural painted stone texture remains and is not claimed to be globally eliminated.',
 'v6ReturnFinding':'The full1254 context, actual mask, four native mask-return strips and two changed internal junction crops were actually viewed. Return strips include actual full-tile pixels beyond the left/right native support. No definitive new hard mask band, clipped bevel or contour break was observed.',
 'coverage':{'repairSupportFreshlyViewed':1,'actualMaskFreshlyViewed':1,'maskReturnStripsFreshlyViewed':4,
  'changedInternalJunctionsFreshlyViewed':2,'internalJunctionsInheritedByRawPixelEquality':7,
  'existingOuterBoundariesInheritedFromCurrentV5Review':2,'resizedEvidenceImages':0},
 'independentMechanicalEvidence':{'v6RepairHashChecks':len(p['v6Checks']),'failedChecks':p['v6FailedChecks'],
  'changedPixels':p['v6ChangedPixels'],'changedOutsideActualMask':p['v6ChangesOutsideMask'],
  'fullContextAfterEqualsFinalTileCrop':p['v6FullRepairContextMatchesFinalCrop'],
  'entireLeft375pxBandEqualsReviewedV5':p['v6LeftTreatmentBandUnchanged'],
  'entireBottomFromY3720EqualsReviewedV5':p['v6BottomTreatmentBandUnchanged']},
 'internalCoverageInheritance':'V6 equals reviewed v5 outside its actual mask. Its changed pixels lie within the fully viewed1254 support; the2 changed junctions were additionally viewed and the other7 junctions are pixel-identical. Prior whole seam coverage is inherited only for unchanged portions.',
 'repairSupport':{'file':str(V6/'context-after.png'),'sha256':sha(V6/'context-after.png'),'viewedAtOriginalPixels':True},
 'mask':{'file':str(V6/'mask.png'),'sha256':sha(V6/'mask.png'),'viewedAtOriginalPixels':True},
 'returnCrops':mask_crops,
 'changedJunctionEvidence':[e for e in p['extraEvidence'] if 'v6_junction_' in Path(e['file']).name],
 'junctionInheritance':p['v6InternalJunctionInheritance'],
 'resamplingDisclosure':r['resampling'],'recordedActualModel':r['actualModel'],'backendModelVerified':r['backendModelVerified'],
 'remaining':['top/right future neighbors and their junctions','full256 tile city and all cross-tile seams','foreground/navigation/entrances','nearest game camera and movement','device performance'],
 'sourceUnchanged':sha(Path(p['v6Candidate']))==p['v6Sha256'],
 'reviewerChangedProductionFiles':False}
(OUT/'visual-review-v6.json').write_text(json.dumps(v6,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='''# r09_c09 第三轮：v5 共享边界通过局部检查；最新 v6 保持候选

最新检查对象为 `tools/repairs/versions/r09_c09_repair_v6/r09_c09.png`，SHA：`5ce3e9099c4292a3c2d2b854bcc6d2cfd3b8858bb6960bc8e7966699ade4742c`。

v5 已重新检查左/下两条完整4096px共享边界、两条完整处理带返回线、四块交点、返回带交点、4张旧问题特写及4张近8px配准位置特写。当前未见明确断裂轮廓、硬色带或新增模糊返回线，已给出**仅此范围的局部连续性通过**。v4外边失败是历史结论，不作为v5/v6当前结论。

触顶统计写明口径：有效核心 mask>0 且任一方向位移≥7.999px，共587像素；精确8.0px为449像素，分4个区域。已逐区域看原像素，并非因触顶或SHA一致而自动判过。

v6 清除了上方OBS01目标石板的密集刮刷纹理。已看完整1254支持图、实际遮罩、4条返回边和2个变化交点；未见新接缝。独立核实遮罩外改动为0，整个左375px及下方y3720起的图带与本轮已审v5完全同像素，所以继承当前v5外边证据。其余7个内部交点按原像素SHA一致继承。

校验：v5来源/输出/QA共30项SHA、v6修补链14项SHA均通过。有限亚像素配准和局部色彩匹配如实披露，不声称无重采样或单次原生4K。

这是局部候选QA，**正式成品=false、整城验收未完成、客户端实机未验**。上/右尚无邻块，后续256块整城、前景、导航、出入口、最近镜头与移动仍须检查。未修改源图、邻块、共享统计或旧报告。

记录：`visual-review-v5.json`、`visual-review-v6.json`、`verification.json`。来源12张QA中10张当前v5证据实际查看；2张v4对比板仅校验SHA，不计本次查看数量。
'''
(OUT/'README.md').write_text(text,encoding='utf-8')
print(json.dumps({'v5Status':v5['status'],'v6Status':v6['status'],'latestSha256':v6['candidateSha256'],
 'sourcesUnchanged':v5['sourceUnchanged'] and v6['sourceUnchanged'],'formalArtAccepted':False},indent=2))
