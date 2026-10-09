from record import ROOT,sha,write,now
from PIL import Image
sources=[ROOT/f'p2{i}.png' for i in range(1,5)]
ims=[Image.open(p).convert('RGB') for p in sources]
qa=ROOT/'qa'; qa.mkdir(exist_ok=True)
def deriv(out,src,operation):
    im=Image.open(out)
    write(str(out)+'.generation.json',dict(file=str(out),sha256=sha(out),createdAt=now(),width=im.width,height=im.height,format='PNG',derivedFrom=[dict(file=str(p),sha256=sha(p),generationRecord=str(p)+'.generation.json') for p in src],operation=operation,formalTile=False,productionPixels=False))
row=Image.new('RGB',(4096,1024))
for i,im in enumerate(ims): row.paste(im.crop((115,115,1139,1139)),(i*1024,0))
out=qa/'row2-cores-4096x1024.png';row.save(out)
deriv(out,sources,dict(kind='native core concat for QA only',cropLTRB=[115,115,1139,1139],scale=1,blend=None,retouched=False))
out=qa/'row2-preview.png';row.resize((1536,384),Image.Resampling.LANCZOS).save(out)
deriv(out,sources,dict(kind='downsampled row QA preview',sourceCoreLTRB=[115,115,1139,1139],scale=0.375))
for i in range(3):
    seam=Image.new('RGB',(512,1254));seam.paste(ims[i].crop((883,0,1139,1254)),(0,0));seam.paste(ims[i+1].crop((115,0,371,1254)),(256,0))
    out=qa/f'seam-p2{i+1}-p2{i+2}-native.png';seam.save(out)
    deriv(out,sources[i:i+2],dict(kind='native hard-join seam inspection',leftCropLTRB=[883,0,1139,1254],rightCropLTRB=[115,0,371,1254],joinX=256,scale=1,blend=None,retouched=False))
print(str(qa))

for i in range(4):
    up=ROOT.parent/'row1'/f'p1{i+1}.png'
    if up.exists():
        ui=Image.open(up).convert('RGB'); seam=Image.new('RGB',(1254,512));seam.paste(ui.crop((0,883,1254,1139)),(0,0));seam.paste(ims[i].crop((0,115,1254,371)),(0,256))
        out=qa/f'north-p1{i+1}-p2{i+1}-native.png';seam.save(out)
        deriv(out,[up,sources[i]],dict(kind='native hard-join north seam inspection',upperCropLTRB=[0,883,1254,1139],lowerCropLTRB=[0,115,1254,371],joinY=256,scale=1,blend=None,retouched=False))
