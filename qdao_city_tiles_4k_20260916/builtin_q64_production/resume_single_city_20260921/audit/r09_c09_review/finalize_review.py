from pathlib import Path
from datetime import datetime, timezone
import json,hashlib

OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((OUT/'crop-manifest.json').read_text(encoding='utf-8'))
for entry in manifest['entries']:
    entry['viewedAtOriginalPixels']=True
    entry['reviewMethod']='tools.view_image(detail=original) with image emitted at original detail; all four seam panels visually read'
(OUT/'crop-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

issues=[
 {'id':'R09C09-01','priority':'P1','category':'contour_and_tonal_seam','blocksCandidateAcceptance':True,
  'title':'Lower-left continuous steps have a highlight step and hard gray-face patches',
  'approximatePrimaryPixelXY':[928,3114],
  'approximateAdditionalPixelXY':[[944,3260],[1024,3408]],
  'observedBoundsLTRB':[880,3020,1190,3450],
  'evidence':['junction_x1024_y3072.png','defect_step_highlight_gray_block.png','v1024_full_4096_native.png','h3072_full_4096_native.png'],
  'finding':'The long ivory step is not interrupted by a stone joint at this location, yet its white front highlight makes an abrupt small step near x928/y3114. The gray face immediately below and the next lower bevel show straight-edged light/dark patches, inconsistent with the continuing slab. This is visible at native pixel scale, not inferred from a seam metric.',
  'suggestedNativeSupportLTRB':[397,2553,1651,3807],
  'repairIntent':'Redraw only the affected continuous step/bevel faces and reconnect the long white highlight. Keep the top stair silhouettes, all slab joints, perspective and road geometry. Do not blur the seam or replace the whole support image.',
  'requiredRecheck':['full x1024 internal seam','full y3072 internal seam','x1024/y3072 junction','all actual repair-mask return edges']},
 {'id':'R09C09-02','priority':'P1','category':'material_style_inconsistency','blocksCandidateAcceptance':True,
  'title':'Central stone panel switches to dense scratched and flaky material',
  'approximatePrimaryPixelXY':[2048,1900],
  'observedBoundsLTRB':[1830,1550,2400,2160],
  'evidence':['junction_x2048_y2048.png','defect_dense_stone.png','v2048_full_4096_native.png','h2048_full_4096_native.png'],
  'finding':'The central gray-ivory slab has a large cluster of dense fine diagonal scratch marks and irregular flake-like layers; the left side is much smoother. It creates a strong material-density boundary and conflicts with the clean rounded stone direction. The pattern also reaches the bevel instead of reading as a few broad intentional painted shapes. This is an art-style rejection; no road break is claimed at this location.',
  'suggestedNativeSupportLTRB':[1433,1233,2687,2487],
  'repairIntent':'Regenerate clean ivory/gray stone faces with sparse broad soft color shapes and crisp existing bevel geometry. Preserve all current stone joints, slab edges and shading direction. Use a material-only mask within the affected slab; no noise, sharpening or diffuse blur.',
  'requiredRecheck':['full x2048 internal seam','full y2048 internal seam','x2048/y2048 junction','material transition at all patch-mask edges']},
 {'id':'R09C09-03','priority':'P2','category':'small_contour_step','blocksCandidateAcceptance':True,
  'title':'Upper-right diagonal inner rim has a small stepped highlight lip',
  'approximatePrimaryPixelXY':[3280,1000],
  'approximateAdditionalPixelXY':[[2995,942]],
  'observedBoundsLTRB':[2950,900,3330,1090],
  'evidence':['junction_x3072_y1024.png','defect_thin_inner_rim.png','v3072_full_4096_native.png','h1024_full_4096_native.png'],
  'finding':'On the continuous diagonal inner border, the narrow white rim makes a visible little notch/step near x3280/y1000. A second rough highlight lip is visible near x2995/y942. The overall road/step direction is continuous; this is a local edge defect, not a claim of large geometric displacement.',
  'suggestedNativeSupportLTRB':[2445,397,3699,1651],
  'repairIntent':'Locally redraw the two thin rim interruptions as continuous clean beveled edges. Preserve both sides of the diagonal rail, adjacent slab corners, spacing and illumination; do not erase the intended shadow groove.',
  'requiredRecheck':['full x3072 internal seam','full y1024 internal seam','x3072/y1024 junction','all actual repair-mask return edges']}
]

observations=[
 {'id':'OBS-01','priority':'P2','regionLTRB':[2250,880,2970,1150],
  'evidence':['h1024_full_4096_native.png'],
  'finding':'A second broad stone patch above/right of the central slab also has visibly dense streak/flake texture. Re-evaluate it together with R09C09-02 so a repaired small center crop does not leave the same style problem nearby.'},
 {'id':'OBS-02','regionLTRB':[2816,2816,3328,3328],
  'evidence':['junction_x3072_y3072.png'],
  'finding':'Broad painted tone variation remains on the sloping front face. I did not see a definitive broken contour here; do not classify every broad paint shape as a geometric seam.'}
]
seam_findings={
 'v1024':['R09C09-01'],'v2048':['R09C09-02'],'v3072':['R09C09-03'],
 'h1024':['R09C09-03','OBS-01'],'h2048':['R09C09-02'],'h3072':['R09C09-01']}
seams=[]
for key,ids in seam_findings.items():
    entry=next(e for e in manifest['entries'] if Path(e['file']).stem==key+'_full_4096_native')
    seams.append({'seam':key,'fullLengthPixels':4096,'allFourSegmentsViewed':True,
      'segmentRangesInclusive':[[0,1023],[1024,2047],[2048,3071],[3072,4095]],
      'sourceBoxesLTRB':entry['sourceBoxesLTRB'],'evidenceFile':entry['file'],'evidenceSha256':entry['sha256'],
      'observations':ids,'artAcceptancePassed':False})
junction_map={(1024,3072):['R09C09-01'],(2048,2048):['R09C09-02'],(3072,1024):['R09C09-03'],(3072,3072):['OBS-02']}
junctions=[]
for y in [1024,2048,3072]:
    for x in [1024,2048,3072]:
        name=f'junction_x{x}_y{y}.png'
        ids=junction_map.get((x,y),[])
        junctions.append({'pixelXY':[x,y],'evidenceFile':str(OUT/name),'sha256':sha(OUT/name),
            'viewedAtOriginalPixels':True,'findings':ids,
            'observation':'listed finding requires follow-up' if ids else 'No definitive broken contour observed in this crop; not a whole-tile acceptance.',
            'wholeTileArtAcceptancePassed':False})
defect_boxes={'defect_step_highlight_gray_block.png':[768,2816,1280,3456],
              'defect_dense_stone.png':[1696,1504,2400,2208],
              'defect_thin_inner_rim.png':[2872,768,3384,1280]}
report={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
 'reviewer':'independent inventory_audit subagent','sourceFile':manifest['source'],
 'sourceSha256':manifest['sourceSha256'],'sourceUnchangedAtReviewFinish':sha(Path(manifest['source']))==manifest['sourceSha256'],
 'status':'rejected_internal_visual_QA_repair_required','artAcceptancePassed':False,'formallyAccepted':False,
 'runtimePublished':False,'wholeCityComplete':False,
 'coverage':{'fullVerticalSeams':3,'fullHorizontalSeams':3,'nativeSegmentsViewed':24,'junctionsViewed':9,
             'extraDefectCropsViewed':3,'sourcePixelsPerDisplayedArtPixel':1},
 'method':'Pillow lossless exact-coordinate crops and non-overlapping labeled boards, no resize. Every listed board and all nine junction crops were actually opened with view_image detail=original. The existing 1024 overview was read for composition only.',
 'toolLimitObserved':'Direct opening of the large 4096 source failed in the view transport with invalid base64; source fully decoded in Pillow, and exact-scale crops were successfully viewed instead.',
 'seams':seams,'junctions':junctions,'issues':issues,'observations':observations,
 'extraDefectEvidence':[{'file':str(OUT/name),'sha256':sha(OUT/name),'sourceBoxLTRB':box,'resized':False,'viewedAtOriginalPixels':True} for name,box in defect_boxes.items()],
 'priorityOrder':['R09C09-01','R09C09-02','R09C09-03','OBS-01'],
 'recommendedDisposition':'Retain source candidate and native sources; do not merge this candidate as locally passed or formal art. Produce bounded native repair revisions with mask/source/SHA records, then recheck all affected full seams, junctions and every actual ROI edge.',
 'outsideThisReview':['seams to delivery tile r09_c08 and r10_c09','four-delivery-tile junction','global layout/navigation/entrances','complete 256-tile city','foreground','game nearest camera/movement/device performance']}
(OUT/'visual-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
text='''# r09_c09 独立原像素检查：不通过

对象 SHA：`ec6b067c57c98ee21cdb4ef3bad6b0df8481920b6d11409c1b74348834946171`。保留原候选；本检查未生图、未改任何成品或共享统计。

已实际查看 3 竖 + 3 横内部接缝的全部 4096 像素，每条以 4 个顺序原像素面板覆盖；另查看 9 个 512×512 四补丁交点和 3 张缺陷特写。裁图未缩放、未滤镜、未混色。总览仅看构图。

优先修补：

1. **P1，约 (928,3114)**：连续台阶白高光突成小台阶；其下约 (944,3260) 灰面和更下一级出现硬色块。见 `defect_step_highlight_gray_block.png`。先保持石缝位置，局部原生重绘高光和灰面，不能靠模糊压住。
2. **P1，约 (2048,1900)，范围约 x1830–2400/y1550–2160**：中央石板细密刮痕、片状石纹与左侧平整石面反差明显，不符合明亮干净 Q 版方向。见 `defect_dense_stone.png`。要清理整片实际受影响石面，不能只把 x2048 附近抹软；上方 x2250–2970/y880–1150 也有相同材质密度问题。
3. **P2，约 (3280,1000)**：斜向细白内沿有小错口，另约 (2995,942) 高光唇边不顺。见 `defect_thin_inner_rim.png`。这是局部轮廓缺陷，未判定为道路整体错位。

`visual-review.json` 保存逐接缝、逐交点覆盖、建议 1254px 原生修补支持框、实际缺陷坐标与复查项。建议框不是可直接整块贴回的遮罩；须限定实际修补区域并验四周返回边。

本轮未检查与 r09_c08/r10_c09 的跨正式图块边界、四正式图块交点、导航、前景或实机镜头。内部检查已失败，因此候选不能进入局部通过或正式成品清单。
'''
(OUT/'README.md').write_text(text,encoding='utf-8')
print(json.dumps({'status':report['status'],'coverage':report['coverage'],'issues':len(issues),
    'sourceUnchanged':report['sourceUnchangedAtReviewFinish']},indent=2))
