from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, io
import numpy as np
from PIL import Image

ROOT=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005')
SPRING=ROOT/'lanxian_spring';OUT=ROOT/'parent_audit_20261008/town'
observed={};images={};bindings=[];gaps=[];claims=[]
def sha(b):return hashlib.sha256(b).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def raw(p):
 p=Path(p);b=p.read_bytes();observed.setdefault(str(p),{'path':str(p),'beforeSha256':sha(b),'observedAt':now()});return b
def read(p):return json.loads(raw(p).decode('utf-8-sig'))
def img(p):
 p=Path(p)
 if str(p) not in images:images[str(p)]=Image.open(io.BytesIO(raw(p))).convert('RGB')
 return images[str(p)]
def ref(p):
 p=Path(p);raw(p);return {'path':str(p),'sha256':observed[str(p)]['beforeSha256']}
def bbox(mask):
 yy,xx=np.where(mask)
 return [int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)] if len(xx) else None
def mapping(board,source,sourceBox,boardBox,rotation=0):
 a=img(source).crop(tuple(sourceBox))
 if rotation:a=a.transpose(Image.Transpose.ROTATE_90)
 b=img(board).crop(tuple(boardBox))
 aa=np.asarray(a);bb=np.asarray(b)
 if aa.shape!=bb.shape:return {'source':ref(source),'sourceROI':sourceBox,'boardROI':boardBox,'shapeMismatch':[list(aa.shape),list(bb.shape)],'exact':False}
 diff=np.any(aa!=bb,axis=2)
 return {'source':ref(source),'sourceROI':sourceBox,'sourceCoordinates':'extended local' if img(source).size==(4326,4326) else 'core local','boardROI':boardBox,'losslessRotationDegrees':rotation,'resampling':None,'exact':not bool(diff.any()),'comparedPixels':int(diff.size),'mismatchedPixels':int(diff.sum()),'mismatchBBoxInBoardROI':bbox(diff),'expectedCropRawRgbSha256':sha(aa.tobytes()),'observedCropRawRgbSha256':sha(bb.tobytes())}
def board_entry(board,review,expected=None):
 e={'board':ref(board),'review':ref(review),'expectedBoardSha256FromSourceRecord':expected,'boardHashMatchesSourceRecord':observed[str(Path(board))]['beforeSha256']==expected if expected else None,'mappings':[],'actualViewedByThisAudit':False}
 bindings.append(e);return e
def match_crop(board,source):
 a=np.asarray(img(source)); b=np.asarray(img(board)); bh,bw=b.shape[:2];ah,aw=a.shape[:2]
 if bh>ah or bw>aw:return None
 # Candidate locations are exact RGB matches of first pixel; confirm full crop.
 for y in range(ah-bh+1):
  xs=np.flatnonzero(np.all(a[y,:aw-bw+1]==b[0,0],axis=1))
  for x in xs:
   if not np.array_equal(a[y,x+min(10,bw-1)],b[0,min(10,bw-1)]):continue
   if np.array_equal(a[y:y+bh,x:x+bw],b):return [int(x),y,int(x+bw),y+bh]
 return None

started=now()
c10=SPRING/'r08_c10/selected-v2/core4096.png';x10=SPRING/'r08_c10/selected-v2/extended4326.png'
c09=SPRING/'r08_c09/repairs/join-endpoint/candidate_4096.png';x09=SPRING/'r08_c09/repairs/join-endpoint/candidate_with_halo.png'
c11=SPRING/'r09_c10/selected-v2/core4096.png';x11=SPRING/'r09_c10/selected-v2/extended4326.png'
for p in (c10,x10,c09,x09,c11,x11):img(p)

