from native_work import *
from PIL import ImageChops
import re
tile='r03_c09-native-v1-20261016';f=ZONE/'tiles'/f'{tile}.png';der=read(f.with_suffix('.png.derivation.json'));expected='69a5ce63ac62f03290cbc51ad4ff3dd21195fba4bf9091d96ac63d4dde5b9f2c'
assert sha(f)==expected==der['sha256'];im=Image.open(f).convert('RGB');assert im.size==(4096,4096)
rebuild=Image.new('RGB',im.size);sources=[]
for s in der['sources']:
    sf=Path(s['file']);assert sha(sf)==s['sha256'];part=Image.open(sf).convert('RGB');assert part.size==(1254,1254);rebuild.paste(part.crop(s['coreCrop']),s['tileLocalPaste']);sources.append({'id':s['id'],'hashValid':True,'size':[1254,1254]})
overlays=[]
for s in der['requiredOverlays']:
    sf=Path(s['source']);assert sha(sf)==s['sha256'];part=Image.open(sf).convert('RGB');rebuild.paste(part.crop(s['coreCrop']),s['tileLocalPaste']);overlays.append({'id':s['id'],'hashValid':True,'crop':s['coreCrop'],'paste':s['tileLocalPaste']})
assert ImageChops.difference(rebuild,im).getbbox() is None
q=ZONE/'qa'/f'{tile}-final';entries=[];sel=read(ZONE/'selection-r03_c09.json')
for p in sorted(q.glob('*.png')):
    small=Image.open(p).convert('RGB');w,h=small.size
    stem=p.stem.replace('-100pct','');bits=stem.split('-');kind=bits[0]
    if kind=='core':
        rr,cc=map(int,bits[1:]);box=[(cc-1)*1024,(rr-1)*1024,cc*1024,rr*1024];names=[sel['cores'][rr-1][cc-1]]
    elif kind=='cross':
        rr,cc=map(int,bits[1:]);box=[cc*1024-w//2,rr*1024-h//2,cc*1024+w//2,rr*1024+h//2];names=[]
    elif kind=='vertical':
        seam,seg=int(bits[1]),int(bits[3]);box=[seam*1024-w//2,(seg-1)*1024,seam*1024+w//2,seg*1024];names=[sel['cores'][seg-1][seam-1],sel['cores'][seg-1][seam]]
    else:
        seam,seg=int(bits[1]),int(bits[3]);box=[(seg-1)*1024,seam*1024-h//2,seg*1024,seam*1024+h//2];names=[sel['cores'][seam-1][seg-1],sel['cores'][seam][seg-1]]
    assert ImageChops.difference(small,im.crop(box)).getbbox() is None
    rec={'file':p.as_posix(),'sha256':sha(p),'name':p.name,'kind':kind,'candidateCrop':box,'size':[w,h],'exactPixelsVerified':True,'status':'pending_visual_review'}
    if len(names)==2:
        prev=ZONE/'qa'/('__'.join(names)+'.json')
        if prev.exists():
            old=read(prev);ev=old.get('inspectionEvidencePath');valid=True
            for k in ['a','b']:
                if k not in old or sha(old[k]['path'])!=old[k]['sha256']:valid=False
            identical=bool(ev and Path(ev).exists() and Image.open(ev).size==small.size and ImageChops.difference(Image.open(ev).convert('RGB'),small).getbbox() is None)
            rec['previousReview']={'path':prev.as_posix(),'status':old.get('status'),'hashesMatch':valid,'exactCropPixelIdentical':identical,'evidence':ev}
    entries.append(rec)
assert len(entries)==49
right=ZONE/'tiles/r03_c10-native-v2-20261013.png';rim=Image.open(right).convert('RGB');assert rim.size==(4096,4096);ext=ZONE/'qa'/f'{tile}-right-boundary';ext.mkdir(exist_ok=True);boundaries=[]
for n in range(4):
    plate=Image.new('RGB',(512,1024));plate.paste(im.crop([3840,n*1024,4096,(n+1)*1024]),(0,0));plate.paste(rim.crop([0,n*1024,256,(n+1)*1024]),(256,0));p=ext/f'right-{n+1}-100pct.png';plate.save(p);boundaries.append({'file':p.as_posix(),'sha256':sha(p),'segment':n+1,'neighbor':right.as_posix(),'neighborSha256':sha(right),'status':'pending_visual_review'})
report={'tileId':'r03_c09','candidate':f.as_posix(),'sha256':expected,'size':[4096,4096],'sources':sources,'overlays':overlays,'reconstructedPixelsMatch':True,'all49ExactPixelsVerified':True,'inspectionEntries':entries,'rightBoundary':boundaries,'createdAtUtc':now(),'reviewer':'/root/local_seams16','status':'mechanical_verified_visual_pending','selectionCoreAndOverlaySnapshot':{'cores':sel['cores'],'overlays':sel['overlays']}}
p=ZONE/'qa'/f'{tile}-local-seams16-verification.json';write(p,report)
print(json.dumps({'verification':p.as_posix(),'candidateHashVerified':True,'placementsVerified':True,'crops':len(entries),'previous':[{'name':e['name'],**e.get('previousReview',{})} for e in entries if 'previousReview' in e]},ensure_ascii=False))
