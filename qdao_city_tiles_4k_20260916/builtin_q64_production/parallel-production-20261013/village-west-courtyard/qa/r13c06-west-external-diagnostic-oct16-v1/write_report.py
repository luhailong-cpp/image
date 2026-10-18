from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

OUT = Path(__file__).resolve().parent
m = json.loads((OUT/'snapshot-manifest.json').read_text(encoding='utf-8'))
observations = [
    {
        'id':'west-external-part01', 'status':'fail', 'segment':1,
        'globalSeamX':20480, 'globalYHalfOpen':[49152,50176],
        'evidenceBox':[20250,49152,20710,50176],
        'finding':'整段中央边界显著。西侧水体更深蓝，细密而锐的白色焦散纹；东侧更浅青，块面更大，白线更宽且更软。水纹轮廓与亮线在x20480直接截断，色阶也呈竖直跳变。',
    },
    {
        'id':'west-external-part02', 'status':'fail', 'segment':2,
        'globalSeamX':20480, 'globalYHalfOpen':[50176,51200],
        'evidenceBox':[20250,50176,20710,51200],
        'finding':'西侧细线水纹与东侧宽线大块水纹持续不匹配；亮线相位未跨界延续。中央竖线仍清楚，部分水色较接近不能消除纹理尺度与相位断裂。',
    },
    {
        'id':'west-external-part03', 'status':'fail', 'segment':3,
        'globalSeamX':20480, 'globalYHalfOpen':[51200,52224],
        'evidenceBox':[20250,51200,20710,52224],
        'finding':'西侧较亮且有密集交叉焦散线，东侧较平整的大水纹块和宽白线。多条波纹在边界被垂直裁断，整段仍可辨硬接缝。',
    },
    {
        'id':'west-external-part04', 'status':'fail', 'segment':4,
        'globalSeamX':20480, 'globalYHalfOpen':[52224,53248],
        'evidenceBox':[20250,52224,20710,53248],
        'finding':'上部仍是同样的水纹尺度和亮线相位跳变。下部泡沫与石岸处，右侧宽白泡沫接到左侧较细的白线/水面；最下方岩石面明暗和棱线在中央呈硬切。',
        'localIssueEnclosingBoxes':[
            {'globalBox':[20448,52928,20540,53120], 'kind':'泡沫宽度、走向和相位不连续',
             'rangeMeaning':'人工视觉圈定的保守包围范围，不是逐像素缺陷分割'},
            {'globalBox':[20448,53072,20512,53248], 'kind':'礁石面、色阶与棱线在接缝处硬截',
             'rangeMeaning':'人工视觉圈定的保守包围范围，不是逐像素缺陷分割'},
        ],
    },
]
detail=OUT/'detail-part04-y52864-53248-100pct.png'
detail_record={'path':detail.as_posix(),'sha256':hashlib.sha256(detail.read_bytes()).hexdigest(),
               'size':[460,384], 'source':'contact-part04-y52224-53248-100pct.png',
               'cropBox':[0,640,460,1024], 'globalBox':[20250,52864,20710,53248],
               'operation':'integer crop only', 'actuallyViewed':True}
