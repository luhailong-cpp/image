from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from collections import Counter
import numpy as np
from PIL import Image

R=Path(__file__).resolve().parents[1]
O=R/'production-audit/cleanup-proposal.json'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()
cache={}
def info(p):
    p=Path(p).resolve()
    if str(p) not in cache:
        cache[str(p)]={'file':p.as_posix(),'existsAtSnapshot':p.is_file(),'sha256':sha(p) if p.is_file() else None}
    return dict(cache[str(p)])
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pix(p):return np.array(Image.open(p).convert('RGB'))

fragment=R/'c10-expansion/current/r08_c10-fragment-1254x1139.png'
canvas=R/'c10-expansion/state/canvas.png'
lower=R/'c10-seed/joined-v1/r09_c10.png'
oldfrag=R/'c10-seed/joined-v1/r08_c10-native-fragment-1254x627.png'
coupled=R/'c10-seed/joined-v1/coupled-seed-1254.png'
joined=R/'c10-expansion/r04_c02/joined.png'
f=pix(fragment);cv=pix(canvas);lo=pix(lower);co=pix(coupled);j=pix(joined)
checks={
'currentFragmentExactlyInState':bool(np.array_equal(f,cv[3072:4211,1024:2278])),
'currentFragmentExactlyInJoinedTop1139':bool(np.array_equal(f,j[:1139])),
'joinedLower115ExactlyInRetainedLowerTile':bool(np.array_equal(j[1139:],lo[:115,909:2163])),
'coupledLower627ExactlyInRetainedLowerTile':bool(np.array_equal(co[627:],lo[:627,909:2163])),
'coupledUpper627ExactlyInOldSeedFragment':bool(np.array_equal(co[:627],pix(oldfrag))),
'oldSeedWasSupersededNotAssumedByteDuplicate':True
}
assert all(checks.values()), checks
replc10=[info(fragment),info(lower),info(canvas)]
dj=load(R/'donghai/review.json')
dongsrc={(a['appearance'],a['tile']):Path(a['file']) for a in dj['sources']}
lj=load(R/'lanxian/sources.json')
lanxsrc={(a['city'],a['tile']):Path(a['source']['file']) for a in lj['tiles']}
pj=load(R/'penglai/input-and-qa-index.json')
pengsrc={(a['appearance'],a['tile']):Path(a['source']['file']) for a in pj['tiles']}
c08repl=[R/'c08/final-pair/r08_c08.png',R/'c08/final-pair/r09_c08.png']
c07repl=[R/'c07/tone-candidate-v1/r08_c07.png']
c09repl=[R/'c09/tone-candidate-v1/r08_c09.png']
candidates=[]; protected=[]
def add(p,state,reason,replacements,condition,evidence):
    item=info(p)
    item.update(bytes=p.stat().st_size,status=state,reason=reason,
        replacementCurrentOutputs=[info(a) for a in replacements],
        requiredBeforeAnyDeletion=condition,evidenceTextFiles=[info(a) for a in evidence],
        deletionExecutedByThisProposal=False)
    candidates.append(item)
def keep(p,reason):
    a=info(p);a.update(bytes=p.stat().st_size,reason=reason);protected.append(a)

