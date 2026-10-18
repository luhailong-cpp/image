from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import hashlib,json,re

O=Path(__file__).resolve().parent
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def write(f,d):Path(f).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
now=datetime.now(timezone.utc).isoformat();s=read(O/'summary.json')
with Image.open(s['candidate']['file']) as cur,Image.open(s['baselineV2']['file']) as old:
    assert cur.crop((0,0,4096,185)).convert('RGB').tobytes()==old.crop((0,0,4096,185)).convert('RGB').tobytes()
s['north185RowsPixelIdenticalToV2']=True
context=(O/'v3-changed-region-and-perimeters-100pct.png').as_posix()
focus=(O/'v3-old-focus-junction-x3072-y1024-100pct.png').as_posix()
for e in s['visualEvidence']:
    e.update({'actuallyViewed':True,'viewedAtUtc':now,'inspectionTool':'view_image','inspectionDetail':'original','inspectionScale':1})
    if e['id'].startswith('v2-'):
        e.update({'status':'before_comparison_only','finding':'v2原灯笼背景出现矩形清晰度跃变，供与v3对比，不能当作当前v3缺陷。'})
    elif e['id']=='external-top-4-100pct':
        e.update({'status':'not_passed_gold_rib_detail_pending','finding':'北边灯笼金色细棱仍有轻微宽度和横向台阶；本次未修图，保持同一问题开放。'})
    elif e['id']=='northeast-neighbor-fourway-100pct':
        e.update({'status':'fourway_center_contours_continuous_gold_rib_detail_pending',
             'finding':'四邻中心花叶与朱柱轮廓连续；左侧灯笼金棱跨北缝的细节仍按同一外接问题待修，不把整处外接升级通过。'})
    else:
        e.update({'status':'local_visual_passed',
             'finding':'原矩形虚化与石面清晰度断层已消除，石板灰缝、树叶与灯笼轮廓连续；本处未见新增直线色带或裁片四边错接。'})
changed=[];reused=[]
for q in s['internalQAItems']:
    if 'reused' in q['status']:
        q.update({'independentFinalQA':'passed_reused_hash_and_exact_current_pixels',
             'reviewMethodThisAudit':'Existing passing visual evidence reused after SHA256 and exact v3 candidate-crop verification.',
             'reviewedThisAudit':False})
        reused.append(q)
    else:
        q.update({'independentFinalQA':'passed_changed_pixels_viewed_unchanged_pixels_reused',
             'reviewMethodThisAudit':'All changed pixels viewed in original-resolution context; unchanged portions reuse existing passed crop evidence after exact pixel checks.',
             'reviewedThisAudit':True,'viewedVia':[context,focus], 'reviewedAtUtc':now})
        changed.append(q)
assert len(changed)==9 and len(reused)==40
for i,q in enumerate(s['perimeterQAItems']):
    q.update({'independentFinalQA':'local_visual_passed','reviewedThisAudit':True,'reviewedAtUtc':now,
              'viewedVia':(O/('large-repair-four-perimeters-100pct.png' if i<4 else 'micro-gap-four-perimeters-100pct.png')).as_posix()})
for q in s['externalBoundarySegments']:
    if q['side']=='top' and q['segment']==4:
        q.update({'independentFinalQA':'not_passed_gold_rib_detail_pending','reviewedThisAudit':True,
                  'finding':'上邻当前哈希已核实；前185行与v2完全相同。原北缝金色细棱宽度／横向台阶仍保留。'})
    elif q['side']=='right' and q['segment']<=2:
        q.update({'independentFinalQA':'local_visual_passed','reviewedThisAudit':True,
                  'finding':'当前r05_c12-sol-v1对接的花叶、朱柱、石墙与铺地轮廓连续，无阻塞性断点。'})
    else:
        q.update({'independentFinalQA':'passed_reused_hash_bound_exact_current_boundary_pixels','reviewedThisAudit':False,
                  'finding':'本条当前v3与实际邻图的原像素拼接裁片匹配旧通过证据，复用，未重复实看。'})
s['internalQA']={'status':'passed16core24seam9cross','coreCount':16,'seamCount':24,'crossCount':9,
     'hashBoundInspectionCropsVerified':49,'unchangedPassingCropsReused':40,'changedInspectionCropsReviewed':9,
     'repairPerimeterCropsActuallyViewed':8,'oldFocusJunctionResolved':True,
     'scope':'Native assembled 4096 candidate internal artwork only; external gold-rib detail prevents full external acceptance.'}
s['externalQA']={
 'north':{'neighbor':'r04_c11','file':next(x['neighbor'] for x in s['externalBoundarySegments'] if x['side']=='top'),
    'sha256':next(x['neighborSha256'] for x in s['externalBoundarySegments'] if x['side']=='top'),
    'segments1to3':'passed_reused_hash_bound_exact_current_pixels','segment4':'not_passed_gold_rib_detail_pending',
    'entire4096EdgeAccepted':False},
 'east':{'neighbor':'r05_c12','file':next(x['neighbor'] for x in s['externalBoundarySegments'] if x['side']=='right'),
    'sha256':next(x['neighborSha256'] for x in s['externalBoundarySegments'] if x['side']=='right'),
    'segments1to2':'local_visual_passed_this_audit','segments3to4':'passed_reused_hash_bound_exact_current_pixels',
    'entire4096EdgeAcceptedLocally':True},
 'west':{'neighbor':'r05_c10','status':'pending_missing_complete_neighbor','entire4096EdgeAccepted':False},
 'south':{'neighbor':'r06_c11','status':'pending_missing_complete_neighbor','entire4096EdgeAccepted':False},
 'northeastFourway':{'worldPoint':[45056,16384],'status':'center_contours_continuous; north_gold_rib_detail_remains_pending',
    'evidence':(O/'northeast-neighbor-fourway-100pct.png').as_posix(),'formalAccepted':False}}
