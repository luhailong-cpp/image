from native_work import *
q=ZONE/'qa/local-seams16-20261016'
mid=read(q/'middle/inspection.json');im=Image.open(mid['trial']);crop=mid['proposedCoreCrop']
for name,cx,cy in [('ul',crop[0],crop[1]),('ur',crop[2],crop[1]),('ll',crop[0],crop[3]),('lr',crop[2],crop[3])]:
    box=[cx-100,cy-100,cx+100,cy+100];f=q/'middle'/f'{name}-100pct.png';im.crop(box).save(f)
    mid['inspections'].append({'file':f.as_posix(),'sha256':sha(f),'crop':box,'status':'pending_visual_review'})
write(q/'middle/inspection.json',mid)
print(json.dumps({'cornersPrepared':True}))
