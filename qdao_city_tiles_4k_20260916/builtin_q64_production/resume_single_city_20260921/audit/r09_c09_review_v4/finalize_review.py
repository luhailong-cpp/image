from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,json,hashlib
OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((OUT/'crop-manifest.json').read_text(encoding='utf-8'))
for e in m['entries']:
    if e.get('identicalToPreviouslyViewedEvidence'):
        e['reviewMethod']='inherited previous original-pixel visual review after exact PNG SHA equality verified'
        e['viewedFreshThisRound']=False
    else:
        e['reviewMethod']='view_image detail=original, actually visually inspected this round'
        e['viewedFreshThisRound']=True
    e['reviewCoverageSatisfied']=True
(OUT/'crop-manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
source=Path(m['source']);a=np.array(Image.open(source).convert('RGB'))
left=np.array(Image.open(m['neighbors'][0]['file']).convert('RGB'))
bottom=np.array(Image.open(m['neighbors'][2]['file']).convert('RGB'))
metrics={'bottomBoundaryMeanAbsoluteRgbDifference':float(np.abs(a[-1].astype(float)-bottom[0]).mean()),
 'currentBottomAdjacentRowMeanAbsoluteRgbDifference':float(np.abs(a[-1].astype(float)-a[-2]).mean()),
 'neighborTopAdjacentRowMeanAbsoluteRgbDifference':float(np.abs(bottom[0].astype(float)-bottom[1]).mean()),
 'leftBoundaryMeanAbsoluteRgbDifference':float(np.abs(left[:,-1].astype(float)-a[:,0]).mean()),
 'bottomDarkGrooveSample':{'searchX':[1300,1460],'upperMinimumX':1300+int(a[-1,1300:1460].mean(axis=1).argmin()),
  'lowerMinimumX':1300+int(bottom[0,1300:1460].mean(axis=1).argmin())},
 'meaning':'Supplementary diagnostics only. Scalar pixel differences are not visual acceptance and do not measure a universal geometric shift.'}
extra={
 'external_left_y640_detail.png':[-256,384,256,896],
 'external_left_y1376_detail.png':[-256,1120,256,1632],
 'external_bottom_x1408_detail.png':[1152,3840,1664,4352],
 'external_bottom_x1856_detail.png':[1600,3840,2112,4352]}
issues=[
 {'id':'V4-EXTERNAL-LEFT','priority':'P1','status':'not_passed','tileLocalBoundary':'x=0, y=0..4095',
  'wholeCityBoundary':{'x':32768,'yStart':32768,'yEndExclusive':36864},
  'finding':'Joining unchanged r09_c08 v5 and this r09_c09 v4 produces a visible straight material/tone boundary. The full-length board also shows small white-highlight/bevel discontinuities, especially around local y600-700 and y1300-1600. The map structures continue in the same general direction; no large road-layout displacement is claimed.',
  'focusedLocationsApproximate':[[0,625],[0,1376]],
  'evidence':['external_left_r09_c08_c09_full_4096_native.png','external_left_y640_detail.png','external_left_y1376_detail.png'],
  'requiredRepair':'Reconcile the shared material/tone and the specific small rim mismatches in a versioned joint assembly. Preserve existing neighbor source and geometry; recheck all4096 pixels afterward.'},
 {'id':'V4-EXTERNAL-BOTTOM','priority':'P1','status':'not_passed','tileLocalBoundary':'y=4096, x=0..4095',
  'wholeCityBoundary':{'y':36864,'xStart':32768,'xEndExclusive':36864},
  'finding':'Joining unchanged r10_c09 v5 creates a horizontal material/tone line along the produced bottom boundary. Near x1409 the dark groove and its white rim change position/width slightly. A sampled darkest groove point shifts from upper x1409 to lower x1412, about3px; this does not support a claim of a large structural break.',
  'focusedLocationsApproximate':[[1409,4096],[1901,4096]],
  'evidence':['external_bottom_r09_c09_r10_c09_full_4096_native.png','external_bottom_x1408_detail.png','external_bottom_x1856_detail.png'],
  'requiredRepair':'Preserve the slab pattern and bring the shared edge into local geometric and material continuity in a new joint version. Review the complete4096-pixel boundary, not only the groove crop.'},
 {'id':'V4-EXTERNAL-JUNCTION','priority':'P1','status':'not_passed',
  'tileLocalPixelXY':[0,4096],'wholeCityPixelXY':[32768,36864],
  'finding':'The four-tile board shows a texture/tone quadrant change at the intersection. Stone joints remain generally connected, but the corner cannot be accepted while both incident new boundaries fail.',
  'evidence':['external_four_tile_junction.png'],
  'requiredRepair':'Recheck this corner from the final shared-boundary outputs of r09c08/r09c09/r10c08/r10c09.'},
 {'id':'V4-STYLE-OBS01','priority':'P2','status':'remaining_art_observation_not_accepted',
  'regionApproximateLTRB':[2250,880,2970,1150],
  'finding':'The prior OBS-01 dense streak/flake texture remains on an upper slab outside the central stone cleanup. The central repaired slab is substantially cleaner; that limited result does not establish uniform clean-stone styling over the entire tile.',
  'evidence':['h1024_full_4096_native.png','repair_v4_final_support.png'],
  'requiredRepair':'Review and, if retaining the clean-stone target, simplify the affected stone-face texture without changing slab joints or bevel geometry.'}
]
old_results=[
 {'previousId':'R09C09-01','result':'specific_defect_resolved_in_reviewed_area',
  'evidence':['junction_x1024_y3072.png','repair_v2_final_support.png'],
  'finding':'The former abrupt highlight step and gray hard blocks are no longer visible in the exact target area. The continuing step highlight and gray faces reconnect cleanly.'},
 {'previousId':'R09C09-02','result':'specific_central_slab_defect_resolved_in_reviewed_area',
  'evidence':['junction_x2048_y2048.png','repair_v3_final_support.png'],
  'finding':'Dense scratches/flaky streaks on the targeted central slab face are replaced by sparse broad painted variation. Adjacent slabs and some inherited bevel texture were outside this material mask; broader style observation remains separate.'},
 {'previousId':'R09C09-03','result':'specific_defect_resolved_in_reviewed_area',
  'evidence':['junction_x3072_y1024.png','repair_v4_final_support.png'],
  'finding':'The two narrow highlighted rim interruptions targeted by v4 are now continuous in the reviewed native crop.'}
]
report={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),
 'source':m['source'],'sourceSha256':m['sourceSha256'],'sourceUnchanged':sha(source)==m['sourceSha256'],
 'neighborSources':m['neighbors'],'neighborSourcesUnchanged':all(sha(Path(n['file']))==n['sha256'] for n in m['neighbors']),
 'status':'candidate_retained_external_neighbor_QA_failed','formalArtAccepted':False,'runtimePublished':False,
 'coverage':{'internalFullSeamsFreshlyViewed':6,'internalSegmentsFreshlyViewed':24,
  'internalJunctionsFreshlyViewed':3,'internalJunctionsInheritedAfterExactShaMatch':6,
  'repairFinalSupportsFreshlyViewed':3,'actualRepairMasksFreshlyViewed':3,
  'externalFullSeamsFreshlyViewed':2,'externalSegmentsFreshlyViewed':8,'externalFourTileJunctionsViewed':1,
  'externalDetailCropsViewed':4,'resizedEvidenceImages':0},
 'repairChainVerification':{'versions':[2,3,4],'verifiedRecordedFiles':42,'fileShaMismatches':0,
  'changedPixelsOutsideActualMaskPerVersion':[v['changedOutsideMask'] for v in m['repairMechanicalVerification']],
  'actualMaxRegistrationShiftXYPerVersion':[v['actualMaxShiftXY'] for v in m['repairMechanicalVerification']],
  'resamplingDisclosure':'Three native1254 repairs retained original bytes. Their assembly used bounded subpixel geometric registration and local color matching; this is not a no-resampling or single-native4K claim.'},
 'previousDefects':old_results,
 'internalContinuityFinding':'No definitive new internal contour break was observed in six whole seam boards and nine covered junctions. This scoped observation does not pass whole-tile art because existing-neighbor boundaries fail and broader stone texture remains under review.',
 'repairMaskReturnFinding':'The entire1254 support of each final repair and its actual cross/polygon/horizontal mask were viewed. No definitive new clipped contour or hard mask-return boundary was observed around these repair contours. Mechanical outside-mask invariance was independently verified, not substituted for visual inspection.',
 'issues':issues,'metrics':metrics,
 'extraEvidence':[{'file':str(OUT/name),'sha256':sha(OUT/name),'sourceBoxRelativeToCurrentTileLTRB':box,'resized':False,'viewedAtOriginalPixels':True} for name,box in extra.items()],
 'priorityOrder':['V4-EXTERNAL-LEFT','V4-EXTERNAL-BOTTOM','V4-EXTERNAL-JUNCTION','V4-STYLE-OBS01'],
 'notReviewed':['missing top and right delivery neighbors','whole256 tile city','navigation/entrances/foreground','game nearest camera/movement/device performance'],
 'sourceFilesModifiedByReviewer':False}
