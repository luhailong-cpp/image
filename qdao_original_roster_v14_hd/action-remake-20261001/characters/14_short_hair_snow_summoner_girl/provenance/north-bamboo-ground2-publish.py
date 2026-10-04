import json,sys,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
R=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/14_short_hair_snow_summoner_girl')
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
d=sys.argv[1]
assert d in ['N','NE']
rows=read(R/'run/staging'/f'north-bamboo-ground2-proposed-{d}.jpg.sources.json')
obs=read(R/'provenance'/f'north-bamboo-ground2-{d}-visual-observations.json')
now=datetime.now(timezone.utc).isoformat();frames=[];registrations=[]
for i,row in enumerate(rows):
 f=i+1;src=R/row['file'];dst=R/'run'/d/f'{f:02}.png';old=read(Path(str(dst)+'.generation.json'));oldsha=sha(dst)
 assert sha(src)==row['sha256']
 if src!=dst:
  meta=read(Path(str(src)+'.generation.json'));shutil.copy2(src,dst)
  meta['previousFormalEvidence']={'sha256':oldsha,'derivedFrom':old.get('derivedFrom'),'review':old.get('review'),'registrationTransform':old.get('registrationTransform')}
 else:meta=old
 meta.update(file=dst.relative_to(R).as_posix(),sha256=sha(dst),actualModel=None,actualQuality=None)
 rt=meta['registrationTransform'];rt.update(file=meta['file'],status='applied',outputSha256=meta['sha256'],registrationFile=f'run/{d}/ground2-registration.json')
 meta['review']={'status':'static_pending_root_preview','notes':obs['observations'][i],'direction':'four spatial contact zones; same support foot for eight frames','independentFinalReview':'pending_root_1200ms_animation'}
 leg='left' if f<=8 else 'right';pos='P'+str(((f-1)%8)//2+1)
 meta['phase']={'supportLeg':leg,'position':pos,'variant':1+(f-1)%2,'durationMs':75,'noFlightPhase':True}
 save(Path(str(dst)+'.generation.json'),meta)
 frame={'frame':f,'file':meta['file'],'sha256':meta['sha256'],'selectedNative':meta['derivedFrom']['file'],'supportLeg':leg,'position':pos,'phase':leg+'_'+pos,'durationMs':75,'observations':obs['observations'][i],'hands':'左臂抱一只白狐；右肩肘腕连接到唯一托晶掌，各帧上身/摆臂保留已审查版本。','footAxis':'膝踝到足掌沿当前方向前后轴，鞋底俯仰与足外翻分别检查。','reviewStatus':'static_pending_root_preview','registrationEvidence':rt}
 frames.append(frame);registrations.append(rt)
contact={'schemaVersion':2,'direction':d,'recordedAt':now,'reviewer':'north_run','status':'static_pending_root_preview','cycleDurationMs':1200,'frameDurationMs':75,'criterion':'four spatial pairs per support foot: front landing, under hip, slightly rear load, rear toe-pad push-off; two independent poses each','evidence':{'actualVisualReview':True,'currentContactSheet':f'run/staging/north-bamboo-ground2-proposed-{d}.jpg','sourceShaList':f'run/staging/north-bamboo-ground2-proposed-{d}.jpg.sources.json'},'contacts':[{'frames':list(range(1,9)),'supportLeg':'left','observations':'同一实体左腿由前侧落地连续经过髋下、稍后负重至后侧前掌蹬离，右腿在空中回收。'},{'frames':list(range(9,17)),'supportLeg':'right','observations':'同一实体右腿由前侧落地连续经过髋下、稍后负重至后侧前掌蹬离，左腿在空中回收。'}],'positionPairs':[{'frames':[2*k+1,2*k+2],'position':'P'+str(k%4+1),'supportLeg':'left' if k<4 else 'right','observations':obs['pairs'][k]} for k in range(8)],'frames':frames,'pending':['root actual 1200ms playback and final acceptance']}
cp=R/'audit'/f'contact-{d}-review.json'
if cp.exists():contact['supersededAudit']={'status':read(cp).get('status'),'sha256':sha(cp),'criterionNote':'Earlier reviews described previous images/rules and do not certify the new four-spatial-pair criterion.'}
save(cp,contact)
gp=R/'run'/d/'grounding-review.json';oldg=read(gp) if gp.exists() else {}
save(gp,{'schemaVersion':2,'direction':d,'status':'static_pending_root_preview','recordedAt':now,'frames':frames,'contacts':contact['contacts'],'positionPairs':contact['positionPairs'],'historicalReview':oldg,'historicalNote':'Old selectedNative, SHA and phase labels apply only to former images; current frames above supersede them.'})
save(R/'run'/d/'ground2-registration.json',{'direction':d,'recordedAt':now,'globalScale':0.8,'targetRoot':[512,942],'method':'native full canvas downsample and one global affine at inherited anatomical root; no bbox fitting or sole alignment','frames':registrations})
save(R/'audit'/f'bamboo-ground2-{d}-selection.json',{'direction':d,'recordedAt':now,'status':'static_pending_root_preview','frames':frames,'replaced':[r['frame'] for r in rows if '/staging/' in r['file']],'retained':[r['frame'] for r in rows if '/staging/' not in r['file']]})
print(f'Published {d} with 16 SHA-linked records; final animation pending')

