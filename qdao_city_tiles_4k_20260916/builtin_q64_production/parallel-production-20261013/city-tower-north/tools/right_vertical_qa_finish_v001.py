import json
from pathlib import Path
from datetime import datetime, timezone
from right_vertical_qa_v001 import BASE, M, sha, save_group

save_group(2, [
    {'status':'local-pass','observation':'蓝瓦筒轮廓与高光、斜红檐和下方红柱跨缝连续，未见结构断边。','defects':[]},
    {'status':'local-pass','observation':'红柱、金脊和蓝瓦跨 x=192 连续；此结论仅限该纵缝，不豁免 p23 其他边的既有问题。','defects':[]},
    {'status':'needs-repair','observation':'顶部约 50px 高的蓝瓦在 x=192 突然竖切为红色檐梁，跨缝屋瓦/檐梁轮廓不能连续。其余较低段金脊和红柱连接可读。',
     'defects':[{'id':'r03c14-v-p32-p33-top-roof-cut','kind':'structural-material-boundary-discontinuity',
                 'bboxSeamPixels':[180,0,240,64],
                 'description':'左侧蓝瓦端头在拼缝处被竖直截断，右侧同一高度已经是红色檐梁；估计约 50px 轮廓相位差。',
                 'contextEvidence':{'file':str(BASE/'qa/right-r03c14-p32-p33-top-context-100pct-v001.png'),'sha256':sha(BASE/'qa/right-r03c14-p32-p33-top-context-100pct-v001.png'),'cropTilePixels':[1664,1792,2432,2304],'resized':False},
                 'adjacentCorner':['p22','p23','p32','p33'],
                 'action':'Reported to root for conflict/previous-attempt check before any generation. p23 already has two repairs; no blind retry.',
                 'generationStarted':False}]},
    {'status':'local-pass','observation':'蓝瓦筒、斜红梁和其下方红柱边在拼缝连续；仅该纵向边局部通过，p43 的其他残留保持未过。','defects':[]},
])
save_group(3, [
    {'status':'local-pass','observation':'白石柱花苞、方座、竖柱及后方石地线跨缝连续。','defects':[]},
    {'status':'local-pass','observation':'石柱/灌木/路缘和下部石地接缝连续，叶轮廓没有沿拼缝被切断。','defects':[]},
    {'status':'local-pass','observation':'上层石地灰缝、平台侧墙及下方石地跨缝连续，无明显错层。','defects':[]},
    {'status':'local-pass','observation':'石地块的斜向灰缝、树影和下部灌木跨缝连续。','defects':[]},
])
group_files = [BASE/f'qa/right-r03c14-vertical-group{i}-v001.json' for i in (1,2,3)]
groups = [json.loads(p.read_text(encoding='utf-8')) for p in group_files]
summary = {
    'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
    'reviewer':'tower_right','tile':'r03_c14','candidate':M['artifacts'][0],
    'selection':M['selection'],'scope':'12 vertical internal seams only; each actual 384x1024 crop viewed at original pixels.',
    'groupReports':[{'file':str(p),'sha256':sha(p)} for p in group_files],
    'reviewedVerticalCount':12,'localPassCount':11,'needsRepairCount':1,
    'needsRepair':['vertical-p32-p33'],
    'defects':[d for g in groups for r in g['results'] for d in r.get('defects',[])],
    'horizontalSeams':'Not reviewed by this agent; delegated to tower_qa.',
    'externalSeams':'Not in this review scope.',
    'formalAcceptedCount':0,
    'formalStatus':'Candidate remains unaccepted; local seam passes are not full tile approval.',
    'newImagesGenerated':0,'sourceImagesModified':False,
    'existingTwoRepairPoints':['p23','p43'],
    'nextAction':'Root to cross-check p32-p33 roof-cut with adjacent p23 repair history before any new native AI repair.'
}
out=BASE/'qa/right-r03c14-vertical-summary-v001.json'
with out.open('x',encoding='utf-8') as stream:
    json.dump(summary,stream,ensure_ascii=False,indent=2)
    stream.write('\n')
print(json.dumps({'file':str(out),'sha256':sha(out),'reviewed':12,'localPass':11,'needsRepair':1,'formalAcceptedCount':0},ensure_ascii=False))
