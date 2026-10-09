from prepare_repair import *
d=HERE/"geometry-combined-v1";proposal=d/"proposal-p14.png";im=Image.open(proposal)
for name,box in [("qa-old-y742",(0,652,1254,842)),("qa-old-ne-e-only",(1139,0,1254,360))]:
 p=d/(name+".png");im.crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(proposal)],operation=dict(cropLTRB=box),nativeScale=1,actuallyViewed=False))
print(str(d))

