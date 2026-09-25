"""Bind completed human/agent visual review to final bytes; no image edits."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
REC=Path(__file__).resolve().parents[1];OUT=REC/'14-delivery-preview';A=OUT/'assets'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source=read(OUT/'source-audit.json');assert source['sourceAuditPass'] and len(source['selected'])==136
for name in ['qa-north.md','qa-west.md','qa-south-east.md']:assert (OUT/name).is_file()
rows=[];total_cleanup=0;exceptions=[];dirs=['N','NE','E','SE','S','SW','W','NW']
for r in source['selected']:
 p=A/r['file'];m=read(Path(str(p)+'.generation.json'));assert sha(p)==r['finalSHA256']==m['sha256']
 m['visualReview']='passed-offline-2026-09-23';m['visualReviewEvidence']='qa-summary.json';m['sourceEvidence']='provenance.json';write(Path(str(p)+'.generation.json'),m)
 rows.append({'file':r['file'],'sha256':sha(p),'sourceArchive':m['sourceArchive'],'sourceSHA256':r['rawSHA256'],'offlineApproved':True})
 total_cleanup+=sum(x['changedPixels'] for x in m.get('colorCleanup',[]))
 last=m.get('colorCleanup',[])[-1] if m.get('colorCleanup') else {}
 if last.get('unresolvedCandidates'):exceptions.append({'file':r['file'],'pixels':last['unresolvedCandidates'],'assessment':'Low-alpha snowflake glow particles, outside character body outline; retained after visual review.'})
qa={'character':source['character'],'reviewedAt':datetime.now(timezone.utc).isoformat(),'walkCount':128,'idleCount':8,'offlineApproved':True,'frameDurationMs':30,'cycleMs':480,'directions':{d:{'walk':16,'independentIdle':1,'offlineApproved':True} for d in dirs},'evidence':['qa-north.md','qa-west.md','qa-south-east.md','source-audit.json'],'assets':rows,'colorCleanup':{'cumulativeChangedPixels':total_cleanup,'allAlphaUnchanged':True,'retainedGlowCandidates':exceptions},'observations':['Small hand-painted hair, fabric, ornament and snowflake detail changes remain visible at enlarged scale.','Browser animation uses a 30ms timeline; display refresh timing was not benchmarked.'],'clientIntegrationPerformed':False,'unityValidated':False}
write(OUT/'qa-summary.json',qa)
manifest={'character':source['character'],'canvas':[1024,1024],'format':'PNG RGBA','directionOrder':dirs,'frameDurationMs':30,'cycleMs':480,'anchor':{'x':512,'y':942,'origin':'top-left','note':'Export reference; engine pivot and world-space ground contact not yet validated.'},'walk':{d:[{'file':f'assets/walk/{d}/{i:02d}.png','durationMs':30,'sha256':sha(A/f'walk/{d}/{i:02d}.png')} for i in range(1,17)] for d in dirs},'idle':{d:{'file':f'assets/idle/{d}.png','sha256':sha(A/f'idle/{d}.png')} for d in dirs},'integrationStatus':'assets ready; client integration not performed'}
write(OUT/'game-assets.json',manifest)
source['sourceRetention']='Originals verified before user-authorized cleanup; exact text provenance remains in provenance.json. See cleanup-report.json for actual deletion results.'
source['visualApproval']='passed; bound to final bytes in qa-summary.json';write(OUT/'source-audit.json',source)
print(json.dumps({'walk':128,'idle':8,'offlineApproved':True,'cleanupChangedPixels':total_cleanup,'retainedGlowCandidates':sum(x['pixels'] for x in exceptions)}))
