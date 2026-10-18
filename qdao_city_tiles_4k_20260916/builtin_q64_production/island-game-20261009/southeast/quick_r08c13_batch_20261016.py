from workflow import *
from PIL import Image
import sys
rev=sys.argv[1]
q=ROOT/'qa'/f'r08_c13-quick-{rev}';q.mkdir(exist_ok=False)
versions={'11':'v02','12':'v01','14':'v01','21':'v01','31':'v01','34':'v02','41':'v01','42':'v02','44':'v01'}
def np(rc):return ROOT/'native'/f'r08_c13_p{rc}_{versions[rc]}.png'
pairs=[('11-12',np('11'),np('12'),'h'),('11-21',np('11'),np('21'),'v'),('21-31',np('21'),np('31'),'v'),('31-41',np('31'),np('41'),'v'),('34-44',np('34'),np('44'),'v'),('41-42',np('41'),np('42'),'h'),('42-S',np('42'),ROOT/'native'/'r09_c13_p12_v01.png','v')]
records=[]
for name,aa,bb,d in pairs:
 a=Image.open(aa).convert('RGB').crop((115,115,1139,1139));b=Image.open(bb).convert('RGB').crop((115,115,1139,1139))
 if d=='h':
  im=Image.new('RGB',(512,1024));im.paste(a.crop((768,0,1024,1024)),(0,0));im.paste(b.crop((0,0,256,1024)),(256,0))
 else:
  im=Image.new('RGB',(1024,512));im.paste(a.crop((0,768,1024,1024)),(0,0));im.paste(b.crop((0,0,1024,256)),(0,256))
 f=q/f'{name}.png';im.save(f);records.append({'id':name,'file':str(f),'sha256':sha(f),'inputs':[{'file':str(x),'sha256':sha(x)} for x in [aa,bb]],'status':'pending_visual'})
for rc in ['11','21','31']:
 w=ROOT/'tiles'/'r08_c12.candidate-v15.png';a=Image.open(w).convert('RGB');y=(int(rc[0])-1)*1024;b=Image.open(np(rc)).convert('RGB').crop((115,115,1139,1139));im=Image.new('RGB',(512,1024));im.paste(a.crop((3840,y,4096,y+1024)),(0,0));im.paste(b.crop((0,0,256,1024)),(256,0));f=q/f'{rc}-W-actual.png';im.save(f);records.append({'id':rc+'-W-actual','file':str(f),'sha256':sha(f),'inputs':[{'file':str(x),'sha256':sha(x)} for x in [w,np(rc)]],'status':'pending_visual'})
write(q/'manifest.json',{'tile':'r08_c13','workingVersions':versions,'entries':records,'fullCandidate':False,'operation':'exact native 1024 core crops and hard paste; no resampling'})
print(q)