s['resolvedPriorIssues']=[
 {'id':'v2-p01_04-left-focus-boundary','status':'resolved_in_bound_v3','tileLocalBoundaryX':3072,
  'evidence':[context,focus],'finding':'灯笼左侧栏柱窄缝及铺地细节现可连续，不再沿原核心左边形成突兀虚化直线。'},
 {'id':'v2-p01_04-bottom-focus-boundary','status':'resolved_in_bound_v3','tileLocalBoundaryY':1024,
  'evidence':[context,focus],'finding':'原下侧清晰度切换已消除，阶面、石缝和阴影跨原核心下边延续。'}]
s['openIssues']=[{'id':'r05_c11_upper_gold_rib_continuity','status':'not_passed_external_detail_deferred',
 'worldAffectedBox':[44032,16352,45056,16448],'tileLocalArea':[3072,0,4096,64],
 'finding':'北接第4段金色细棱仍有小幅粗细／横向台阶；这处未通过，不因内部问题修好而升级。',
 'evidence':[q['file'] for q in s['visualEvidence'] if q['id']=='external-top-4-100pct']}]
unique={x['file']:x['sha256'] for x in s['inputs']};changes=[]
for f,h in unique.items():
    hh=sha(f) if Path(f).exists() else None
    if hh!=h:changes.append({'file':f,'frozenSha256':h,'currentSha256':hh})
s['sourceRecheck']={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'inputCount':len(unique),
   'unchangedCount':len(unique)-len(changes),'changes':changes,'frozenInputsUnchanged':not changes,
   'policy':'This closeout binds v3 only. Later production changes are recorded without following newer candidates.'}
s.update({'status':'frozen_v3_closeout_complete_internal_passed_external_detail_pending','completedAtUtc':now,
          'formalAccepted':False,'batchStoppedAfterThisTile':True,'newCandidateFollowedAfterV3':False})
write(O/'summary.json',s)
lines=['# r05_c11 v3 独立检查收尾','',
 '本张内部检查通过，北边灯笼金棱仍待修，正式验收未通过。该结论仅绑定下列v3哈希；本批完成后停止追查新版本。','',
 f"当前核实的4096×4096图：[r05_c11-localfinish-v3-20261016.png]({s['candidate']['file']})。",'',
 f"SHA256：`{s['candidate']['sha256']}`。",'',
 'v3相对v2的差异框为图块局部 `[2944,185,3968,1280]`，世界框 `[43904,16569,44928,17664]`。差异框外像素完全相同，前185行亦相同。16个1254原生核心源加2处原生修补裁片，按记录原尺寸摆放可逐像素重建当前4096图；无缩放、羽化或程序绘制细节。实际生图型号未返回。','',
 '49份内部检查裁片均已核实文件哈希且与当前v3裁切像素完全一致，分别覆盖16核心、24缝、9交点。40项未变的通过证据直接复用，9项变化的实际像素范围及8处修补四边已原尺寸查看，其余未变部分复用已有检查。','',
 '原 x3072／y1024 的矩形清晰度边界已消除：灯笼左侧栏柱旁窄铺地、阶面灰缝和阴影恢复连续，两处修补的四边及交汇未见新增断点或直线材质框。旧v2虚化问题不再列为当前v3待修。','',
 '| 范围 | 当前QA |','|---|---|',
 '| 内部16核心、24缝、9交点 | 通过；绑定49份当前像素证据 |',
 '| 北边 r04_c11，第1—3段 | 当前邻图hash与裁片像素一致，复用通过 |',
 '| 北边第4段 | 未通过；灯笼金棱粗细和横向小台阶仍开放 |',
 '| 东边 r05_c12-sol-v1，4段共4096 | 第1—2段本次实看通过，第3—4段复用hash绑定通过 |',
 '| 西边 r05_c10 | 缺完整邻图，待外接验收 |',
 '| 南边 r06_c11 | 缺完整邻图，待外接验收 |',
 '| 东北四邻交点 | 中心花叶／朱柱轮廓连续；左侧北缝金棱细节同样待修 |','',
 f"- [v3变化区及四边原尺寸图]({context})",
 f"- [原x3072／y1024交点原尺寸图]({focus})",
 f"- [北边第4段金棱证据]({next(q['file'] for q in s['externalBoundarySegments'] if q['side']=='top' and q['segment']==4)})",
 f"- [完整源图hash、逐条内部／外接QA与输入复核]({(O/'summary.json').as_posix()})",'',
 f"收尾复核本批 {len(unique)} 项唯一输入，{len(unique)-len(changes)} 项哈希未变，{len(changes)} 项变化。原生产源、选源账本和Git均未修改；本审查零生图、零AI修图。"]
(O/'review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
missing=[x for x in re.findall(r'\]\((D:/[^)]+)\)',(O/'review.md').read_text(encoding='utf-8')) if not Path(x).exists()]
assert not missing,missing
print(json.dumps({'status':s['status'],'candidate':s['candidate'],'internalQA':s['internalQA'],
                  'sourceRecheck':s['sourceRecheck'],'report':(O/'review.md').as_posix()},ensure_ascii=False))
