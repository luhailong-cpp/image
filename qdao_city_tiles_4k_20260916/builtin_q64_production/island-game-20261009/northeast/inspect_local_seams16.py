from native_work import *
import sys
which=sys.argv[1];ident='r03_c09_cross_local_seams16_'+which+'_v1'
out=ZONE/'qa/local-seams16-20261016'/which;out.mkdir(exist_ok=True)
source=ZONE/'native'/f'{ident}.png';guide=ZONE/'guides'/f'{ident}.png'
new=Image.open(source).convert('RGB');base=Image.open(guide).convert('RGB');assert new.size==(1254,1254)
crop=[500,360,850,1060] if which=='top' else [430,140,830,980]
trial=base.copy();trial.paste(new.crop(crop),crop[:2]);trial.save(out/'trial-native.png')
sources=[]
for name,box in [('left',[crop[0]-100,crop[1]-80,crop[0]+100,crop[3]+80]),('right',[crop[2]-100,crop[1]-80,crop[2]+100,crop[3]+80]),('top',[crop[0]-100,crop[1]-100,crop[2]+100,crop[1]+100]),('bottom',[crop[0]-100,crop[3]-100,crop[2]+100,crop[3]+100]),('center',[430,270,900,1100])]:
    p=out/(name+'-100pct.png');trial.crop(box).save(p);sources.append({'file':p.as_posix(),'sha256':sha(p),'crop':box,'status':'pending_visual_review'})
write(out/'inspection.json',{'id':ident,'source':source.as_posix(),'sha256':sha(source),'sourceGuideSha256':sha(guide),'proposedCoreCrop':crop,'nativeWorldBox':patch(ident)['nativeWorldBox'],'trial':(out/'trial-native.png').as_posix(),'trialSha256':sha(out/'trial-native.png'),'inspections':sources,'status':'unreviewed','formalAccepted':False,'scale':1,'blend':False})
print(json.dumps({'out':str(out),'sourceSha256':sha(source),'crop':crop}))
