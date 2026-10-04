from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, argparse

R=Path(__file__).resolve().parents[1].resolve()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
d=json.loads((R/'delivery-current.json').read_text(encoding='utf-8'))
v=json.loads((R/'validation.json').read_text(encoding='utf-8'))
assert v['status']=='passed' and v['runtimeCount']==196
keep=set(); rows=[]
for group,fs in d['groups'].items():
    for f in fs:
        p=(R/f['file']).resolve();assert p.is_relative_to(R/'runtime') and sha(p)==f['sha256'];keep.add(p);rows.append((group,f))
    sheet=(R/'preview'/(group.replace('/','-')+'-contact.jpg')).resolve()
    m=json.loads(Path(str(sheet)+'.generation.json').read_text(encoding='utf-8'))
    assert m['sha256']==sha(sheet) and [x['sha256'] for x in m['derivedFrom']]==[f['sha256'] for f in fs]
    keep.add(sheet)
keep.add((R/'preview/current-four-actions.jpg').resolve())
proof=R/'preview/final-browser-check.jpg'
if proof.exists():keep.add(proof.resolve())
delete=[]
for p in R.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.png','.jpg','.jpeg','.gif','.webp'}:
        resolved=p.resolve()
        assert resolved.is_relative_to(R) and resolved!=R, str(p)
        if resolved not in keep:
            assert not resolved.is_relative_to(R/'runtime'), str(p)
            delete.append({'file':p.relative_to(R).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size,'reason':'native/candidate/rejected/intermediate review superseded by verified current runtime export'})
report={'status':'applied' if args.apply else 'dry-run','scope':str(R),'verifiedFinalImages':196,'retainedCurrentImageCount':len(keep),'removedImageCount':len(delete),'removedBytes':sum(x['bytes'] for x in delete),'generationTextRecordsRetained':True,'outsideRootUntouched':True,'time':datetime.now(timezone.utc).isoformat(),'files':delete}
if not args.apply:
    write(R/'retention-plan.json',report)
else:
    # Only text snapshots are retained, as required by the user's image-retention policy.
    for name in ['source-selection.json','candidate-inventory.json','run-playback-proposals.json']:
        p=R/name;dest=R/(p.stem+'-historical.json')
        if not dest.exists():dest.write_bytes(p.read_bytes())
    write(R/'source-selection.json',{'status':'current-runtime-production','inventory':'delivery-current.json','basis':'Playback numbering already applied once; historical native source paths remain in per-image generation records.','slots':{group+'/'+str(f['frame']).zfill(2):f['file'] for group,f in rows}})
    write(R/'candidate-inventory.json',{'status':'superseded-by-current-runtime','groups':d['groups'],'currentInventory':'delivery-current.json','historicalInventory':'candidate-inventory-historical.json'})
    write(R/'run-playback-proposals.json',{'status':'reviewed-source-order-already-applied-to-runtime','groups':{},'historicalSourceOrders':'run-playback-proposals-historical.json','doNotApplyAgain':True})
    old=R/'RUN_REVIEW.md';historic=R/'RUN_REVIEW_HISTORICAL.md'
    if not historic.exists():historic.write_bytes(old.read_bytes())
    old.write_text('# 跑步当前复核\n\n本轮八方向128张制作版已完成，当前结果见FINAL_REVIEW.md、manifest.json和runtime/run/。早期问题快照保留在RUN_REVIEW_HISTORICAL.md，不代表当前状态。每方向16×75ms=1200ms；客户端尚未接入。\n',encoding='utf-8')
    for row in delete:
        p=(R/row['file']).resolve()
        assert p.is_relative_to(R) and p not in keep and sha(p)==row['sha256']
        p.unlink()
    # Work previews load removed native drafts; keep the working text, but route old HTML entry points to current preview.
    for p in R.rglob('*.html'):
        if p.parent==R/'preview' and p.name in {'index.html','timing-grounding.html'}:continue
        if p.is_relative_to(R/'tools'):continue
        import os
        target=os.path.relpath(R/'preview/index.html',p.parent).replace('\\','/')
        p.write_text('<!doctype html><meta charset="utf-8"><title>历史检查入口</title><p>本轮已完成；旧过程图已按保留规则清理。</p><a href="'+target+'">打开当前196张成品预览</a>',encoding='utf-8')
    write(R/'retention-report.json',report)
print(json.dumps({k:v for k,v in report.items() if k!='files'},ensure_ascii=False))
