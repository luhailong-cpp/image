from worker import *
for tile,ver in [('r12_c13','v04'),('r12_c14','v03')]:
 t=B/tile;src=t/'qa'/('repair-candidate-'+ver+'.png');im=Image.open(src).convert('RGB');d=t/'qa'/('internal-audit-20261016-'+ver);d.mkdir(exist_ok=True);items=[]
 for axis in ['h','v']:
  for n in range(1,4):
   p=d/(axis+str(n)+'.png'); sheet=Image.new('RGB',(1024,1024)); boxes=[]
   for s in range(4):
    box=(s*1024,n*1024-128,(s+1)*1024,n*1024+128) if axis=='h' else (n*1024-128,s*1024,n*1024+128,(s+1)*1024)
    patch=im.crop(box);sheet.paste(patch,(0,s*256) if axis=='h' else (s*256,0));boxes.append(box)
   if not p.exists():sheet.save(p)
   items.append({'path':str(p),'sha256':sha(p),'axis':axis,'boundary':n*1024,'sourceBoxes':boxes,'noResize':True})
 write(d/'manifest.json',{'source':str(src),'sourceSha256':sha(src),'size':list(im.size),'sheets':items,'accepted':False,'status':'await_visual_review'})
 print(d)
