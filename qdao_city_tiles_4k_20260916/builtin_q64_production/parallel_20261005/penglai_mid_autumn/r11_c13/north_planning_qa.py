from prepare_structure import *
src=Path(sys.argv[1]);tag=sys.argv[2]
ni=Image.open(N).convert('RGB');si=Image.open(src).convert('RGB');k=1254/S
for i in range(4):
    box=[(320+i*1024)*k,320*k,(320+(i+1)*1024)*k,640*k]
    im=Image.new('RGB',(1024,640));im.paste(ni.crop((i*1024,3776,(i+1)*1024,4096)),(0,0));im.paste(si.transform((1024,320),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC),(0,320))
    image_save(im,Q/tag/f'north-join-segment{i+1}.png',[N,src],dict(kind='actual native north vs planning at true scale, macro geometry QA only',seamY=320,northCropLTRB=[i*1024,3776,(i+1)*1024,4096],structureExtentLTRB=box,structureGlobalFrameXYWH=FRAME,notNativeSeamAcceptance=True))
print(Q/tag)
