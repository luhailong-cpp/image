from native_work import *
ident='r03_c09_cross_local_seams16_foliage_v1';q=ZONE/'qa/local-seams16-foliage-20261016/foliage-only-crop';q.mkdir(exist_ok=True)
src=ZONE/'native'/f'{ident}.png';g=ZONE/'guides'/f'{ident}.png';base=Image.open(g).convert('RGB');new=Image.open(src).convert('RGB')
crop=[400,350,800,1040];trial=base.copy();trial.paste(new.crop(crop),crop[:2]);out=q/'trial-native.png';trial.save(out)
specs=[('left',[300,250,500,1140]),('right',[700,250,900,1140]),('top',[300,250,900,450]),('bottom',[300,940,900,1140]),('center',[480,300,800,1090]),('ul',[300,250,500,450]),('ur',[700,250,900,450]),('ll',[300,940,500,1140]),('lr',[700,940,900,1140])];evidence=[]
for name,box in specs:
    f=q/(name+'-100pct.png');trial.crop(box).save(f);evidence.append({'file':f.as_posix(),'sha256':sha(f),'crop':box,'status':'pending_visual_review'})
native=patch(ident)['nativeWorldBox'];core=[native[0]+crop[0],native[1]+crop[1],native[0]+crop[2],native[1]+crop[3]]
write(q/'inspection.json',{'id':ident,'source':src.as_posix(),'sha256':sha(src),'guide':g.as_posix(),'guideSha256':sha(g),'nativeWidth':1254,'nativeHeight':1254,'nativeWorldBox':native,'coreCrop':crop,'coreWorldBox':core,'tileLocalPaste':[core[0]-32768,core[1]-8192],'trial':out.as_posix(),'trialSha256':sha(out),'evidence':evidence,'status':'pending_visual_review','formalAccepted':False,'resized':False,'blending':False,'actualModel':None,'actualQuality':None})
print(json.dumps({'inspection':str(q/'inspection.json'),'crop':crop,'tileLocalPaste':[core[0]-32768,core[1]-8192]}))
