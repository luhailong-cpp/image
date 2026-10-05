from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
OUT=Path(__file__).resolve().parent
manifest=json.loads((OUT/'contact-manifest.json').read_text(encoding='utf-8'))
metrics=json.loads((OUT/'seam-metrics.json').read_text(encoding='utf-8'))
by_hash={s['patch']:s['sha256'] for s in manifest['derivedFrom']}
notes={
'V_r01_x1024':('minor_difference','米黄石面在 x=1024 处有轻微直线纹理/色阶界，主要 y=0:530；穿越的金边连续，未见明显几何断口。'),
'V_r01_x2048':('defect','x=2048 的纵向色差贯穿石面与台阶侧面；y约650:940的棕色侧面最易见。道路轮廓总体接续。'),
'V_r01_x3072':('minor_difference','金色面有低对比纵向色阶界；穿过此缝的斜边总体接续，未见大幅位置差。'),
'V_r02_x1024':('defect','台阶侧面和黄色石面出现同一条纵向明暗切线，约 y=1130:1630；主要轮廓连续。'),
'V_r02_x2048':('minor_difference','黄色石面和三条横斜金边的色调在缝两侧变化；约 y=1380:1740可见细小边缘厚度变化，无大块结构缺失。'),
'V_r02_x3072':('defect','灰色石面右侧整体偏暗。金边/白色倒角在 y约1030:1045、1470:1490、1840:1865处有短尖楔或阶梯形错位。'),
'V_r03_x1024':('minor_difference','黄色石面有轻微纵向色阶变化；经过的石缝和边框连续，未见明显几何缺口。'),
'V_r03_x2048':('defect','灰色板面在 x=2048 处有纵向色阶/材质切线；上方横斜金边 y约2290:2330有细小接头。'),
'V_r03_x3072':('defect','灰色石面明显纵向色差，延续至黄色边框和树叶；y约2730:3072叶片区域存在硬切色界，未见大树结构丢失。'),
'V_r04_x1024':('minor_difference','黄色石面有轻微纵向明暗界；三条穿越的板缝/边框基本连续。'),
'V_r04_x2048':('defect','黄石和绿叶有明显纵向色界。y约3700:4096叶片的明暗、局部形状和边缘不能在中心缝自然衔接，最明显约3800:4050。'),
'V_r04_x3072':('defect','纵向界贯穿叶片/树干；y约3170:3490及3750:4096叶簇出现色阶硬切，局部叶缘接头可见；树干主体仍连续。'),
'H_c01_y1024':('minor_difference','黄色地面纹理/色温在 y=1024 处有低对比水平界；此段中心缝未穿过重大结构。'),
'H_c01_y2048':('minor_difference','灰石与黄石有轻微水平色阶变化；边框连续，未见先前灰面亮带在此缝形成大断口。'),
'H_c01_y3072':('no_obvious_defect','在所查看的原像素条带中未见明显几何断口或醒目的直线色块；不代表外边、整片或客户端验收。'),
'H_c02_y1024':('defect','棕色台阶侧面出现非常清晰的水平亮度切线，尤其 x约1320:1780；投影和石材材质跨缝突变，结构主体仍延续。'),
'H_c02_y2048':('defect','灰石中心出现贯穿的水平色阶界，约 x=1150:2048；无大块结构缺失。'),
'H_c02_y3072':('minor_difference','金色条带有低对比水平色调/边缘厚度变化；白边总体连续，未见大错位。'),
'H_c03_y1024':('minor_difference','金面低对比水平色差；横穿的斜边总体接续，未见显著断缝。'),
'H_c03_y2048':('defect','y=2048 的水平色阶线同时跨过黄色石面与右侧灰石，约 x=2120:2580及2750:3072；斜边轮廓主体连续。'),
'H_c03_y3072':('defect','地面水平色界延续至绿叶，x约2670:3072的树叶出现明显平直明暗/颜色分割；叶片局部高光突变。'),
'H_c04_y1024':('defect','灰石有水平色阶变化；金色斜边的白色高光/暗倒角在 x约3540:3590及3770:3820产生尖楔和短折角。'),
'H_c04_y2048':('defect','灰石水平色差明显，约 x=3072:3510；黄色大边框虽接续，但跨缝有色温/明暗变化。'),
'H_c04_y3072':('defect','水平接缝穿过树冠/树干，x=3072:3650可见色调硬切及叶簇高光的平直分界；右侧黄石也有低对比色差。'),
}
jnotes={
'J_x1024_y1024':('minor_difference','黄石纹理在交点两轴轻微变化；无明显十字形几何断口。'),
'J_x2048_y1024':('defect','台阶侧面/交角附近存在上下、左右色阶变化；石块轮廓主体相接。'),
'J_x3072_y1024':('defect','灰石形成明显竖向色界；交点下方金边/白边有尖楔接头，详见 V_r02_x3072。'),
'J_x1024_y2048':('minor_difference','黄石与板缝整体连续；有轻微两轴色调差，未见大型几何裂口。'),
'J_x2048_y2048':('defect','灰石与金面形成明确水平色阶界；竖向差较弱，斜边主体连续。'),
'J_x3072_y2048':('defect','灰石中心有清晰十字形四象限色/纹理差，不能按无缝通过。'),
'J_x1024_y3072':('no_obvious_defect','金色横条及黄色石面在所看320x320范围未见醒目的交点缺口；不作外邻验收。'),
'J_x2048_y3072':('minor_difference','黄色石面存在轻微十字色阶，边框总体连续。'),
'J_x3072_y3072':('defect','树叶和树干形成明显横纵十字颜色分界，最突出为左下象限亮绿叶与上方深绿叶的水平切口。'),
}
metric_map={v['id']:v for v in metrics['segments']}
entries=[]
for output in manifest['outputs']:
    for sec in output['sections']:
        identifier=sec['id'];status,note=(notes|jnotes)[identifier]
        if identifier.startswith('V_'):
            r=int(identifier[3:5]);c=int(identifier.split('_x')[1])//1024
            patches=[f'r{r:02d}_c{c:02d}',f'r{r:02d}_c{c+1:02d}']
        elif identifier.startswith('H_'):
            c=int(identifier[3:5]);r=int(identifier.split('_y')[1])//1024
            patches=[f'r{r:02d}_c{c:02d}',f'r{r+1:02d}_c{c:02d}']
        else:
            x,y=sec['junctionCoreXY'];c=x//1024;r=y//1024
            patches=[f'r{rr:02d}_c{cc:02d}' for rr in (r,r+1) for cc in (c,c+1)]
        entries.append({**sec,'assessment':status,'observation':note,'contactFile':output['file'],
            'sourceShas':{p:by_hash[p] for p in patches},'viewedAtNativeScale':True,'accepted':False,
            'writerStableConfirmationPending':'r03_c01' in patches,
            'descriptiveMetrics':metric_map.get(identifier)})
