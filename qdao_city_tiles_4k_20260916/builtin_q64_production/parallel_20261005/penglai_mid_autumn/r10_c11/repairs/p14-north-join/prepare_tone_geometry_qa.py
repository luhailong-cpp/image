from prepare_repair import *
D=HERE/"tone-diagnostic-separated-v2/separate-edges256"
proposal=Image.open(D/"proposal-native-frame.png").convert("RGB")
for name,box in [("qa-north-wave-endpoint.png",[420,65,620,175]),("qa-east-wave-endpoint.png",[1030,620,1254,800])]:
 p=D/name;proposal.crop(box).save(p);write(str(p)+".generation.json",dict(**ref(p),derivedFrom=[ref(D/"proposal-native-frame.png")],operation={"cropLTRB":box},nativeScale=1,actuallyViewed=False))
print(json.dumps(read(D/"diagnostic.json"),ensure_ascii=False))

