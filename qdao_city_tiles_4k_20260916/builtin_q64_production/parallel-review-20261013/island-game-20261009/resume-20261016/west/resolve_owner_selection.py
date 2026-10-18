exec((__import__('pathlib').Path(__file__).parent/'audit.py').read_text(encoding='utf-8').split('oldraw=')[0])
import numpy as np
j=read(OUT/'prepared.json');save('prepared-index-baseline.json',j);tm={t['tileId']:t for t in j['tiles']}
nw=read(OUT/'snapshots/northwest/current-adopted-20261012.json');west=read(OUT/'snapshots/northwest/west-current-selection-20261012.json');right=read(OUT/'snapshots/northwest/right-current-selection-20261012.json')
resolved=[];before={t['tileId']:dict(t) for t in j['tiles']};diffs={}
for tid,own in [('r05_c02',west['currentTile']),('r07_c04',right['tiles']['r07_c04'])]:
 t=tm[tid];p=norm(own['candidate']['path']);h=sha(p);assert h==own['candidate']['sha256']
 old=Image.open(t['file']).convert('RGB');new=Image.open(p).convert('RGB');delta=np.any(np.asarray(old)!=np.asarray(new),axis=2);ys,xs=np.nonzero(delta);bbox=[int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1)] if len(xs) else None
 diffs[tid]=delta
 t.update(file=p,sha256=h,dimensions=list(new.size),adopted=True,diagnosticOnly=False,candidateSourceChanged=True,priorEvidenceReusable=False,candidateStatusRecord=own,adoptionAuthority='explicit frozen owner selection; aggregate current-adopted index disagrees')
 resolved.append({'tileId':tid,'indexFile':before[tid]['file'],'resolvedFile':p,'resolvedSha256':h,'changedPixelCount':int(delta.sum()),'differenceBBox':bbox,'ownerManifest':norm(OUT/'snapshots/northwest'/('west-current-selection-20261012.json' if tid=='r05_c02' else 'right-current-selection-20261012.json')),'basis':'Explicit owner-selected candidate, not newest-file inference. Aggregate index mismatch retained for coordinator.'})
save('selection-authority-resolution.json',resolved)
glob={};needs=set()
for t in j['tiles']:
 rr=int(t['tileId'][1:3]);cc=int(t['tileId'][5:7])
 for s in t['selectedSources']:
  k=((rr-1)*4+s['subrow']-1,(cc-1)*4+s['subcolumn']-1);glob[k]=(t,s)
  if t['tileId'] in diffs:needs.add(k)
def core(t,s,prior=False):
 z=before[t['tileId']] if prior else t
 if z.get('file'):
  x=(s['subcolumn']-1)*1024;y=(s['subrow']-1)*1024
  with Image.open(z['file']) as im:return im.convert('RGB').crop((x,y,x+1024,y+1024))
 with Image.open(s['path']) as im:return im.convert('RGB').crop((115,115,1139,1139))
def crop(ka,kb,prior=False):
 ta,sa=glob[ka];tb,sb=glob[kb];a=core(ta,sa,prior);b=core(tb,sb,prior);axis='v' if ka[0]==kb[0] else 'h';im=Image.new('RGB',(256,1024) if axis=='v' else (1024,256))
 if axis=='v':im.paste(a.crop((896,0,1024,1024)),(0,0));im.paste(b.crop((0,0,128,1024)),(128,0))
 else:im.paste(a.crop((0,896,1024,1024)),(0,0));im.paste(b.crop((0,0,1024,128)),(0,128))
 return im,axis
pairs=set()
for k in needs:
 for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
  n=(k[0]+dr,k[1]+dc)
  if n in glob:pairs.add(tuple(sorted((k,n))))
edges=[]
for ix,(ka,kb) in enumerate(sorted(pairs),1):
 a,axis=crop(ka,kb);old,_=crop(ka,kb,True);eq=a.tobytes()==old.tobytes();ta,sa=glob[ka];tb,sb=glob[kb];name=f"owner-{ix:03}-{ta['tileId']}-s{sa['subrow']}{sa['subcolumn']}--{tb['tileId']}-s{sb['subrow']}{sb['subcolumn']}";p=OUT/'owner-delta'/f'{name}.png'
 p.parent.mkdir(exist_ok=True)
 if not eq:a.save(p)
 edges.append({'id':name,'path':norm(p) if not eq else None,'axis':axis,'tiles':[ta['tileId'],tb['tileId']],'sourceA':sa,'sourceB':sb,'currentCandidateA':ta['file'],'currentCandidateB':tb['file'],'baselineCandidateA':before[ta['tileId']]['file'],'baselineCandidateB':before[tb['tileId']]['file'],'identicalToPriorReviewedPixels':eq,'status':'reuse_prior_pass_or_pending_status' if eq else 'pending_visual_review','actuallyViewed':False})
boards=[]
for axis in ['v','h']:
 es=[e for e in edges if e['axis']==axis and not e['identicalToPriorReviewedPixels']]
 for st in range(0,len(es),8):
  im=Image.new('RGB',(2048,1024),(40,40,40));part=es[st:st+8]
  for k,e in enumerate(part):
   with Image.open(e['path']) as q:im.paste(q,(k*256,0) if axis=='v' else ((k%2)*1024,(k//2)*256))
  p=OUT/f'owner-delta-board-{axis}-{st//8+1:02}-100pct.png';im.save(p);boards.append({'path':norm(p),'axis':axis,'edgeIds':[e['id'] for e in part],'noScaling':True})
cross=[]
for tid in diffs:
 with Image.open(tm[tid]['file']) as im:
  board=Image.new('RGB',(1536,1536))
  for row,y in enumerate([1024,2048,3072]):
   for col,x in enumerate([1024,2048,3072]):board.paste(im.crop((x-256,y-256,x+256,y+256)),(col*512,row*512))
 p=OUT/f'{tid}-owner-current-nine-junctions-100pct.png';board.save(p);cross.append({'tileId':tid,'path':norm(p),'noScaling':True,'actuallyViewed':False})
j.update(ownerSelectionResolution=resolved,ownerDeltaEdges=edges,ownerDeltaBoards=boards,ownerDeltaCrossings=cross)
j['totals']['adopted4kCount']=sum(t['adopted'] for t in j['tiles'])
save('prepared.json',j)
print(json.dumps({'resolved':resolved,'changedEdges':sum(not e['identicalToPriorReviewedPixels'] for e in edges),'reusableEdges':sum(e['identicalToPriorReviewedPixels'] for e in edges),'boards':boards,'crossings':cross},ensure_ascii=False,indent=2))
