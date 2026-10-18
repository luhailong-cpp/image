exec((__import__('pathlib').Path(__file__).parent/'audit.py').read_text(encoding='utf-8').split('oldraw=')[0])
import numpy as np
j=read(OUT/'prepared.json');tm={t['tileId']:t for t in j['tiles']};mem={}
def image(p):
 p=norm(p)
 if p not in mem:mem[p]=Image.open(p).convert('RGB')
 return mem[p]
for tid in ['r07_c04']:
 t=tm[tid];im=Image.new('RGB',(4096,4096))
 for s in t['selectedSources']:
  assert s['dimensions']==[1254,1254]
  im.paste(image(s['path']).crop((115,115,1139,1139)),((s['subcolumn']-1)*1024,(s['subrow']-1)*1024))
 p=OUT/f'{tid}-native-core-hard-join-4096.png';im.save(p);t.update(file=norm(p),sha256=sha(p),dimensions=[4096,4096],diagnosticOnly=True)
 save('r07_c04-pixel-verification.json',{'path':norm(p),'sha256':t['sha256'],'mode':'16 native 1024 center-core exact paste; no resize, interpolation, feathering','nativeSources':t['selectedSources'],'selectedSourcePixels':16777216,'formalAccepted':False})
changed={(d['tileId'],d['subrow'],d['subcolumn']) for d in j['changedSelectedCores']};glob={};needs=set()
for t in j['tiles']:
 rr=int(t['tileId'][1:3]);cc=int(t['tileId'][5:7])
 for s in t['selectedSources']:
  key=((rr-1)*4+s['subrow']-1,(cc-1)*4+s['subcolumn']-1);glob[key]=(t,s)
  if (t['tileId'],s['subrow'],s['subcolumn']) in changed or t['candidateSourceChanged']:needs.add(key)
def core(t,s):
 if t.get('file'):
  x=(s['subcolumn']-1)*1024;y=(s['subrow']-1)*1024
  return image(t['file']).crop((x,y,x+1024,y+1024))
 return image(s['path']).crop((115,115,1139,1139))
pairs=set()
for k in needs:
 for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
  n=(k[0]+dr,k[1]+dc)
  if n in glob:pairs.add(tuple(sorted((k,n))))
edges=[]
for n,(ka,kb) in enumerate(sorted(pairs),1):
 ta,sa=glob[ka];tb,sb=glob[kb];a=core(ta,sa);b=core(tb,sb);axis='v' if ka[0]==kb[0] else 'h'
 im=Image.new('RGB',(256,1024) if axis=='v' else (1024,256))
 if axis=='v':im.paste(a.crop((896,0,1024,1024)),(0,0));im.paste(b.crop((0,0,128,1024)),(128,0));line=[kb[1]*1024,ka[0]*1024,kb[1]*1024,(ka[0]+1)*1024]
 else:im.paste(a.crop((0,896,1024,1024)),(0,0));im.paste(b.crop((0,0,1024,128)),(0,128));line=[ka[1]*1024,kb[0]*1024,(ka[1]+1)*1024,kb[0]*1024]
 name=f"{n:03}-{ta['tileId']}-s{sa['subrow']}{sa['subcolumn']}--{tb['tileId']}-s{sb['subrow']}{sb['subcolumn']}";p=OUT/'edges'/f'{name}.png';p.parent.mkdir(exist_ok=True);im.save(p)
 edges.append({'id':name,'path':norm(p),'axis':axis,'tiles':[ta['tileId'],tb['tileId']],'globalSeamLine':line,'sourceA':sa,'sourceB':sb,'candidateA':ta.get('file'),'candidateB':tb.get('file'),'status':'pending_visual_review','actuallyViewed':False})
boards=[]
for axis in ['v','h']:
 es=[e for e in edges if e['axis']==axis]
 for st in range(0,len(es),8):
  im=Image.new('RGB',(2048,1024),(40,40,40));part=es[st:st+8]
  for k,e in enumerate(part):im.paste(image(e['path']),(k*256,0) if axis=='v' else ((k%2)*1024,(k//2)*256))
  p=OUT/f'board-{axis}-{st//8+1:02}-100pct.png';im.save(p);boards.append({'path':norm(p),'axis':axis,'edgeIds':[e['id'] for e in part],'noScaling':True})
crosses=[]
for tid in ['r07_c04','r12_c04']:
 im=image(tm[tid]['file']);board=Image.new('RGB',(1536,1536))
 for row,y in enumerate([1024,2048,3072]):
  for col,x in enumerate([1024,2048,3072]):board.paste(im.crop((x-256,y-256,x+256,y+256)),(col*512,row*512))
 p=OUT/f'{tid}-nine-junctions-100pct.png';board.save(p);crosses.append({'tileId':tid,'path':norm(p),'junctions':[[x,y] for y in [1024,2048,3072] for x in [1024,2048,3072]],'noScaling':True,'actuallyViewed':False})
# Current new 4096 uses a same-coordinate source-ID selection mask.
t=tm['r12_c04'];ca=t['candidateStatusRecord'];r=read(ca['sourceReport']);mask=np.asarray(image(ca['sourceIdMask'])) if False else np.asarray(Image.open(ca['sourceIdMask']));cand=np.asarray(image(t['file']));validation=[];covered=bad=0
for s in r['inputs']:
 sid=s['sourceId'];box=s['nativeGlobalBox'];tx=box[0]-12288;ty=box[1]-45056;x0=max(tx,0);y0=max(ty,0);x1=min(tx+1254,4096);y1=min(ty+1254,4096)
 if x0>=x1 or y0>=y1:continue
 src=np.asarray(image(s['path']));sel=mask[y0:y1,x0:x1]==sid;cut=src[y0-ty:y1-ty,x0-tx:x1-tx];n=int(sel.sum());b=int(np.count_nonzero(np.any(cand[y0:y1,x0:x1]!=cut,axis=2)&sel));covered+=n;bad+=b
 validation.append({'sourceId':sid,'path':norm(s['path']),'recordedSha256':s['sha256'],'sha256':sha(s['path']),'selectedPixels':n,'pixelMismatchCount':b})
save('r12_c04-pixel-verification.json',{'candidate':t['file'],'sha256':t['sha256'],'sourceIdMask':ca['sourceIdMask'],'sourceReport':ca['sourceReport'],'selectedPixelCount':covered,'pixelMismatchCount':bad,'allSourceHashesMatch':all(v['recordedSha256']==v['sha256'] for v in validation),'inputs':validation,'formalAccepted':False})
j.update(edges=edges,boards=boards,crossings=crosses)
save('prepared.json',j)
print(json.dumps({'edges':len(edges),'boards':boards,'crossings':crosses,'r12_c04PixelReplay':{'pixels':covered,'bad':bad,'inputs':len(validation)}},ensure_ascii=False,indent=2))