# r09 c10: retain the actual historical review; bind its exact image hashes and ROIs.
t=SPRING/'r09_c10/tone-refinement';review=t/'qa/final-review.json';rr=read(review);scope=read(t/'qa/scope-and-metrics.json');boxes=read(t/'qa/boxes.json')
claims.append({'tile':'r09_c10','review':ref(review),'decision':rr['decision'],'visualFindings':rr['visualFindings'],'unresolvedInheritedGeometryOrExcludedSeams':rr['unresolvedInheritedGeometryOrExcludedSeams'],'supplementScope':'Bind only 23 named historical reviewed images to current selection; no new artistic review.'})
assert scope['imageSHA256']['core4096.png']==ref(c11)['sha256']
assert scope['imageSHA256']['extended4326.png']==ref(x11)['sha256']
for item in rr['reviewedImages']:
 board=t/item['file'];name=board.name;e=board_entry(board,review,item['sha256'])
 if name=='preview1254.png':
  res=img(c11).resize((1254,1254),Image.Resampling.LANCZOS);e['previewOnly']=True;e['downsample']='Pillow LANCZOS 4096 to1254; not native-pixel QA'
  e['previewMatchesCurrentCoreDownsample']=np.array_equal(np.asarray(res),np.asarray(img(board)))
 elif name in scope['scopes']:
  sc=scope['scopes'][name];rotation=sc['horizontalStripsQAOnlyRotationDegrees'];x=0
  for box in sc['boxesExtendedLTRB']:
   crop=img(x11).crop(tuple(box))
   if rotation:crop=crop.transpose(Image.Transpose.ROTATE_90)
   w,h=crop.size;e['mappings'].append(mapping(board,x11,box,[x,0,x+w,h],rotation));x+=w
  e['layoutEvidence']=ref(t/'qa/scope-and-metrics.json')
 elif name.startswith('north-'):
  j=int(name.split('-')[1])-1
  e['mappings']=[mapping(board,c10,[j*1024,3904,(j+1)*1024,4096],[0,0,1024,192]),mapping(board,c11,[j*1024,0,(j+1)*1024,192],[0,192,1024,384])]
 elif name.endswith('-after.png') and name[:-10] in boxes:
  box=boxes[name[:-10]];w,h=img(board).size;e['mappings']=[mapping(board,c11,box,[0,0,w,h])]
 else:
  box=match_crop(board,c11)
  if box:
   w,h=img(board).size;e['mappings']=[mapping(board,c11,box,[0,0,w,h])];e['coordinateEvidence']='Exact full RGB subimage search, then full crop comparison; not geometric registration.'
  else:gaps.append({'board':str(board),'reason':'Could not prove direct full-crop coordinates in current candidate.'})

# r08 c10 final color edits: preserved native crop and AFTER panels.
t=SPRING/'r08_c10';review=t/'selected-v2/visual-review.json';rr=read(review);claims.append({'tile':'r08_c10','review':ref(review),'scopedChecks':rr['scopedChecks'],'knownMinorLimitations':rr['knownMinorLimitations'],'remainingAcceptance':rr['remainingAcceptance'],'supplementScope':'Native central/SW/west and final color-patch pixels only; record gaps and changed old scopes explicitly.'})
polish=t/'repairs/final-color-patches';pr=read(polish/'processing.json');crop=pr['cropBox']
assert pr['repairSha256']==ref(c10)['sha256']
board=polish/'final-crop1254.png';gen=read(polish/'final-crop1254.png.generation.json');e=board_entry(board,polish/'processing.json',gen.get('sha256'));e['mappings']=[mapping(board,c10,crop,[0,0,1254,1254])];e['existingObservation']=pr['visualQA']
board=polish/'qa-native.png';gen=read(polish/'qa-native.png.generation.json');e=board_entry(board,polish/'processing.json',gen.get('sha256'))
for name,box,y in [('pillar',[995,700,1230,910],26),('leaf',[100,1110,265,1254],254)]:
 bx=[248,y,248+box[2]-box[0],y+box[3]-box[1]];sr=[crop[0]+box[0],crop[1]+box[1],crop[0]+box[2],crop[1]+box[3]]
 e['mappings'].append(dict(mapping(board,c10,sr,bx),panel=name+' AFTER'))
e['existingObservation']=pr['visualQA']
e['scopeNote']='Final processing review explicitly names native crop/standalone local crops; retained qa-native AFTER panels verified as corroborating pixel evidence. This audit does not invent a historical viewing claim for this panel.'

