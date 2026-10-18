from produce import *
name=sys.argv[1];outversion=sys.argv[2]
req=json.loads((ROOT/'requests'/f'{name}.json').read_text());p=ROOT/'seam-native'/f'{name}.png';im=Image.open(p);assert im.size==(1254,1254)
base=Image.open(req['source']);x,y,_,_=req['tileCoreBox'];base.paste(im.crop((115,115,1139,1139)),(x,y))
out=ROOT/'candidates'/f"{req['tile']}-4096-{outversion}.png";assert not out.exists();base.save(out);base.resize((1254,1254)).save(ROOT/'qa'/f"{req['tile']}-preview-{outversion}.png")
write(ROOT/'seam-native'/f'{name}.json',{**req,'file':p.as_posix(),'sha256':sha(p),'actualModel':None,'nativePixelsResampled':False,'status':'candidate_pending_perimeter_qa','receipt':str(ROOT/'qa'/f'{name}.receipt.json')})
write(out.with_suffix('.manifest.json'),{'file':out.as_posix(),'sha256':sha(out),'dimensions':[4096,4096],'baseSource':req['source'],'baseSha256':req['sourceSha256'],'nativeOverlay':p.as_posix(),'overlaySha256':sha(p),'sourceCrop':[115,115,1139,1139],'destinationCore':req['tileCoreBox'],'method':'unaltered native pixel hard crop/paste; no resizing or feathering','status':'pending_internal_qa'})
