from native_work import *
import sys
which=sys.argv[1];ident='r03_c09_cross_local_seams16_'+which+'_v1'
out=ZONE/'qa/local-seams16-20261016'/(which+'-full');out.mkdir(exist_ok=True)
source=ZONE/'native'/f'{ident}.png';guide=ZONE/'guides'/f'{ident}.png'
new=Image.open(source).convert('RGB');base=Image.open(guide).convert('RGB');assert new.size==(1254,1254)
crop=[115,115,1139,1139]
trial=base.copy();trial.paste(new.crop(crop),crop[:2]);trial.save(out/'trial-native.png');sources=[]
for name,box in [('left',[0,0,230,1254]),('right',[1024,0,1254,1254]),('top',[0,0,1254,230]),('bottom',[0,1024,1254,1254]),('center',[397,0,857,1254]),('ul',[0,0,371,371]),('ur',[883,0,1254,371]),('ll',[0,883,371,1254]),('lr',[883,883,1254,1254])]:
    p=out/(name+'-100pct.png');trial.crop(box).save(p);sources.append({'file':p.as_posix(),'sha256':sha(p),'crop':box,'status':'pending_visual_review'})
p=patch(ident);native=p['nativeWorldBox'];paste=[native[0]+crop[0]-32768,native[1]+crop[1]-8192]
write(out/'inspection.json',{'id':ident,'source':source.as_posix(),'sha256':sha(source),'sourceGuideSha256':sha(guide),'coreCrop':crop,'tileLocalPaste':paste,'nativeWorldBox':native,'trial':(out/'trial-native.png').as_posix(),'trialSha256':sha(out/'trial-native.png'),'inspections':sources,'status':'unreviewed','formalAccepted':False,'scale':1,'blend':False})
print(json.dumps({'out':str(out),'sourceSha256':sha(source),'crop':crop,'tileLocalPaste':paste}))
