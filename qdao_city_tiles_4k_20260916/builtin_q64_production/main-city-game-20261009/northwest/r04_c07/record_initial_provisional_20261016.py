from pathlib import Path
import sys,json
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent));import production_v2 as p
items=[('s04_02','s04_02_native01',[[150,990,300,1024],[660,990,760,1024]],'Two south-adjacent paving joints have short doglegs. Overall flat inlay footprint and healthy northern/side geometry usable. Southern 180 core rows excluded from guide anchors.'),('s04_03','s04_03_native01',[[450,980,1024,1024]],'South paving-joint phases differ from actual approved southern neighbor. Vertical inlay X positions and cloud footprint stable; north and most side geometry usable. Southern 180 core rows excluded from guide anchors.')]
ex={}
for pid,identifier,boxes,note in items:
 D=T/'qa/source-review'/identifier;m=p.read(D/'manifest.json')
 review={'source':m['source'],'reviewer':'/root/resume_r08_audit_20261016','actuallyViewed':True,'status':'selected_with_local_issue','cropReviews':[dict(file=c['file'],sha256=c['sha256'],status='needs_repair',actuallyViewed=True,finding=note) for c in m['crops']],'issueCoreLTRB':boxes,'finding':note,'healthyAnchorCoreLTRB':[0,0,1024,844],'parentAuthorization':'2026-10-16 parent explicitly authorizes provisional selection only for non-propagating fixed-south localized joints; this is not a passed review.','fullTileInternalQAPassed':False,'formalAccepted':False}
 f=D/'provisional-review.json';p.write_json(f,review)
 print(p.record_selection(T.name,pid,identifier,note,str(f)))
 ex[pid]={'identifier':identifier,'trustedAnchorCoreLTRB':[0,0,1024,844],'status':'selected_with_local_issue','review':str(f)}
p.write_json(T/'provisional-sources.json',ex)

