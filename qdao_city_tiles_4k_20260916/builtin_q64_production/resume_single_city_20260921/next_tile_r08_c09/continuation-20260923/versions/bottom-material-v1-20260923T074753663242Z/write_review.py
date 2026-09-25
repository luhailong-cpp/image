"""Persist append-only review after direct view_image inspection; does not edit artwork."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
V=Path(__file__).resolve().parent
BASE=V.parent/'hard-core-20260923T070734660600Z'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def linked(p): return {'file':str(p),'sha256':sha(p)}
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write_new(p,data):
    if p.exists(): raise RuntimeError(f'Refuse overwrite {p}')
    with p.open('x',encoding='utf-8',newline='\n') as f:
        f.write(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
q=read(V/'qa/index.json');s=read(V/'qa/supplement-index.json');r=read(V/'repair.json')
for item in [q['candidate'],q['repair'],r['neighbor'],r['sourceCandidate'],r['sourceRecord'],r['mask'],*q['evidence'],*s['evidence']]:
    assert sha(item['file'])==item['sha256'],item['file']
a=np.asarray(Image.open(r['sourceCandidate']['file']).convert('RGB'))
b=np.asarray(Image.open(q['candidate']['file']).convert('RGB'))
mask=np.asarray(Image.open(r['mask']['file']))
assert np.array_equal(a[mask==0],b[mask==0])
assert np.array_equal(a[:3768],b[:3768])
now=datetime.now(timezone.utc).isoformat()
results=[]
for e in q['evidence']:
    k=e['kind'];i=e['id']
    status='local_geometry_pass';observed='No new geometry break or distinct horizontal return line observed in inspected 1:1 crop. This does not approve material cleanliness.'
    if i=='bottom-edge-01':
        status='fail_material_cleanliness'
        observed='Upper candidate now carries broad irregular cream cloud patches to meet fixed lower neighbor. The visible bottom interface is less abrupt, but this violates the requested clean restrained stone material. Geometry appears locally continuous.'
    elif i=='bottom-edge-02':
        status='local_edge_continuity_pass'
        observed='In the inspected 1024x256 original-pixel strip, gray bevels and gray slab tone continue across boundary with no obvious new positional break. Gray mottling remains; pass is only this local edge strip and does not approve the full tile or other patches.'
    elif i=='bottom-edge-03':
        status='pending_fine_bevel_joint'
        observed='Gold/gray major geometry continues, but a small bevel kink at the tile boundary near candidate x2410-2430 remains ambiguous in the 384x384 focus crop. No geometry pass assigned for this segment.'
    elif i=='bottom-edge-04':
        status='fail_material_cleanliness'
        observed='Dense cream/gold vein and flake texture remains in the fixed lower neighbor and now extends into the upper candidate band. Wider original-pixel crop confirms a broad material-density transition. Clean style not achieved.'
    elif k=='affected_internal_seam':
        status='pending_inherited_tonal_boundary'
        observed='No gross new geometric step observed in the narrow 256x1024 strip. Wider before/after crop reveals low-amplitude tonal-boundary concerns near the existing core cut, including above the permitted repair band. Earlier geometry impression is insufficient to mark the entire seam passed; require independent visual recheck/material repair.'
    results.append({**e,'reviewed':True,'reviewMethod':'view_image original pixels','status':status,'observation':observed})
supp=[]
for e in s['evidence']:
    if e['id']=='wide-bottom-fourth':
        status='fail_material_cleanliness'
        note='Fixed neighbor contains pronounced layered cloud/vein shapes; reproducing them in upper patch compromises clean material target.'
    elif e['id']=='focus-bottom-gold-joint':
        status='pending_fine_bevel_joint'
        note='Original-pixel enlarged-context evidence only, not image enlargement. Small gold-bevel joint uncertainty near x2410-2430 at y4096 not resolved; no pass.'
    else:
        status='pending_inherited_tonal_boundary'
        note='768px-wide original-pixel context supports caution about faint core-cut tonal transitions. Not a proven geometry failure. Before/after both retained as linked QA until parent resolves candidate selection.'
    supp.append({**e,'reviewed':True,'reviewMethod':'view_image original pixels','status':status,'observation':note})
f=a.astype(np.float32)
metrics=[]
for x in [1024,2048,3072]:
    metrics.append({'x':x,'yRange':[3469,3768],'acrossCoreCutMeanAbsoluteRGB':np.abs(f[3469:3768,x]-f[3469:3768,x-1]).mean(axis=0).tolist(),'onePixelLeftMeanAbsolute':float(np.abs(f[3469:3768,x-1]-f[3469:3768,x-2]).mean()),'onePixelRightMeanAbsolute':float(np.abs(f[3469:3768,x+1]-f[3469:3768,x]).mean())})
review={
 'schemaVersion':1,'reviewedAtUtc':now,'tile':'r08_c09','candidate':q['candidate'],'repair':q['repair'],'qaIndex':linked(V/'qa/index.json'),'supplementIndex':linked(V/'qa/supplement-index.json'),
 'status':'failed_bottom_material_repair_batch','formalAccepted':False,'productionAccepted':False,'clientValidated':False,
 'scope':'Four native 1254 repair outputs; c09 bottom y3768..4096 only. All 14 generated QA artifacts and all 8 supplemental original-pixel crops directly inspected. No fifth generation.',
 'actualModel':None,'actualQuality':None,
 'mechanicalVerification':{'outsideMaskPixelsUnchanged':True,'candidateYBefore3768Unchanged':True,'fixedNeighborShaReverified':r['neighbor'],'resampling':'none','registration':'none','colorCorrection':'none','topReturnPixels':32},
 'evidence':results,'supplementalEvidence':supp,
 'tonalBoundaryDiagnostic':{'source':r['sourceCandidate'],'meaning':'Pixel differences support reinspection only; numerical magnitude alone is not an art pass or failure. These rows are above repair band and unchanged in new candidate.','values':metrics},
 'unchangedInheritedScope':q['unchangedInheritedScope'],
 'priorReviewAmendment':'Earlier original candidate review stated all 24 internal seam segments locally passed. The three bottom vertical segments are now pending due wider-context tonal-boundary concerns. Do not count them as passed. Previous report is retained unchanged; this newer supplementary review controls this scope. The concerns are not asserted as proven geometric misalignment.',
 'otherEdges':'Uninspected for this repair; pending neighbors and inspection','externalFourTileJunctions':'pending; not passed',
 'disposition':'Do not promote this repair to latest/production. The batch could not simultaneously match the fixed noisy lower neighbor and retain the clean new stone style. Parent must choose the next art strategy; no changes to r09_c09 repair_v6.'
}
write_new(V/'visual-review.json',review)
text="""# r08_c09 bottom-material v1 原像素复核

