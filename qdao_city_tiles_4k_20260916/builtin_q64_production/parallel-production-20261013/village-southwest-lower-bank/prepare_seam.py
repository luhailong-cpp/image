from produce import *
tile=sys.argv[1];version=sys.argv[2];sx=int(sys.argv[3]);sy=int(sys.argv[4]);name=sys.argv[5]
source=ROOT/'candidates'/f'{tile}-4096-{version}.png'
im=Image.open(source);box=[sx-115,sy-115,sx+1139,sy+1139];assert min(box)>=0 and max(box)<=4096
p=ROOT/'guides'/f'{name}-native-target.png';im.crop(box).save(p)
write(ROOT/'requests'/f'{name}.json',{'tile':tile,'source':source.as_posix(),'sourceSha256':sha(source),'reference':p.as_posix(),'referenceSha256':sha(p),'tileContextBox':box,'tileCoreBox':[sx,sy,sx+1024,sy+1024],'coreCrop':[115,115,1139,1139],'dimensions':[1254,1254],'kind':'native_seam_repair','actualModel':None})
print(p)