(OUT/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='''# r09_c09 v4 第二轮 QA：保留候选，外邻边界不通过

源 SHA：`3421c5b29eea9cc72b00825738d339f4786572b477ee70cdd8c86894a4f34d50`。

原 3 处定点缺陷已在修补范围内解决：左下台阶高光/灰面、中央大石板密集石纹、右上斜向细白沿。重新查看 6 条完整内缝与 3 个改变的交点；另外 6 个交点裁图 SHA 与首轮完全相同，继承已实际看过的记录。三份最终1254支持图和实际遮罩均查看，未见明确的新遮罩返回边断口。

三版修补共 42 项文件 SHA 匹配，实际遮罩外像素变化均为 0。记录保留了亚像素配准与局部色彩匹配，不能声称完全无重采样。

新增的左邻、下邻与四块交点检查仍失败：

- **左边 x=0**：与 r09_c08 v5 拼接后有直线材质/色调分界，约 y600–700、y1300–1600 的高光/倒角有小错口。
- **下边 y=4096**：与 r10_c09 v5 有横向材质/亮度分界。约 x1409 的暗石缝上侧最低点 x1409、下侧 x1412，约 3px；不夸大为道路整体错位。白沿宽度也变化。
- **四块交点 (0,4096)**：可见纹理/色调象限变化，两个新边界未合格，交点不能通过。
- 首轮 OBS-01 的上方石板密集刮刷纹理仍在，中央一片修复不能证明全块美术风格统一。

所有坐标均相对 r09_c09 左上原点；全图对应左边 x32768、下边 y36864。边界板覆盖两条完整4096px接缝，另有4张原像素缺陷特写。优先修两条共享边界并一起复查交点，保留现有邻块源与回退版本。

未修改任何候选、修补记录、邻块或共享状态。未将本块加入通过或正式成品清单。
'''
(OUT/'README.md').write_text(text,encoding='utf-8')
print(json.dumps({'status':report['status'],'coverage':report['coverage'],'metrics':metrics,
 'sourceUnchanged':report['sourceUnchanged'],'neighborsUnchanged':report['neighborSourcesUnchanged']},indent=2))
