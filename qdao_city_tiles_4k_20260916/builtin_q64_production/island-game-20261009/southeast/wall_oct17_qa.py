import os,sys
os.environ['ISLAND_PROGRESS_FILE']='progress-wall-oct16.json'
from workflow import *
pid,v=sys.argv[1:];tid=pid[:7];f=ROOT/'native'/f'{pid}_{v}.png';im=Image.open(f).convert('RGB');b=patch(pid)['coreGlobalBox'];sources=[]
if tid=='r11_c10':
 for nt,name in [('r10_c10','r10_c10.candidate-wall-oct17-v02.png'),('r11_c11','r11_c11.candidate-v02.png')]:
  r=int(nt[1:3]);c=int(nt[5:7]);nf=ROOT/'tiles'/name;sources.append((nf,[(c-1)*4096,(r-1)*4096,c*4096,r*4096],Image.open(nf).convert('RGB')))
for other in read(ROOT/'progress-wall-oct16.json')['selected'].values():
 nf=Path(other['file'])
 if not nf.name.startswith(tid+'_') or nf.name.startswith(pid+'_'):continue
 cb=read(Path(str(nf)+'.generation.json'))['coordinate']['coreGlobalBox'];sources.append((nf,cb,Image.open(nf).convert('RGB').crop((115,115,1139,1139))))
entries=[];q=ROOT/'qa'/'wall-oct17';q.mkdir(exist_ok=True)
for nf,nb,ni in sources:
 direction=None
 if nb[2]==b[0] and nb[1]<=b[1] and nb[3]>=b[3]:
  direction='W';a=ni.crop((nb[2]-nb[0]-256,b[1]-nb[1],nb[2]-nb[0],b[3]-nb[1]));z=im.crop((115,115,371,1139));e=Image.new('RGB',(512,1024));e.paste(a,(0,0));e.paste(z,(256,0))
 elif nb[0]==b[2] and nb[1]<=b[1] and nb[3]>=b[3]:
  direction='E';a=im.crop((883,115,1139,1139));z=ni.crop((0,b[1]-nb[1],256,b[3]-nb[1]));e=Image.new('RGB',(512,1024));e.paste(a,(0,0));e.paste(z,(256,0))
 elif nb[3]==b[1] and nb[0]<=b[0] and nb[2]>=b[2]:
  direction='N';a=ni.crop((b[0]-nb[0],nb[3]-nb[1]-256,b[2]-nb[0],nb[3]-nb[1]));z=im.crop((115,115,1139,371));e=Image.new('RGB',(1024,512));e.paste(a,(0,0));e.paste(z,(0,256))
 elif nb[1]==b[3] and nb[0]<=b[0] and nb[2]>=b[2]:
  direction='S';a=im.crop((115,883,1139,1139));z=ni.crop((b[0]-nb[0],0,b[2]-nb[0],256));e=Image.new('RGB',(1024,512));e.paste(a,(0,0));e.paste(z,(0,256))
 if direction:
  out=q/f'{pid}-{v}-{direction}.png';assert not out.exists();e.save(out);entries.append({'direction':direction,'file':str(out),'sha256':sha(out),'sources':[{'file':str(f),'sha256':sha(f)},{'file':str(nf),'sha256':sha(nf)}],'status':'pending_visual_review'})
write(q/f'{pid}-{v}-review.json',{'native':str(f),'sha256':sha(f),'edges':entries,'status':'pending_visual_review','actualModel':None,'formalAccepted':False});print(json.dumps(entries))
