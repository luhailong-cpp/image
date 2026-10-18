from pathlib import Path
from PIL import Image
import json,hashlib,shutil,numpy as np
T=Path(__file__).resolve().parent;Q=T/'qa/joint-20261016-v1';O=T/'processed/stone-joint-20261016-v1';O.mkdir(parents=True,exist_ok=True)
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
write=lambda p,d:Path(p).write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding='utf-8')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
meta=read(Q/'stone-joint-input-1254.png.derivation.json');receipt=read(T/'stone-joint-v1-20261016.receipt.json')
raw=Path(receipt['sourcePath']);saved=O/'stone-joint-v1-raw.png';assert not saved.exists();shutil.copy2(raw,saved)
edited=Image.open(saved).convert('RGB');assert edited.size==(1254,1254)
sel=read(T/'selected-patches.json');backup=read(T/'selected-patches.json');records=[];original=Image.new('RGB',(4096,4096));result=Image.new('RGB',(4096,4096))
fx,fy=meta['tileBox'][:2];adopt=[fx+115,fy+115,fx+1139,fy+1139]
for pid,rel in list(sel['patches'].items()):
 src=T/rel;im=Image.open(src).convert('RGB');a=np.array(im);r,c=int(pid[1])-1,int(pid[2])-1;tx,ty=c*1024,r*1024
 original.paste(im.crop((115,115,1139,1139)),(tx,ty))
 l,t=max(tx,adopt[0]),max(ty,adopt[1]);rr,b=min(tx+1024,adopt[2]),min(ty+1024,adopt[3])
 if l<rr and t<b:
  db=[l-tx+115,t-ty+115,rr-tx+115,b-ty+115];sb=[l-fx,t-fy,rr-fx,b-fy]
  im.paste(edited.crop(sb),tuple(db[:2]));out=O/f'{pid}-stone-joint-v1.png';im.save(out);outa=np.array(im);mask=np.zeros(a.shape[:2],bool);mask[db[1]:db[3],db[0]:db[2]]=True
  assert np.array_equal(a[~mask],outa[~mask]);assert np.array_equal(outa[db[1]:db[3],db[0]:db[2]],np.array(edited.crop(sb)))
  rec=dict(patch=pid,file=str(out),sha256=sha(out),base=dict(file=str(src),sha256=sha(src)),newNativeSource=dict(file=str(saved),sha256=sha(saved),sourceCrop=sb),destination=db,operation='Binary exact coordinate native substitution, no scaling, blending, color change or geometry transform',outsideAdoptedPixelsExactlyUnchanged=True,exactNativeSourceReplay=True,formalAccepted=False)
  write(str(out)+'.derivation.json',rec);records.append(rec);sel['patches'][pid]=str(out.relative_to(T))
 result.paste(im.crop((115,115,1139,1139)),(tx,ty))
sel.update(internalReady=False,formalAccepted=False,status='joint_candidate_pending_native_perimeter_QA')
write(Q/'joint-candidate-selected.json',sel);write(Q/'base-selected-snapshot.json',backup)
boxes={'left':[adopt[0]-128,adopt[1],adopt[0]+128,adopt[3]],'right':[adopt[2]-128,adopt[1],adopt[2]+128,adopt[3]],'top':[adopt[0],adopt[1]-128,adopt[2],adopt[1]+128],'bottom':[adopt[0],adopt[3]-128,adopt[2],adopt[3]+128],'center':[397,1721,1651,2975]}
qa=[]
for name,box in boxes.items():
 p=Q/f'{name}-after-native.png';result.crop(box).save(p);qa.append(dict(file=str(p),sha256=sha(p),tileBox=box,visualReview='pending'))
report=dict(tile='r09_c10',source=str(saved),sha256=sha(saved),inputFrame=meta['tileBox'],adoptedTileBox=adopt,sourceCrop=[115,115,1139,1139],records=records,evidence=qa,canonicalSelectionChanged=False,internalReady=False,formalAccepted=False)
write(Q/'joint-candidate-report.json',report)
print(json.dumps(dict(changedPatches=[x['patch'] for x in records],report=str(Q/'joint-candidate-report.json'))))