# Central front/back: final selection review explicitly states both1254 crops were seen.
central=t/'spring-edits/central';cp=read(central/'composition-record.json')
for cr in cp['crops']:
 board=central/(cr['name']+'-composited-1254.png');e=board_entry(board,review);box=cr['sourceCrop'];m=mapping(board,c10,box,[0,0,1254,1254]);e['mappings']=[m];e['historicalClaim']='Final selection review states central front/back1254 original pixels were viewed.'
 if not m['exact']:
  aa=np.asarray(img(c10).crop(tuple(box)));bb=np.asarray(img(board));df=np.any(aa!=bb,axis=2);yy,xx=np.where(df);covered=(xx+box[0]>=crop[0])&(xx+box[0]<crop[2])&(yy+box[1]>=crop[1])&(yy+box[1]<crop[3])
  e['changedPixelsCoveredByFinalReviewedNativeCrop']=bool(covered.all());e['changedPixelCount']=int(df.sum());e['replacementEvidence']=ref(polish/'final-crop1254.png');e['inheritance']='Only byte-identical pixels retain the earlier scoped observation. Changed pixels are covered by the separately verified final native crop.' if covered.all() else 'Uncovered changed pixels remain.'
  if not covered.all():gaps.append({'board':str(board),'uncoveredChangedPixels':int((~covered).sum()),'reason':'Changed ROI not fully covered by final color native crop.'})

# Southwest reviewed single crop uses extended coordinates including bottom/left halo.
sw=t/'spring-edits/southwest';swp=read(sw/'processing.json');swr=read(sw/'visual-review.json');board=sw/'edited-1254.png';e=board_entry(board,sw/'visual-review.json');e['mappings']=[mapping(board,x10,swp['cropInExtended'],[0,0,1254,1254])];e['existingObservation']=swr['observations']
e['historicalReviewBindingLimitation']='Existing visual-review has no crop hash and predates the current processing record. Later full-edge review names a different southwest source SHA. Pixel equality proves the retained crop matches current selected art; it does not prove the revised crop was actually viewed at the earlier review time.'
gaps.append({'board':str(board),'reason':'Current southwest crop is pixel-bound, but historical local review is un-hashed and predates the current mask/composition. Cannot inherit earlier visual acceptance for subsequently changed pixels without a fresh scoped view.','reviewedAt':swr['reviewedAtUtc'],'currentProcessingCreatedAt':swp['createdAtUtc'],'currentMatchingCropInExtended':swp['cropInExtended']})

# Western narrow repair boards: AFTER half consists of current west neighbor and current selected c10.
west=t/'shared-geometry/west-edge-repair';wp=read(west/'processing.json');wr=read(west/'visual-review.json')
for qb in wp['qaBoards']:
 board=Path(qb['file']);e=board_entry(board,west/'visual-review.json',qb['sha256']);x1,y1,x2,y2=qb['c10RelativeBoxLTRB'];h=y2-y1
 if x1<0:e['mappings'].append(mapping(board,c09,[4096+x1,y1,4096+min(x2,0),y2],[0,h,min(x2,0)-x1,2*h]))
 if x2>0:e['mappings'].append(mapping(board,c10,[max(x1,0),y1,x2,y2],[max(0,-x1),h,x2-x1,2*h]))
 e['existingObservation']=next(z['observation'] for z in wr['actualViewed'] if z['file']==str(board))