changes=[]
for source in manifest['derivedFrom']:
    current=hashlib.sha256(Path(source['file']).read_bytes()).hexdigest()
    if current!=source['sha256']:changes.append({'patch':source['patch'],'snapshotSha256':source['sha256'],'currentSha256':current})
report={'schemaVersion':1,'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'snapshotAtUtc':manifest['createdAtUtc'],
    'tile':'r08_c09','coordinateSystem':'local 4096 core, half-open ranges; global origin (32768,28672)',
    'method':'All 24 internal seam segments, each full 1024 length with 160 native pixels on each side, and all nine 320x320 junctions viewed using view_image detail=original. No resizing or image modification. Additional exact-pixel crops used for local geometry defects.',
    'sourceSnapshot':'contact-manifest.json','sourceChangesSinceSnapshot':changes,
    'internalsViewed':{'seamSegments':24,'junctions':9},'completeTileAccepted':False,
    'externalEdgesReviewed':False,'externalCornersReviewed':False,'clientAccepted':False,'navigationAccepted':False,
    'status':'internal_defects_found','limitations':['r03_c01 was stable and hash-matched throughout capture/review, but writer confirmation remains pending. Its three seam/two junction observations are provisional until confirmed.','Only internal seam strips/junctions reviewed; full patch interiors, outside neighbours and navigation were not reviewed.'],
    'findings':entries,'derivedFrom':manifest['derivedFrom']}
(OUT/'review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# r08_c09 内部缝检查', '',
'结论：当前 core 直接拼接存在多处直线色差、局部金边尖楔和叶片接头，不能标记无缝通过。未修改 native 或 assembly。', '',
f"快照：{manifest['createdAtUtc']}。全部 16 张来源 SHA 与记录 SHA 见 [contact-manifest.json](contact-manifest.json)。检查结束复核：{'所有图片 SHA 仍一致' if not changes else '有来源变化，详见 review.json'}。", '',
'检查方法：查看 24 段完整 1024 像素内部缝（两侧各 160 原像素）及 9 处 320×320 交点；联系图不缩小，使用 original 详情实际查看。所有坐标为 4096 核心内坐标；整城原点为 (32768,28672)。', '',
'r03_c01 的当前 SHA 为 `'+by_hash['r03_c01']+'`；捕获和复核一致，但尚待写入者确认版本停止更新，其 3 条相关缝和 2 处交点暂记观察。', '',
'优先修复：V x=3072 在 y≈1030–1045、1470–1490、1840–1865 的金边尖楔；H y=1024 在 x≈3540–3590、3770–3820 的斜边接头；y=3072 的树叶横向切色，以及 x=2048/3072 的下部树叶纵向切色。定位裁图见 [geometry_findings_1to1.png](geometry_findings_1to1.png)。', '',
'## 逐段观察', '', '| 条目 | 判断 | 观察 |','|---|---|---|']
for entry in entries:
    verdict={'defect':'需修复','minor_difference':'轻微色/材质差','no_obvious_defect':'此范围未见明显缺陷'}[entry['assessment']]
    if entry['writerStableConfirmationPending']:verdict+='（待版本稳定确认）'
    lines.append(f"| [{entry['id']}]({entry['contactFile']}) | {verdict} | {entry['observation']} |")
lines+=['','## 范围限制','','本次没有核验四条外共边、外角、导航约束或客户端接入；没有将整块或任何外邻标为验收。像素跳变统计在 [seam-metrics.json](seam-metrics.json)，仅支持定位，不是自动验收阈值。每个条目的来源 SHA、检查框与联系图位置见 [review.json](review.json)。','']
(OUT/'review.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'review':str(OUT/'review.json'),'segments':24,'junctions':9,'changedSources':changes,'pendingWriterConfirmation':'r03_c01'}))
