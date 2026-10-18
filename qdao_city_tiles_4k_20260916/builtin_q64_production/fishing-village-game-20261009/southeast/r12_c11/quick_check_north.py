from pathlib import Path
import sys,json,hashlib
T=Path(__file__).resolve().parent;Z=T.parent;sys.path.insert(0,str(Z));from review_external_seams import Sources
pid,label=sys.argv[1:3];Q=T/'qa'/label;Q.mkdir(parents=True,exist_ok=False);S=Sources()
x=(int(T.name[5:7])-1)*4096+(int(pid[2])-1)*1024;y=(int(T.name[1:3])-1)*4096+(int(pid[1])-1)*1024
records=[]
for direction,box in {'west':[x-256,y,x+256,y+1024],'east':[x+768,y,x+1280,y+1024],'north':[x,y-256,x+1024,y+256],'south':[x,y+768,x+1024,y+1280]}.items():
 im,pieces,missing=S.extract(box)
 if missing:continue
 p=Q/f'{pid}-{direction}-100pct.png';im.save(p);records.append({'direction':direction,'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'globalBox':box,'sources':pieces,'resampling':False,'visualReview':'pending'})
(Q/'manifest.json').write_text(json.dumps({'patch':pid,'evidence':records,'formalAccepted':False},indent=2),encoding='utf-8');print(json.dumps({'directory':str(Q),'evidence':[r['file'] for r in records]}))
