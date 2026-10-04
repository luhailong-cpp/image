"""Record this explicitly scoped foot-yaw review; does not modify frames or sidecars."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageSequence
import hashlib,json,sys
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
CHANGED={1,2,3,11,12,13,14,15,16}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
records=[]
for d in ['N','SE']:
    for n in range(1,17):
        p=ROOT/'frames/run'/d/f'frame_{n:02}.png';j=load(p.with_suffix('.generation.json'))
        assert j['sha256']==sha(p)
        with Image.open(p) as im: assert im.size==(1024,1024) and im.mode=='RGBA'
        changed=d=='SE' and n in CHANGED
        if d=='N':
            note='脚与鞋底的长轴整体沿背向运动的纵深方向；未见明确向两侧撇开的脚掌。保留本帧，不因腿间距或金色鞋面装饰判错。'
        elif n in (1,2,3):
            note='杖侧前靴由朝镜头/屏下偏左纠为鞋跟上左→鞋尖右下；相邻踝部自然衔接，未把两膝或腿距向中间压缩。承重段继续由根窗口动态判断。'
        elif n in (11,12,13):
            note='屏左抬起的杖侧靴原向左偏；局部调整脚掌yaw至右下行进方向。另一侧支撑/后蹬靴及膝位保留。'
        elif n in (14,15,16):
            note='杖侧前摆靴的跟趾轴改向右下，保留抬脚与鞋底露出，衔接回01。未旋转躯干或整帧。'
        else:
            note='原靴在前摆/回收时的跟趾轴与小腿投影相容，未见需要单独纠正的向两侧外撇；本轮保留。'
        rec={'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'decision':'targeted_foot_yaw_replaced' if changed else 'retained_after_visual_review','observation':note,'reviewScope':'static_image_and_contact_sheet_foot_direction_only','dynamicStatus':'pending_parent_grounded720_review','clientStatus':'not_integrated'}
        if changed:
            native=ROOT/j['nativeSource']['path'];assert native.exists() and sha(native)==j['nativeSource']['sha256']
            with Image.open(native) as im: assert min(im.size)>=1024 and im.mode=='RGBA'
            assert len(j['submittedParameters']['referenced_image_paths'])==5
            assert all(j[k] is None for k in ('actualModel','actualQuality'))
            rec.update(nativeSource=j['nativeSource'],oldFrameSha256=j['replacement']['oldFrameSha256'],retiredRecord=j['replacement']['retiredRecord'],submission=j['evidence']['submission'],receipt=j['evidence']['receipt'])
        records.append(rec)
previews=[]
for d in ['N','SE']:
    for variant in ['grounded720','grounded_slow']:
        p=ROOT/'preview'/f'run_{d}_{variant}.gif'
        j=load(p.with_name(p.name+'.generation.json'))
        with Image.open(p) as im: durations=[f.info.get('duration') for f in ImageSequence.Iterator(im)]
        assert durations==j['operation']['durationsMs']
        assert sum(durations)==(720 if variant=='grounded720' else 2880)
        assert all(sha(ROOT/s['path'])==s['sha256'] for s in j['derivedFrom'])
        previews.append({'file':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'durationMs':sum(durations),'durationsMs':durations,'currentSourcesMatch':True})
report={'reviewedAt':datetime.now(timezone.utc).isoformat(),'character':ROOT.name,'scope':'N/SE foot yaw review after latest user correction','criteria':'按自身足跟到趾尖方向与小腿自然对齐判断；07仅作视觉对照，不是整套或某方向已通过金标。保留不外撇帧，不缩小两腿间距代替修脚向。','changedSEFrames':sorted(CHANGED),'retainedNFrames':list(range(1,17)),'retainedSEFrames':[n for n in range(1,17) if n not in CHANGED],'rejectedExperiment':{'path':'provenance/run/N_02_toeaxis_20261003_01.png','sha256':sha(OUT/'N_02_toeaxis_20261003_01.png'),'decision':'not_exported','reason':'返回几乎未改善足向；原帧未见明确外撇，保留原图。早先以鞋面金色装饰判断朝向不充分，撤回必错判断。'},'modelEvidence':'目标GPT Image 2.5 Sunburst/max，内置入口无model/quality选择器；实际提交及返回未确认，均null。','nativeRetention':'本轮10次生成原生均保留，9张SE采用，1张N实验未采用；本代理不清理。','frames':records,'previews':previews,'notDoneHere':['未修改全局manifest/preview首页或统一sidecar节奏字段','未把静态脚向检查写成动态正常倍速或客户端通过']}
(OUT/'N_SE_toeaxis_review_20261003.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
lines=['# 山岳守卫 N / SE 脚向复核与定点修正','',f"记录时间：{report['reviewedAt']}",'',report['criteria'],'','本轮完成SE第01、02、03、11、12、13、14、15、16帧局部AI脚向修正；N16帧、SE04–10保留。全部新图实际查看后才register替换；每次实际附上当前目标、07对应正式帧、04画像、04对应idle与designs画法共5张参考。','', 'N02有一次试验返回，但没有可确认的脚向改善，未替换正式帧。不能以鞋面装饰外观单独判定鞋头朝向；原N脚掌轴线未见明显两侧外撇，故保留。','', 'SE修正集中在杖侧前靴：原鞋尖偏向屏下/左或正对镜头，现脚跟上左→鞋尖右下，朝向与SE移动相容。上身、膝位和腿间距保留，未通过挤拢双腿掩盖脚向。01–03的承重及14–16→01循环需按新预览动态复核。','', 'N/SE连图和全部试播GIF已重建。grounded720使用[40,70,60,40,40,30,30,50]×2=720ms，grounded_slow=2880ms；实际GIF时长与新正式来源SHA已核对。浏览器动态观感由根窗口继续，本文件不宣称客户端接入。','', '9张替换正式PNG均1024 RGBA、原生1254 RGBA。内置模型和质量实测未确认；目标为GPT Image 2.5 Sunburst/max。原生、未采用N测试稿、逐图文字证据全部保留。','', '| 槽位 | 新正式SHA256 | 原生SHA256 |','| --- | --- | --- |']
for r in records:
    if r['decision']=='targeted_foot_yaw_replaced':lines.append(f"| {r['file']} | `{r['sha256']}` | `{r['nativeSource']['sha256']}` |")
lines += ['', '[逐帧保留/替换与来源JSON](N_SE_toeaxis_review_20261003.json)','']
(OUT/'N_SE_TOEAXIS_REVIEW_20261003.md').write_text('\n'.join(lines),encoding='utf-8')
print(json.dumps({'changed':len(CHANGED),'retained':32-len(CHANGED),'previews':previews,'records':str(OUT/'N_SE_toeaxis_review_20261003.json')},ensure_ascii=False,indent=2))
