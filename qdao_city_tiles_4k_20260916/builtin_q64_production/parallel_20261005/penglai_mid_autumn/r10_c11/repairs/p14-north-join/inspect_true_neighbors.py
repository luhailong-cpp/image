from prepare_repair import *
v=HERE/"v9";sources={};refs={}
for op in read(TILE/"native/p14.request.json")["contextRegions"]:
 sources[op["source"]]=Image.open(op["file"]).convert("RGB");refs[op["source"]]=dict(file=op["file"],sha256=op["sha256"])
im=Image.new("RGB",(512,1024));im.paste(sources["northeast"].crop((0,3584,512,4096)),(0,0));im.paste(sources["east"].crop((0,0,512,512)),(0,512));path=v/"qa-real-ne-e-only.png";im.save(path)
write(str(path)+".generation.json",dict(**ref(path),operation="Exact true-neighbor-only crop/paste. Upper512x512 is r09_c12 southwest corner; lower512x512 is r10_c12 northwest corner. Physical old-neighbor join at y512. No current p14 pixels.",sources=[refs["northeast"],refs["east"]],nativeScale=1,actuallyViewed=False))
im=Image.new("RGB",(640,512));im.paste(sources["north"].crop((3776,3584,4096,4096)),(0,0));im.paste(sources["northeast"].crop((0,3584,320,4096)),(320,0));path=v/"qa-real-n-ne-only.png";im.save(path)
write(str(path)+".generation.json",dict(**ref(path),operation="Exact true-neighbor-only crop/paste: r09_c11 east320 and r09_c12 west320, bottom512rows. Join x320. No current p14 pixels.",sources=[refs["north"],refs["northeast"]],nativeScale=1,actuallyViewed=False))
print("Native actual-neighbor-only QA prepared")

