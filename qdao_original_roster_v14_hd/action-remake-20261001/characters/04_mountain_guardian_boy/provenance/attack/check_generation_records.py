from pathlib import Path
from PIL import Image
from datetime import datetime, timezone
import json, hashlib
ROOT=Path(__file__).resolve().parents[2]
D=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for p in sorted(D.glob('*.png')):
    stem=p.stem
    subp=D/(stem+'.submission.json')
    recp=D/(stem+'.receipt.json')
    if not subp.exists() or not recp.exists(): continue
    sub=json.loads(subp.read_text(encoding='utf-8-sig'))
    rec=json.loads(recp.read_text(encoding='utf-8-sig'))
    gp=D/(stem+'.generation.json')
    prior=json.loads(gp.read_text(encoding='utf-8-sig')) if gp.exists() else {}
    refs=[]
    for value in sub['submittedParameters']['referenced_image_paths']:
        ref=Path(value)
        refs.append({'path':value,'sha256':sha(ref) if ref.exists() else None,'available':ref.exists(),'purpose':'实际用途见完整 prompt 对输入序号的描述'})
    with Image.open(p) as im:
        a=im.getchannel('A') if im.mode=='RGBA' else None
        native={'width':im.width,'height':im.height,'format':im.format,'mode':im.mode,'alphaExtrema':list(a.getextrema()) if a else None,'alpha128Bbox':list(a.point(lambda v:255 if v>=128 else 0).getbbox()) if a else None}
    exports=[]
    for ep in (ROOT/'frames'/'attack').glob('*/*.generation.json'):
        exported=json.loads(ep.read_text(encoding='utf-8-sig'))
        if exported.get('nativeSource',{}).get('path')=='provenance/attack/'+p.name:
            exports.append({'record':ep.relative_to(ROOT).as_posix(),'file':exported['file'],'sha256':exported['sha256'],'review':exported['review']})
    record={**prior,'schemaVersion':1,'character':'04_mountain_guardian_boy','action':'attack','direction':sub['direction'],'frame':sub['frame'],'file':p.name,'sha256':sha(p),**native,'generatedAt':None,'generationTimeEvidence':{'startedAt':sub.get('startedAt',sub.get('attemptedAt')),'completedAt':rec.get('completedAt'),'note':'调用边界，非工具返回精确出图时刻'},'tool':'image_gen.imagegen','route':'builtin','configSnapshot':sub.get('configSnapshot',sub.get('configTarget')),'submittedParameters':{'model':None,'quality':None,'transparent_background':True,'prompt':stem+'.prompt.txt','referenced_image_paths':sub['submittedParameters']['referenced_image_paths']},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理；工具未披露型号/质量，无型号和质量选择器；配置目标不是实际版本证明。','references':refs,'evidence':{'submission':subp.name,'receipt':recp.name,'prompt':stem+'.prompt.txt'},'exports':exports}
    if 'review' not in record: record['review']={'status':exports[0]['review']['status'] if exports else 'candidate_pending_visual','sequencePassed':False}
    gp.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    rows.append({'file':p.name,'sha256':record['sha256'],'exports':len(exports)})
(D/'native-generation-index.json').write_text(json.dumps({'checkedAt':datetime.now(timezone.utc).isoformat(),'records':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'records':len(rows),'exportsLinked':sum(x['exports'] for x in rows)}))

