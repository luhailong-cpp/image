import json,hashlib
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
r=Path(__file__).resolve().parents[2]
report={'reviewer':'ne_finish independent review','createdAt':datetime.now(timezone.utc).isoformat(),'scope':'48 selected south-facing native sources; all full/lower-body contact sheets plus targeted native inspection','dynamicPlaybackObserved':False,'directions':{}}
for d in ['S','SE','SW']:
 p=r/f'generation/run/{d}/selection-middle4-side2-20261004.json'; rows=json.loads(p.read_text(encoding='utf-8-sig')); rows=rows['frames'] if isinstance(rows,dict) else rows
 result={'selection':p.relative_to(r).as_posix(),'selectionSha256':hashlib.sha256(p.read_bytes()).hexdigest(),'frames':[],'hardFindings':[]}
 for f in rows:
  src=r/f['source']; sha=hashlib.sha256(src.read_bytes()).hexdigest();im=Image.open(src)
  assert sha==f.get('sourceSha256',f.get('sha256')) and im.mode=='RGBA' and im.size==(1254,1254)
  actual=f['supportFoot']; status='no hard static defect identified'
  if d=='SW' and src.stem in ['07-v6','08-v8']:
   actual='left'; status='FAIL: wrong support-foot identity'
   result['hardFindings'].append({'frame':f['frame'],'source':f['source'],'sha256':sha,'confidence':'high','issue':'Expected right rear support, but actual grounded posterior leg connects to near anatomical left hip on screen-right/gourd side. Foreground advanced leg connects to far anatomical right hip on screen-left.','impact':'Premature switch from right support at06 to left support at07-08; violates eight continuous right support frames and causes incorrect limb phase.','repair':'Far anatomical right leg from screen-left hip must extend rearward behind the foreground left thigh, with forefoot contact; near left leg advances airborne, producing natural crossing/occlusion. Do not relabel or mirror.'})
  result['frames'].append({'frame':f['frame'],'source':f['source'],'sourceSha256':sha,'expectedSupportFoot':f['supportFoot'],'observedSupportFoot':actual,'position':f.get('position',f.get('supportPositionAlongRun')),'status':status,'durationMs':f['durationMs']})
 assert len({x['sourceSha256'] for x in result['frames']})==16 and sum(x['durationMs'] for x in result['frames'])==1200
 result['hands']='Left hand holds gourd in all16; right hand empty; no new swapped-hand hard defect observed.'
 result['shoeAxes']='No high-confidence sudden outward shoe-axis rotation found in selected sprites.'
 result['notes']=({'S':['S03 source05-v2 and S04 source04-v3 inspected natively: empty right hand remains forward across transition; no former back-swing reversal.','Right01-08 and left09-16 thigh-to-shoe connections consistent; posterior contact inferred from front-view foreshortening.'], 'SE':['SE15-v6 and16-v5 inspected natively: near right thigh crosses toward forward image-right shoe, with far LEFT support behind it extending image-left/rear. Left support identity is consistent.','SE14 source13-v5 also inspected for transition; no side swap identified.'],'SW':['SW07-v6 and08-v8 inspected natively and rejected for actual LEFT rather than RIGHT rear support.','SW15 source12-v1 and SW16 source16-v4 inspected natively: rear leg remains near anatomical left/gourd-side hip; no side swap.16 has a short foreshortened posterior limb and downward toe tip consistent with possible forefoot contact; world-ground contact height cannot be proven from alpha image alone.']})[d]
 result['decision']='requires targeted repair' if result['hardFindings'] else 'no hard static defect found; dynamic unverified'
 report['directions'][d]=result
report['limitations']=['No browser/client playback inspected.','Static drawn sole, ankle, knee and overlap evidence does not measure world-ground plane or runtime slip.','Snapshot hashes bind these findings to the selected native files at review time.']
(r/'review/grounding-fourframes/S-SE-SW-independent-static-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print('48 native sources checked; hard findings: '+str(sum(len(v['hardFindings']) for v in report['directions'].values())))