for p in sorted(R.rglob('*')):
    if not p.is_file() or p.suffix.lower() not in ('.png','.npy','.webp','.jpg','.jpeg'):continue
    rel=p.relative_to(R).as_posix();parts=rel.split('/')
    if rel in ('c10-expansion/current/r08_c10-fragment-1254x1139.png','c10-expansion/state/canvas.png','c10-seed/joined-v1/r09_c10.png'):
        keep(p,'当前唯一局部/工作画布/已配对的 4K 下块；尚未完成整块，不可删。');continue
    if parts[0]=='c10-seed':
        reason='已合入当前局部及下块的原片、加工场或可重建 QA；保留所有逐图来源与审查文字。'
        if p in (oldfrag,coupled):reason='旧 seed 已由更高 1254×1139 当前局部及保留的 r09_c10 取代；旧上片不是当前片的逐像素副本，不再作为唯一在制稿。'
        add(p,'candidate_after_reference_selection',reason,[fragment,lower,canvas],
            ['核对当前文件 SHA 未变化并保留。','当前消费者选用 current/state，不再读取旧 seed 图片；来源文字允许保留历史路径并记 deleted。','保留 c10 尚未完成的事实；不得按正式 4K 成品统计。'],
            [R/'c10-seed/joined-v1/assembly.json',R/'c10-seed/joined-v1/visual-review.json',R/'c10-expansion/completion.json'])
        continue
    if parts[0]=='c10-expansion':
        if parts[1]=='r04_c02':
            add(p,'defer_unique_wip_dependency',
                '该接受局部已合入 current 与 state；但 c10 整块未完成，原片/回接场仍可能是继续制作所需的唯一在制输入，暂不删。',
                [fragment,canvas,lower],['确认后续编辑只需 current/state，且不再需要本文件后方可删；当前建议保留。'],
                [R/'c10-expansion/r04_c02/assembly.json',R/'c10-expansion/completion.json'])
        else:keep(p,'未归类的新 c10 文件；只读快照，不推断可删。')
        continue
    if parts[0]=='donghai':
        appearance=parts[2] if len(parts)>2 else ''
        tile=parts[3] if len(parts)>3 else ''
        replacements=([dongsrc[(appearance,tile)]] if (appearance,tile) in dongsrc else [v for (a,t),v in dongsrc.items() if a==appearance])
        add(p,'candidate_rebuildable_review_image','源图未改；本文件只是已完成审查的原像素 QA 或缩略构图图，不是游戏图。',
            replacements,['保留锁定源图、review.json、来源 manifest 和 QA 生成脚本。','消费方不再展示当前 QA 路径，或显示时按记录重新裁切。'],
            [R/'donghai/review.json',R/'donghai/baseline/source-and-qa-manifest.json'])
        continue
    if parts[0]=='c08':
        if parts[1] in ('adjacent-qa','final-pair') and (p.name in ('r08_c08.png','r09_c08.png') or parts[1]=='adjacent-qa'):
            keep(p,'c08 agent 正在进行 6 图 coupled 接边修复；这些是当前源/候选/审查输入，尚未稳定。');continue
        add(p,'defer_active_c08',
            'c08 较早候选、已合入补丁、回退/加工场或派生 QA 的清理建议；活动工作仍可能读取，尚未确认最终替代。',
            c08repl,['等待 c08 agent 的 coupled 6 图版本稳定并记录全部输出 SHA。','以最终 coupled 输出重新核对替代关系与所有消费者引用；不得仅按目录名删除。'],
            [R/'c08/final-pair/assembly.json',R/'c08/final-pair/manifest.json'])
        continue
    if parts[0] in ('c07','c09'):
        rep=c07repl if parts[0]=='c07' else c09repl
        if p in rep:keep(p,'当前 4K 在制候选，也是 c08 coupled 修复输入；不得删。');continue
        reason='可从保留当前 4K 重建的 QA/缩略图，或候选的加工输入；c08 coupled 工作结束前仅建议。'
        if 'full-native' in rel or 'native2304-probe' in rel:
            reason='尺寸实测拒稿或其导入参考，不进入任何当前 4K；保留返回尺寸/型号未披露的文字记录。'
        add(p,'defer_active_adjacent_dependencies',reason,rep,
            ['coupled 修复停止读取本文件后，再确认它不是唯一所需在制输入。','逐图记录、实测尺寸和拒稿文字保留。'],
            [R/'production-audit/verified-scope.json'])
        continue
    if parts[0] in ('lanxian','penglai'):
        mapping=lanxsrc if parts[0]=='lanxian' else pengsrc
        appearance=parts[1] if len(parts)>1 else ''
        tile=next((x for x in parts if x.startswith('r0') and '_c' in x),'')
        rep=[v for (a,t),v in mapping.items() if a==appearance and (not tile or t==tile)]
        isqa=parts[0]=='penglai' or 'baseline' in parts
        if not isqa:
            keep(p,'岚仙活动修复的原生输入、唯一候选或加工场；状态未由本审查人核定，不列可删。');continue
        add(p,'defer_active_other_city_qa','活动目录的源图派生 QA/缩略图，日后可以重建；只列建议，不影响仍进行中的审查。',
            rep,['由该目录当前负责人确认审查已结束且需要的比较/修复输入已另有当前文件。','保留来源图、审查记录与重建脚本。'],
            [R/('lanxian/sources.json' if parts[0]=='lanxian' else 'penglai/input-and-qa-index.json')])
        continue
    keep(p,'未核实用途；不是清理候选。')

receipt=load(R/'c10-expansion/cleanup-receipt.json')
historical=[]
for row in receipt['deleted']:
    p=Path(row['file'])
    historical.append({'file':p.as_posix(),'sha256BeforeEarlierDeletion':row['sha256'],
        'existsAtSnapshot':p.is_file(),'status':'already_absent_not_a_new_deletion_candidate' if not p.exists() else 'unexpected_reappeared_hold',
        'reason':row['reason'],'replacementCurrentOutputs':replc10,
        'evidenceReceipt':info(R/'c10-expansion/cleanup-receipt.json')})
assert not any(x['existsAtSnapshot'] for x in historical)
res={
'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
'run2Scope':R.as_posix(),'mode':'enumeration_only_no_deletions',
'userPolicy':'2026-09-23 仅保留当前游戏/WIP图、唯一尚未导出的在制稿、必要设计/接入文件与来源文字；无图片备份。',
'warning':'此文件是有限时间只读快照，不是删除脚本。所有列项都必须逐文件复核 SHA、用途、当前替代与消费者；不允许递归广删。',
'deletionsExecutedByThisProposal':0,
'protectedTextPolicy':'所有 JSON/TXT/MD/脚本，包括逐图型号质量实际未披露记录、请求、来源 SHA、退稿与 QA 文字均保留；外部设计主图/风格参考不在本轮清理范围。',
'activeWorkHolds':['c08/adjacent-qa 6 图 coupled 尚未稳定；当前图片及加工输入保护。','lanxian 活动生成/修复候选保护。','本 RUN2 之外的正式源图/设计不列为删除项。'],
'c10PixelCrossChecks':checks,
'counts':dict(Counter(x['status'] for x in candidates)),
'candidateBytes':sum(x['bytes'] for x in candidates),
'candidates':candidates,'protectedCurrentBinaryFiles':protected,
'alreadyDeletedEarlierNotNewCandidates':historical,
'notes':['c10-expansion 4 组拒稿及宿主重复原片已由先前 cleanup-receipt 记录处理，本次未重复删除。','当前像素/模型记录不因清理而增加 formalAccepted 或完整坐标数。','历史文档保留的原图路径是溯源，不应误读成仍需加载的运行引用。']
}
O.write_text(json.dumps(res,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':O.as_posix(),'counts':res['counts'],'protectedBinary':len(protected),'alreadyAbsent':len(historical),'pixelChecks':checks,'deletionsExecuted':0},ensure_ascii=False))

