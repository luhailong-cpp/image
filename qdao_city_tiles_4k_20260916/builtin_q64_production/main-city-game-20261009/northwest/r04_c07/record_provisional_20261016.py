from pathlib import Path
import sys,json
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent));import production_v2 as p
identifier,note,region=sys.argv[1:4];pid=identifier[:6];D=T/'qa/source-review'/identifier;m=p.read(D/'manifest.json')
q=json.loads(region)
v={'source':m['source'],'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'status':'selected_with_local_issue','finding':note,'cropReviews':[dict(file=c['file'],sha256=c['sha256'],name=c['name'],status='needs_repair',actuallyViewed=True,finding=note) for c in m['crops']],'trustedAnchorCoreLTRB':q,'fullTileInternalQAPassed':False,'formalAccepted':False}
f=D/'provisional-review.json';p.write_json(f,v)
print(p.record_selection(T.name,pid,identifier,note,str(f)))
ex=p.read(T/'provisional-sources.json');ex[pid]={'identifier':identifier,'trustedAnchorCoreLTRB':q,'status':'selected_with_local_issue','review':str(f)};p.write_json(T/'provisional-sources.json',ex,replace=True)

