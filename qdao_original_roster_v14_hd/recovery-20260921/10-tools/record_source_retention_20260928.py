"""Record actual authorized image deletions without rewriting historical receipts."""
from pathlib import Path
from datetime import datetime, timezone
import json,hashlib
R=Path(__file__).resolve().parents[1];O=R/'10-delivery-preview/current';C=R/'10-work/cleanup-20260928'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=read(C/'result.json');p=read(C/'plan.json');m=read(O/'manifest.json')
assert r['status']=='deleted-and-verified' and r['deletedFiles']==p['summary']['totalFiles']==787
assert r['planSHA256']==sha(C/'plan.json')
assert all(not Path(x['path']).exists() for x in r['targets'])
assert all(not (R/'10-generation'/row['archive']/'raw.png').exists() for row in m['frames'].values())
record={'character':m['character'],'status':'completed','checkedAt':datetime.now(timezone.utc).isoformat(),'authorization':'用户及AGENTS最新素材保留规则：最终成品和引用安全后删除原图、拒稿、回退和中间图片，保留设计及文字来源。','deletedFiles':r['deletedFiles'],'deletedBytes':r['deletedBytes'],'byKind':p['summary']['byKind'],'scope':'仅本角色10明确列入白名单的图片和由本角色工具回执绑定的宿主原图；未递归删除。','plan':{'file':'../../10-work/cleanup-20260928/plan.json','sha256':sha(C/'plan.json')},'executionResult':{'file':'../../10-work/cleanup-20260928/result.json','sha256':sha(C/'result.json')},'selectedNativeRawImagesRemaining':0,'finalPNGCount':136,'finalAPNGCount':8,'retained':'本目录最终PNG/APNG/逐帧预览、当前身份设计、全部精确提示词/请求/回执/模型质量/尺寸/SHA与选稿审查文字。','historicalRecordMeaning':'历史raw路径和originalPreserved字段陈述生成归档当时的事实；本清理记录说明当前像素原图已按授权删除，不改写历史回执及其SHA。它们不再是可打开的当前文件引用；游戏及预览只依赖最终PNG。','paidAPICalls':0,'clientIntegration':'not_performed'}
(O/'source-retention.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
handoff=R/'10-HANDOFF-20260928.md'
note='\n## 最终清理实绩\n\n已逐文件删除787张图片，共836,224,865字节（约797.5 MiB）：211张原图、167张宿主重复原图、369张工作中间图、40张旧预览图。执行后保护文件校验通过；精确清单和结果见`10-work/cleanup-20260928/`。没有剩余待处理原图；未触及其他角色。\n'
assert '## 最终清理实绩' not in handoff.read_text(encoding='utf-8')
with handoff.open('a',encoding='utf-8') as f:f.write(note)
print(json.dumps({'retentionStatus':'completed','deletedFiles':r['deletedFiles'],'deletedBytes':r['deletedBytes']},ensure_ascii=False))