# All four full western common-edge boards and two corner boards explicitly named in old review.
q=t/'shared-geometry/qa';qr=read(q/'visual-review.json');cm=read(q/'southwest/comparison-manifest.json')
for qb in cm['outputs']:
 if qb['kind'] not in ('exact_core_join','corner_with_halo'):continue
 board=Path(qb['file']);e=board_entry(board,q/'visual-review.json',qb['sha256'])
 if qb['kind']=='exact_core_join':
  e['mappings']=[mapping(board,c09,qb['leftCropC09'],[0,0,512,1024]),mapping(board,c10,qb['rightCropC10'],[512,0,1024,1024])]
  y=qb['c10Y'][0];e['existingObservation']=next(z['observed'] for z in qr['coverage'] if z['c10Y'][0]==y)
  m=e['mappings'][1]
  if not m['exact']:
   a=np.asarray(img(c10).crop(tuple(qb['rightCropC10'])));b=np.asarray(img(board).crop((512,0,1024,1024)));df=np.any(a!=b,axis=2);yy,xx=np.where(df);covered=(xx<240)&(yy+y>=1120)&(yy+y<1400)
   e['changedPixelsCoveredByWestRepairAfterBoard']=bool(covered.all());e['uncoveredChangedPixels']=int((~covered).sum())
   if not covered.all():gaps.append({'board':str(board),'uncoveredChangedPixels':int((~covered).sum()),'mismatchBBoxInC10Core':[int(xx.min()),int(yy.min()+y),int(xx.max()+1),int(yy.max()+1+y)],'reason':'Old full-west board differs beyond the explicitly reviewed narrow west-repair ROI.'})
 else:
  y=qb['c10Y'][0]
  e['mappings']=[mapping(board,x09,[3699,y+115,4211,y+627],[0,0,512,512]),mapping(board,x10,[115,y+115,627,y+627],[512,0,1024,512])]
  e['existingObservation']=next(z['observed'] for z in qr['corners'] if Path(z['file']).name==board.name)
  if not e['mappings'][1]['exact']:
   m=e['mappings'][1];bb=m['mismatchBBoxInBoardROI'];e['currentChangedPixelsAlsoPresentInPixelBoundSouthwestCrop']=True
   gaps.append({'board':str(board),'uncoveredChangedPixels':m['mismatchedPixels'],'mismatchBBoxInC10Core':[bb[0],bb[1]+y,bb[2],bb[3]+y],'reason':'Old southwest corner board differs from current selection. Same revised southwest surface as lower full-edge gap; current single crop matches pixels but earlier review does not hash-bind its revision.'})

# Current preview is composition evidence only, and extended center must equal core.
for tile,core,ext in [('r08_c10',c10,x10),('r09_c10',c11,x11)]:
 assert np.array_equal(np.asarray(img(core)),np.asarray(img(ext).crop((115,115,4211,4211))))
for b in bindings:
 b['allMappedPixelsExact']=bool(b['mappings']) and all(m['exact'] for m in b['mappings'])
 if b.get('boardHashMatchesSourceRecord') is False:gaps.append({'board':b['board']['path'],'reason':'Board SHA does not match historical record.'})
for o in observed.values():
 p=Path(o['path']);o['afterSha256']=sha(p.read_bytes()) if p.exists() else None;o['stableDuringAudit']=o['beforeSha256']==o['afterSha256']
result={'schemaVersion':1,'startedAtUtc':started,'finishedAtUtc':now(),'role':'Read-only exact pixel binding supplement; no fresh artistic judgments or re-acceptance.','currentCandidates':{'r08_c10':ref(c10),'r09_c10':ref(c11)},'extendedSources':{'r08_c10':ref(x10),'r09_c10':ref(x11)},'coordinateConvention':'All boxes integer left,top,right,bottom; half-open; 0-based. Source coordinates are core unless explicitly extended; no production image writes.','historicalReviewClaims':claims,'bindings':bindings,'gaps':gaps,'summary':{'boardRecords':len(bindings),'allMappingsExactBoards':sum(x['allMappedPixelsExact'] for x in bindings),'previewBoards':sum(x.get('previewOnly',False) for x in bindings),'boardsWithPartiallyChangedPixels':sum(bool(x['mappings']) and not x['allMappedPixelsExact'] for x in bindings),'gaps':len(gaps),'formalAccepted':False,'wholeCityComplete':False,'pixelsOrTaskFilesEdited':False},'observedFiles':list(observed.values()),'changedDuringAudit':[x for x in observed.values() if not x['stableDuringAudit']]}
(OUT/'qa-binding-supplement.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(OUT/'qa-binding-supplement.json'),'summary':result['summary'],'gaps':gaps,'changedDuringAudit':len(result['changedDuringAudit'])},ensure_ascii=True))
