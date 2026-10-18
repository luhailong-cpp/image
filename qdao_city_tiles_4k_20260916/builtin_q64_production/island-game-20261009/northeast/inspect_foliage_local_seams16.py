from native_work import *
ident='r03_c09_cross_local_seams16_foliage_v1';q=ZONE/'qa/local-seams16-foliage-20261016'
src=ZONE/'native'/f'{ident}.png';g=ZONE/'guides'/f'{ident}.png';base=Image.open(g).convert('RGB');new=Image.open(src).convert('RGB');assert new.size==(1254,1254)
crop=[500,230,780,1040];trial=base.copy();trial.paste(new.crop(crop),crop[:2]);out=q/'trial-native.png';trial.save(out)
specs=[('left',[400,130,600,1140]),('right',[680,130,880,1140]),('top',[400,130,880,330]),('bottom',[400,940,880,1140]),('center',[480,130,800,1140]),('ul',[400,130,600,330]),('ur',[680,130,880,330]),('ll',[400,940,600,1140]),('lr',[680,940,880,1140])];evidence=[]
for name,box in specs:
    f=q/(name+'-100pct.png');trial.crop(box).save(f);evidence.append({'file':f.as_posix(),'sha256':sha(f),'crop':box,'status':'pending_visual_review'})
p=patch(ident);native=p['nativeWorldBox'];core=[native[0]+crop[0],native[1]+crop[1],native[0]+crop[2],native[1]+crop[3]]
write(q/'inspection.json',{'id':ident,'source':src.as_posix(),'sha256':sha(src),'guide':g.as_posix(),'guideSha256':sha(g),'nativeWidth':1254,'nativeHeight':1254,'nativeWorldBox':native,'coreCrop':crop,'coreWorldBox':core,'tileLocalPaste':[core[0]-32768,core[1]-8192],'trial':out.as_posix(),'trialSha256':sha(out),'evidence':evidence,'status':'pending_visual_review','formalAccepted':False,'resized':False,'blending':False,'actualModel':None,'actualQuality':None})
print(json.dumps({'inspection':str(q/'inspection.json'),'crop':crop,'tileLocalPaste':[core[0]-32768,core[1]-8192]}))
