"""Independent verification. Does not import or execute the candidate builder.
Default execution writes a new QA report only; no canonical/image writes.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
import numpy as np
from PIL import Image

Q=Path(__file__).resolve().parent
Z=Q.parents[2]
EXPECTED={
 'r09_c08':('p44','5c3896b829f0b55d99fc589cdfa64e8fdc137479f2aa2ac31df1a973920fb8bc','106d6079fa3b42739bcc9386773189d9b856d407c65d7772ed5ee2733f2081d9'),
 'r10_c08':('p14','495536017d01bd3c3c6783129edda1f85a9e55ab71c91db8df5cbdef6e7d4a45','08f6cbf51ef539e52e6badd617313e061fb2f04aa04650eecf57419af7ed8f72')}
PINS={
 "jamb-v1-surface-v2.adoption-instructions.json": "7996a1064e186221d5b731cb871ac04dfa309f7b121ca5aa06b758848c141b23",
 "jamb-v1-surface-v2-proof.json": "be15749f58522837a2844514a964bf58a7abd3f558c3ba0ed2ec81fec8b917d0",
 "jamb-v1-surface-v2-raw.png": "4afa629b0437e7919e264c186cbad25a31450f7500b2585f81314f726c757955",
 "jamb-v1-surface-v2-binary-mask.png": "5058bd24af582d9ef84c315429009c752446ce7cd1feabef58c987bbcdadfa1a",
 "jamb-input-v1-1254.png": "49d1627b68dd64d626b985030686084e3113a37e43b826719eeff86a4d54a1ea"
}
def now():return datetime.now(timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def pixels(p):
 im=Image.open(p);assert im.mode=='RGB',(p,im.mode)
 return np.asarray(im)
def new_json(p,value):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def tile_origin(tile):return ((int(tile[5:7])-1)*4096,(int(tile[1:3])-1)*4096)
def assemble(tile,selection,replacement=None):
 out=np.empty((4096,4096,3),dtype=np.uint8);sources=[]
 assert set(selection['patches'])=={f'p{r}{c}' for r in range(1,5) for c in range(1,5)}
 for pid,rel in sorted(selection['patches'].items()):
  p=Path(replacement) if replacement and pid==EXPECTED[tile][0] else Z/tile/rel
  a=pixels(p);assert a.shape==(1254,1254,3)
  x,y=(int(pid[2])-1)*1024,(int(pid[1])-1)*1024
  out[y:y+1024,x:x+1024]=a[115:1139,115:1139]
  sources.append({'patch':pid,'file':str(p),'sha256':sha(p),'crop':[115,115,1139,1139],'destination':[x,y]})
 return out,sources
def evidence_specs(tile):
 if tile=='r09_c08':
  review=Z/tile/'qa/complete-native-20261013-v2/independent-replay-and-review.json'
  data=read(review);ox,oy=tile_origin(tile)
  result=[{'file':e['file'],'sha256':e['sha256'],'tileBox':[e['globalBox'][0]-ox,e['globalBox'][1]-oy,e['globalBox'][2]-ox,e['globalBox'][3]-oy],'priorStatus':e.get('visualReview'),'priorReview':str(review),'priorReviewSha256':sha(review)} for e in data['evidence']]
 else:
  d=Z/tile/'processed/colorpass';result=[]
  names=[]
  for r in range(1,5):
   for c in range(1,5):
    if c<4:names.append(f'p{r}{c}-p{r}{c+1}-horizontal-after-100pct.png')
    if r<4:names.append(f'p{r}{c}-p{r+1}{c}-vertical-after-100pct.png')
  names += [f'crossing-r{r}-c{c}-after-100pct.png' for r in range(1,4) for c in range(1,4)]
  for name in names:
   p=d/name;meta=read(p.with_suffix('.png.derivation.json'))
   result.append({'file':str(p),'sha256':meta['sha256'],'tileBox':meta['tileBox'],'priorStatus':'Preserve historical QA status; pixel reuse is not a new visual pass.','priorReview':str(Z/tile/'qa/active-review-20261011.json')})
 assert len(result)==33 and len({e['file'] for e in result})==33
 return result
def verify_current():
 started=now()
 for name,digest in PINS.items():assert sha(Q/name)==digest,('Pinned artifact changed',name)
 review=read(Q/'jamb-v1-surface-v2.adoption-instructions.json');proof=read(Q/'jamb-v1-surface-v2-proof.json');inp=read(Q/'jamb-input-v1.json')
 assert review['recommendAdoption'] and review['localGeometryPassed'] and review['adoptTogether']
 assert {x['tile'] for x in review['patches']}==set(EXPECTED)
 raw=pixels(Q/'jamb-v1-surface-v2-raw.png');base=pixels(Q/'jamb-input-v1-1254.png')
 assert raw.shape==base.shape==(1254,1254,3)
 maskraw=np.asarray(Image.open(Q/'jamb-v1-surface-v2-binary-mask.png'))
 assert maskraw.shape==(1254,1254) and set(np.unique(maskraw).tolist())=={0,255}
 mask=maskraw==255;protected=np.asarray(Image.open(Q.parent/'window-joint-20261016/window-joint-v1-binary-mask.png'))>0;assert not np.any(mask & protected);fx,fy,ex,ey=review['frameGlobalBox'];assert [fx,fy,ex,ey]==[31744,36065,32998,37319]
 # Independent selected core assembly of the complete conditioning frame.
 rebuilt=np.empty_like(base);coverage=np.zeros((1254,1254),np.uint8)
 conditioning=[]
 for s in inp['sources']:
  p=Path(s['file']);assert sha(p)==s['sha256']
  sel=read(Z/s['tile']/'selected-patches.json');assert (Z/s['tile']/sel['patches'][s['patch']]).resolve()==p.resolve()
  ox,oy=tile_origin(s['tile']);ox+=(int(s['patch'][2])-1)*1024;oy+=(int(s['patch'][1])-1)*1024
  x0,y0,x1,y1=max(ox,fx),max(oy,fy),min(ox+1024,ex),min(oy+1024,ey)
  a=pixels(p)[115+y0-oy:115+y1-oy,115+x0-ox:115+x1-ox]
  rebuilt[y0-fy:y1-fy,x0-fx:x1-fx]=a;coverage[y0-fy:y1-fy,x0-fx:x1-fx]+=1
  conditioning.append({'file':str(p),'sha256':s['sha256']})
 assert np.all(coverage==1) and np.array_equal(rebuilt,base)
 expectedjoint=base.copy();expectedjoint[mask]=raw[mask]
 assert np.array_equal(expectedjoint,pixels(proof['jointCandidate']))
 before={};selections={};records=[];assemblies={};qa={};all_sources={}
 for t in review['patches']:
  tile=t['tile'];pid,source_sha,candidate_sha=EXPECTED[tile]
  assert (t['patch'],t['sourceSha256'],t['candidateSha256'])==(pid,source_sha,candidate_sha)
  source=Path(t['source']);candidate=Path(t['candidate']);assert sha(source)==source_sha and sha(candidate)==candidate_sha
  canonical=Z/tile/'selected-patches.json';before[tile]=canonical.read_bytes();sel=json.loads(before[tile].decode('utf-8-sig'));selections[tile]=sel
  assert (Z/tile/sel['patches'][pid]).resolve()==source.resolve(),('Canonical source changed',tile)
  old=pixels(source);new=pixels(candidate);assert old.shape==new.shape==(1254,1254,3)
  ox,oy=tile_origin(tile);ox+=(int(pid[2])-1)*1024-115;oy+=(int(pid[1])-1)*1024-115
  # Map every candidate-native pixel independently into the frame.
  yy,xx=np.indices((1254,1254));mx=xx+ox-fx;my=yy+oy-fy
  eligible=(xx>=115)&(xx<1139)&(yy>=115)&(yy<1139)&(mx>=0)&(mx<1254)&(my>=0)&(my<1254)
  native_mask=np.zeros((1254,1254),bool);native_mask[eligible]=mask[my[eligible],mx[eligible]]
  assert np.array_equal(new[~native_mask],old[~native_mask])
  assert np.array_equal(new[native_mask],raw[my[native_mask],mx[native_mask]])
  halo=np.ones((1254,1254),bool);halo[115:1139,115:1139]=False;assert np.array_equal(new[halo],old[halo])
  assert int(native_mask.sum())==t['maskPixels'] and int(np.any(new!=old,axis=2).sum())==t['changedPixels']
  current,current_sources=assemble(tile,sel);updated,updated_sources=assemble(tile,sel,candidate)
  prior_candidate=Path(sel['candidate']);assert np.array_equal(pixels(prior_candidate),current),('Stale current full candidate',tile)
  evidence=[]
  for e in evidence_specs(tile):
   ep=Path(e['file']);assert sha(ep)==e['sha256'];x0,y0,x1,y1=e['tileBox'];assert 0<=x0<x1<=4096 and 0<=y0<y1<=4096
   crop=pixels(ep);assert np.array_equal(crop,current[y0:y1,x0:x1]),('Old evidence not current',tile,str(ep))
   assert np.array_equal(crop,updated[y0:y1,x0:x1]),('Changed internal evidence needs QA',tile,str(ep))
   evidence.append(dict(e,currentCoreReplayExact=True,postAdoptionCoreReplayExact=True,unchangedPixelReuse=True,newVisualPassClaimed=False))
  assemblies[tile]=updated;all_sources[tile]=updated_sources;qa[tile]=evidence
  records.append(dict(tile=tile,patch=pid,source=str(source),sourceSha256=source_sha,candidate=str(candidate),candidateSha256=candidate_sha,sourceNativeOrigin=[ox,oy],outsideMaskExact=True,insideMaskSameCoordinateRawExact=True,haloExact=True,maskPixels=int(native_mask.sum()),changedPixels=int(np.any(new!=old,axis=2).sum()),selectionSha256=hashlib.sha256(before[tile]).hexdigest(),full4096Replayed=True,internalEvidenceUnchangedCount=len(evidence)))
 for e in review['evidence']:
  ep=Path(e['file']);assert sha(ep)==e['sha256'];x0,y0,x1,y1=e['frameBox'];assert np.array_equal(pixels(ep),expectedjoint[y0:y1,x0:x1])
 for tile in EXPECTED:assert (Z/tile/'selected-patches.json').read_bytes()==before[tile]
 for s in conditioning:assert sha(s['file'])==s['sha256']
 for sources in all_sources.values():
  for s in sources:assert sha(s['file'])==s['sha256']
 report={'startedAtUtc':started,'completedAtUtc':now(),'status':'independent_replay_passed','canonicalModified':False,'adoptionExecuted':False,'pinnedArtifactHashes':PINS,'conditioningFrameExact':True,'jointMaskReplayExact':True,'patches':records,'internalEvidence':qa,'internalEvidenceUnchangedCount':66,'tenJambEvidenceExact':True,'wholeTileInternalReady':False,'formalAccepted':False,'rootLocalVisualReview':'Subagent viewed all ten native jamb/trim evidence images; parent review pending before adoption.','remainingIssue':'Brown upright farther right outside x1022 still has a tone seam at global y36864; unrelated failures retain prior status.','actualModel':None,'actualQuality':None,'noResampling':True,'noBlur':True,'noBlend':True,'noWarp':True}
 return report,before,selections,assemblies,all_sources

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--output',default=str(Q/'jamb-v1-surface-v2-independent-replay-20261016.json'));args=parser.parse_args()
 report,*_=verify_current();new_json(Path(args.output),report)
 print(json.dumps({'report':args.output,'status':report['status'],'internalEvidenceUnchangedCount':66,'adoptionExecuted':False}))
