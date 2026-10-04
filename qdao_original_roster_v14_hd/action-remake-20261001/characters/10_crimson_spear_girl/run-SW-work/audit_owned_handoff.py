from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json
root=Path(__file__).resolve().parent.parent
items=[]
for p in sorted((root/'cast-work').glob('cast-?-??.png')):items.append(('cast',p,hashlib.sha256(p.read_bytes()).hexdigest()))
for sub in ['grounding-SE-work','run-SW-work']:
 s=json.loads((root/sub/'selection.json').read_text(encoding='utf8'))
 for e in s['entries']:items.append((sub,(root/sub/e['path']).resolve(),e['sha256']))
seen={};out=[]
for group,p,h in items:
 actual=hashlib.sha256(p.read_bytes()).hexdigest();assert actual==h,(p,'SHA mismatch')
 assert h not in seen,(p,'duplicate selection',seen.get(h));seen[h]=p.as_posix()
 rp=Path(str(p)+'.generation.json');r=json.loads(rp.read_text(encoding='utf8'));assert r['sha256']==h
 with Image.open(p) as im:
  assert im.mode=='RGBA' and min(im.size)>=1024
  extrema=im.getchannel('A').getextrema();assert extrema==(0,255)
  out.append(dict(group=group,path=p.as_posix(),sha256=h,nativeSize=list(im.size),mode=im.mode,alphaExtrema=list(extrema),sourceRecord=rp.as_posix(),actualModel=r.get('actualModel'),actualQuality=r.get('actualQuality')))
report=dict(checkedAt=datetime.now(timezone.utc).isoformat(),nativeSelections=len(out),counts={g:sum(e['group']==g for e in out) for g in ['cast','grounding-SE-work','run-SW-work']},allSourceSHAUnique=True,allSHAAndRGBAAndNativeDimensionChecksPassed=True,sourceModelDisclosure='actual model/quality null when unreported, configured target remains separate',fullSequenceDynamicPassed=False,clientTested=False,entries=out)
(root/'run-SW-work'/'FINAL_NATIVE_HANDOFF_AUDIT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
p=root/'cast-work'/'STATUS.json';r=json.loads(p.read_text(encoding='utf8'));r['status']='32 native slots available, targeted continuity/toe/ground repairs selected; root fixed-direction playback verification pending';r['reviewSummary']=['All32 native slots RGBA>=1024 with independent SHA and source records.','W06/W07 tip margins repaired; E04/E06/E08/E12/E15/W08 continuity corrections selected.','E05/E07 rear toes corrected without narrowing stance; remaining foot directions individually checked and preserved where correct.','W15 knee/shin extension restores recovery support; returned modest head shift recorded.','Root has exported constant direction transforms; no full dynamic/client pass claimed here.'];p.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k!='entries'}))
