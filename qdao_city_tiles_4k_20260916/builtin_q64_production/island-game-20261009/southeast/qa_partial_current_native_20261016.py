from workflow import *
from PIL import Image
import sys
tid,rev,pairtext=sys.argv[1:]
q=ROOT/'qa'/f'{tid}-quick-{rev}';q.mkdir(exist_ok=False);p=read(ROOT/f'progress-{tid}.json');vv=p['workingVersions']
def path(k):return ROOT/'native'/(f'{tid}_p{k}_{vv[k]}.png' if len(k)==2 else k+'.png')
records=[]
for pair in pairtext.split(','):
 ka,kb=pair.split(':');aa,bb=path(ka),path(kb);ra=read(Path(str(aa)+'.generation.json'));rb=read(Path(str(bb)+'.generation.json'));ba=ra['coordinate']['nativeGlobalBox'];bbx=rb['coordinate']['nativeGlobalBox'];delta=(bbx[0]-ba[0],bbx[1]-ba[1]);assert delta in [(1024,0),(0,1024)],delta
 a=Image.open(aa).convert('RGB').crop((115,115,1139,1139));b=Image.open(bb).convert('RGB').crop((115,115,1139,1139))
 if delta==(1024,0):im=Image.new('RGB',(512,1024));im.paste(a.crop((768,0,1024,1024)),(0,0));im.paste(b.crop((0,0,256,1024)),(256,0))
 else:im=Image.new('RGB',(1024,512));im.paste(a.crop((0,768,1024,1024)),(0,0));im.paste(b.crop((0,0,1024,256)),(0,256))
 f=q/(pair.replace(':','-')+'.png');im.save(f);records.append({'id':pair,'file':str(f),'sha256':sha(f),'inputs':[{'file':str(x),'sha256':sha(x)} for x in [aa,bb]],'status':'pending_visual'})
write(q/'manifest.json',{'tile':tid,'workingVersions':vv,'entries':records,'fullCandidate':False,'operation':'exact native 1024 core crops and hard paste; no resampling'})
print(q)
