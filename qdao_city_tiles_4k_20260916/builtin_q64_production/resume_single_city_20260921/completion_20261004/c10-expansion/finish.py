from pathlib import Path
import json,hashlib,datetime
from PIL import Image
R=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
review={'reviewer':'verify_model','scope':'Actually viewed native1254 and four mechanical joins at original pixels. No full4K or external-edge approval.','localAccepted':False,'formalAccepted':False,'reasons':['4 px and16 px conventional flow left obvious rail kinks.','Moving blend 550 px deeper transferred geometry faults into the lower stone bevel.','24 px displacement extended from known region initially waved the transverse gold bar; removing vertical displacement fixed that bar but left discernible local curvature changes in vertical rails. This is not a clean single-line join.'],'nextAction':'Keep only r04_c02 accepted local fragment. No additional same-input retries.'}
(R/'r03_c02_seed/visual-review.json').write_text(json.dumps(review,indent=2),encoding='utf-8')
entries=[]
for O in sorted(R.glob('r*_c*')):
 if not O.is_dir() or not (O/'native.png.generation.json').exists():continue
 g=json.loads((O/'native.png.generation.json').read_text())
 for ref in g['references']:
  ref['role']='approved rendering style only' if '04-guild.png' in ref['file'] else ('layout reference only; never contributes output pixels' if 'layout-reference' in ref['file'] else 'exact native known pixels and transparent missing region')
 receipt=json.loads((O/'tool-response.json').read_text());g['hostObservedStartedAtUtc']=receipt['hostObservedStartedAtUtc'];g['hostObservedFinishedAtUtc']=receipt['hostObservedFinishedAtUtc']
 (O/'native.png.generation.json').write_text(json.dumps(g,indent=2),encoding='utf-8')
 a=json.loads((O/'assembly.json').read_text());a['generationRecord']=info(O/'native.png.generation.json');a['visualQaPending']=False;a['visualReview']=info(O/'visual-review.json');a['localAccepted']=O.name=='r04_c02'
 (O/'assembly.json').write_text(json.dumps(a,indent=2),encoding='utf-8')
 d=json.loads((O/'joined.png.generation.json').read_text());d['assembly']=info(O/'assembly.json');(O/'joined.png.generation.json').write_text(json.dumps(d,indent=2),encoding='utf-8')
 entries.append({'patch':O.name,'native':info(O/'native.png'),'generation':info(O/'native.png.generation.json'),'request':info(O/'request.json'),'review':info(O/'visual-review.json'),'localAccepted':a['localAccepted'],'newUniquePixelsAccepted':642048 if a['localAccepted'] else 0})
O=R/'current';O.mkdir(exist_ok=True)
Image.open(R/'r04_c02/joined.png').crop((0,0,1254,1139)).save(O/'r08_c10-fragment-1254x1139.png')
fragment={'file':str(O/'r08_c10-fragment-1254x1139.png'),'sha256':sha(O/'r08_c10-fragment-1254x1139.png'),'derivedFrom':[info(R/'r04_c02/joined.png')],'assembly':info(R/'r04_c02/assembly.json'),'operation':'Exact crop of native-dimension joined current fragment; no enlargement.','tileLocalLTRB':[909,2957,2163,4096],'globalLTRB':[37773,31629,39027,32768],'pixels':[1254,1139],'newModelCalls':0,'formalAccepted':False}
(O/'r08_c10-fragment-1254x1139.png.generation.json').write_text(json.dumps(fragment,indent=2),encoding='utf-8')
p=R/'state/provenance.json';pr=json.loads(p.read_text());pr['operations'][0]['assemblySha256']=sha(R/'r04_c02/assembly.json');pr['currentCanvasSha256']=sha(R/'state/canvas.png');pr['currentStandaloneFragment']=fragment;p.write_text(json.dumps(pr,indent=2),encoding='utf-8')
record={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'builtinCalls':5,'actualNativeEach':[1254,1254],'actualModel':None,'actualQuality':None,'calls':entries,'currentFragment':fragment,'newAcceptedNativePixels':642048,'currentKnownFormalPixelsIncludingParentSeed':1428306,'formalTilePixels':16777216,'newComplete4KTiles':0,'formalAccepted':False,'apiCliCalls':0,'blocker':'Native outpainting modifies opaque established contours by tens of pixels. Bounded registration does not reliably yield single continuous bevels; rejected material and geometry errors are not credited.'}
(R/'completion.json').write_text(json.dumps(record,indent=2),encoding='utf-8')
(R/'README.md').write_text('''# c10 原生扩展结果\n\n本轮内置实际生成 5 次，全部返回 1254×1254；没有 API/CLI。模型与质量均未披露，逐图保留配置目标、真实参数空值、请求、时间、SHA 和入口证据。\n\n当前唯一采用局部片：`current/r08_c10-fragment-1254x1139.png`，r08_c10 本块位置 `[909,2957,2163,4096]`，全球位置 `[37773,31629,39027,32768]`。共 1,428,306 原生像素，其中承接父任务种子 786,258，本轮补入 642,048。没有新增完整4096块，不计正式验收。\n\n`r04_c02` 第一版回接穿过横棱发生波浪，已拒；将接续放在大石板内部后，实际看过最终1254全幅，未见新双线/硬色块，该有限局部采用。不能当作外边、整图或所有交点通过。\n\n另外四张均拒用：常规 c01 的115像素下邻上下文无法约束金边；627/627跨界 c01 seed 仍漂移数十像素；去布局图重试吞掉左金边；c02向上扩展也有轮廓漂移，4/16/24像素有界配准及延拓仍留下折弯或新的曲率变化。各目录 visual-review.json 记录真实实看范围，completion.json 汇总五次返回。没有用放大或强行几何扭曲把失败片算成成品。\n\n`state/canvas.png` 是透明缺失区域的原生在制画布，不能作为已完成4K交付。后续先修好已有29个坐标；待入口和保真能力实际改善再扩展 c10。\n''',encoding='utf-8')
print(json.dumps({'record':str(R/'completion.json'),'currentFragment':fragment,'calls':len(entries)}))