本批 4 张原生 1254 修补已完成，候选未通过，不提升为正式成品。actualModel / actualQuality 均未确认。

- 仅修改 c09 的 y3768..4096；顶部 32px 材质返回，未配准、缩放、模糊或调色。掩膜外像素与旧候选相等；r09_c09 repair_v6 核心 SHA 复核不变。
- 直接查看 14 张 QA 与 8 张补充原像素证据。第 2 段 x1024..2048 在此 1024×256 裁图内局部边界连续；不代表整块通过。
- 第 1 段 x0..1024 与第 4 段 x3072..4096 不通过：为了衔接旧邻，候选带入过量云斑、层叠脉状纹。第 4 段加宽裁图同时显示旧邻强烈碎纹，当前批次未能兼顾衔接与干净风格。
- 第 3 段 x2048..3072 待复核：约 x2410..2430 的金边接头存在微小阶差疑点，384×384 原像素补充图仍不足以确认通过。
- 4 段顶部返回与 3 个返回交点未见新增明显几何断口；该局部观察不豁免上述材质失败。
- 加宽证据对原有 x1024 / 2048 / 3072 的下段内部缝提出轻微色调边界疑点，数值差诊断仅辅助。撤回旧报告对这 3 段的通过状态，改为待复核；并未声称已证实几何错位。旧报告不覆写，以新补充记录为准。
- 未受改动的 3 条水平缝与 9 个内部交点可关联同 SHA 原候选旧复核范围；其他外边、四块外部交点、整城与客户端均未通过。

所有坐标为 r08_c09 局部像素，外边 y4096。完整逐证据结论、SHA 与诊断见 visual-review.json。未生成第 5 张，未修改共享 state、plan 或 latest-candidate。
"""
with (V/'visual-review.md').open('x',encoding='utf-8',newline='\n') as f: f.write(text)
amend={'schemaVersion':1,'createdAtUtc':now,'sourceCandidate':r['sourceCandidate'],'priorReview':q['unchangedInheritedScope']['sourceReview'],'supplementalReview':linked(V/'visual-review.json'),'status':'partial_prior_review_withdrawal','withdrawnPassScope':[{'x':x,'yRange':[3072,4096],'newStatus':'pending_inherited_tonal_boundary'} for x in [1024,2048,3072]],'reason':'Wider original-pixel context raised faint tonal-boundary concerns; not confirmed geometry failure. Do not count these three segments as passed until rechecked. This append-only record does not alter the prior review.','formalAccepted':False}
write_new(BASE/'visual-review-supplement-20260923-bottom-band.json',amend)
print(json.dumps({'review':linked(V/'visual-review.json'),'amendment':linked(BASE/'visual-review-supplement-20260923-bottom-band.json'),'neighbor':r['neighbor'],'status':review['status']},ensure_ascii=False))