report={
    'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
    'status':'fail-diagnostic-snapshot-only','formalAccepted':False,'stableGenerationAnchor':False,
    'task':'r13_c05 east core / r13_c06 west core actual external join diagnostic',
    'snapshotStartedAtUtc':m['snapshotStartedAtUtc'],'snapshotFinishedAtUtc':m['snapshotFinishedAtUtc'],
    'globalSeam':m['globalSeam'],'boxConvention':m['boxConvention'],
    'inputIdentities':m['inputs'],
    'mechanicalVerification':{
        'expectedWestAssemblyMatches':True,'expectedWestCandidateMatches':True,'expectedEastContextMatches':True,
        'westSourceCount':16,'westSourceHashesMatching':16,'candidateContextCoreEqualityBothSides':True,
        'inputHashesUnchangedDuringSnapshot':True,
        'visualPassInferredFromHashes':False,
    },
    'visualInspection':{
        'tool':'tools.view_image','detail':'original','actuallyViewedContactSegments':4,
        'contactSegmentsPassed':0,'contactSegmentsFailed':4,'additionalNativeDetailViewed':detail_record,
        'observations':observations,
        'conclusion':'x20480、y49152..53248的西外接缝未通过。四段均存在可见硬接；南端附加泡沫/岩石问题。不能作为稳定生成锚传播。',
    },
    'scopeLimitations':[
        '只读诊断已有候选，未生图、未修图、未改原owner文件、未操作Git。',
        '16源齐与哈希匹配仅验证来源一致，不代表r13_c05内部接缝或外接通过。',
        '未检查或批准r13_c05完整内部接缝。当前报告不赋予任何图块正式验收状态。',
        '四段图每边各230像素，准确表示实际相邻core接触；无缩放、混合、着色或美化。',
        '最南部r13_c06正在由root修订；本报告仅绑定上述输入哈希及快照时刻。变动区域不得自动复用这次诊断，更新后重做对应原像素接触检查。',
    ],
    'qaOutputs':m['outputs'],
    'recommendedNextStep':'先由协调者决定哪一侧可成为稳定边缘；在新西邻内部/外接未通过前，仅保留此诊断并继续其他独立工作。后续如两侧候选变动，重查受影响的外接段。',
}
for filename, content in [('visual-diagnostic.json',json.dumps(report,ensure_ascii=False,indent=2)+'\n')]:
    p=OUT/filename
    assert not p.exists(),str(p)
    p.write_text(content,encoding='utf-8')

lines=[
    'r13_c05 → r13_c06 西外接原像素诊断',
    '结论：未通过（4/4段可见硬接）；仅候选快照诊断，不是正式验收，不得作为稳定生成锚。',
    f"快照UTC：{m['snapshotStartedAtUtc']} 至 {m['snapshotFinishedAtUtc']}",
    '全局接缝：x=20480；y=[49152,53248)。接触图范围x=[20250,20710)，中央x=230。',
    '裁取：r13_c05真实4096 core右侧230列 + r13_c06 context中真实4096 core左侧230列；四张460×1024；纯整数裁切/并排。',
    '机械核实：指定三个哈希吻合；两侧candidate均4096×4096，context均4326×4326；candidate等于context[115:4211,115:4211]；西邻16源实际哈希全匹配。',
    '上述机械核实不等于视觉通过。已实际使用view_image(detail=original)查看四段及南端460×384细节。',
    '',
]
for o in observations:
    lines.append(f"第{o['segment']}段 y={o['globalYHalfOpen']}：未通过。{o['finding']}")
lines += [
    '南端具体包围范围（半开整数坐标，人工保守圈定，并非逐像素分割）：',
    '泡沫：[20448,52928,20540,53120)；礁石面：[20448,53072,20512,53248)。',
    '',
    '输入哈希：',
]
for k,v in m['inputs'].items():
    lines += [k+': '+v['path'],'SHA256 '+v['sha256']]
lines += ['',
    'r13_c05 assembly快照状态：'+m['westStatusAtSnapshot'],
    'r13_c06 assembly快照状态：'+m['eastStatusAtSnapshot'],
    'root正在修订r13_c06最南部。此报告只绑定快照和输入哈希；未来变动区域须重新检查，不自动复用本诊断。',
    '没有生图/AI修图，没有改动原owner目录，没有操作共享Git。',
    '全部精确裁取框、输出哈希、16源核实记录见snapshot-manifest.json；结构化视觉结论见visual-diagnostic.json。',
]
p=OUT/'REPORT.txt'
assert not p.exists(),str(p)
p.write_text('\n'.join(lines)+'\n',encoding='utf-8')
print(json.dumps({'report':p.as_posix(),'status':report['status'],'failedSegments':4},ensure_ascii=False))
