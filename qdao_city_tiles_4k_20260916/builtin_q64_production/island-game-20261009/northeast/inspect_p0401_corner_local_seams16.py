from native_work import *
q=ZONE/'qa/local-seams16-p0401-corner-20261016';q.mkdir(exist_ok=True)
base=ZONE/'native/r03_c09_p04_01_v2.png';donor=ZONE/'native/r03_c09_p04_01.png';neighbor=ZONE/'native/r03_c09_p04_02.png'
im=Image.open(base).convert('RGB');old=Image.open(donor).convert('RGB');right=Image.open(neighbor).convert('RGB')
crop=[900,750,1139,1139];trial=im.copy();trial.paste(old.crop(crop),crop[:2]);f=q/'trial1-native.png';assert not f.exists();trial.save(f)
join=Image.new('RGB',(512,1024));join.paste(trial.crop([883,115,1139,1139]),(0,0));join.paste(right.crop([115,115,371,1139]),(256,0));jf=q/'trial1-right-join-100pct.png';join.save(jf)
specs=[('left',[800,650,1000,1139]),('top',[800,650,1239,850]),('top-left',[800,650,1000,850]),('top-right',[1039,650,1239,850]),('repaired-region',[850,750,1254,1139])];evidence=[]
for name,box in specs:
    path=q/('trial1-'+name+'-100pct.png');trial.crop(box).save(path);evidence.append({'file':path.as_posix(),'sha256':sha(path),'crop':box,'status':'pending_visual_review'})
native=patch('r03_c09_p04_01')['nativeWorldBox'];core=[native[0]+crop[0],native[1]+crop[1],native[0]+crop[2],native[1]+crop[3]]
write(q/'inspection.json',{'task':'oldv1 lower-right exact crop on selectedv2; no AI','base':{'file':base.as_posix(),'sha256':sha(base)},'source':{'file':donor.as_posix(),'sha256':sha(donor),'nativeWorldBox':native},'neighbor':{'file':neighbor.as_posix(),'sha256':sha(neighbor)},'sourceCrop':crop,'targetSourcePaste':crop[:2],'tileLocalPaste':[crop[0]-115,3072+crop[1]-115],'overlayWorldBox':core,'trial':f.as_posix(),'trialSha256':sha(f),'rightJoin':{'file':jf.as_posix(),'sha256':sha(jf)},'evidence':evidence,'bottom':'pending_future_down_neighbor; not accepted from local halo','status':'pending_visual_review','selectionWritten':False,'progressWritten':False,'newImageCalls':0,'resized':False,'blending':False,'formalAccepted':False})
print(json.dumps({'trial':str(f),'sourceCrop':crop,'tileLocalPaste':[crop[0]-115,3072+crop[1]-115]}))
