import argparse, json, hashlib, shutil, datetime, struct
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
REPO=ROOT.parents[3]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def safe(rel):
 p=(ROOT/rel).resolve()
 if not p.is_relative_to(ROOT): raise ValueError('outside character write scope')
 return p
def register(a):
 src=Path(a.source); dest=safe('generation/'+a.direction+'/'+a.frame+'-v'+a.version+'.png')
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists(): raise ValueError('refuse overwrite')
 shutil.copyfile(src,dest)
 im=Image.open(dest); im.load()
 alpha=im.getchannel('A') if im.mode=='RGBA' else None
 info={'width':im.width,'height':im.height,'mode':im.mode,'format':im.format,'alphaExtrema':alpha.getextrema() if alpha else None,'bboxAlphaGt8':alpha.point(lambda n:255 if n>8 else 0).getbbox() if alpha else None}
 req=dest.with_suffix('.request.json'); reqdata=json.loads(req.read_text(encoding='utf-8'))
 refs=[{'path':p,'sha256':sha(p),'role':('character identity / camera' if i<2 else 'approved designs painting style')} for i,p in enumerate(reqdata['referenced_image_paths'])]
 rec={'file':dest.relative_to(ROOT).as_posix(),'sha256':sha(dest),'generatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'timestampMeaning':'local receipt registration time; exact tool completion timestamp not exposed','native':info,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((REPO/'config/image-generation.json').read_text(encoding='utf-8')),'submittedParameters':{**reqdata,'model':None,'quality':None},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host managed. Tool exposes no model/quality selectors and returned neither actual model nor actual quality.','evidence':{'hostFile':str(src),'outputHint':a.hint,'request':req.relative_to(ROOT).as_posix()},'prompt':dest.with_suffix('.prompt.txt').relative_to(ROOT).as_posix(),'references':refs,'nativeHd':min(im.size)>=1024,'status':'pending_visual_review'}
 dump(Path(str(dest)+'.generation.json'),rec)
 print(json.dumps({'file':str(dest),'sha256':rec['sha256'],**info}))
def inspect(a):
 im=Image.open(a.source); im.load(); print(json.dumps({'size':im.size,'mode':im.mode,'bbox':im.getbbox(),'alpha':im.getchannel('A').getextrema() if im.mode=='RGBA' else None}))
p=argparse.ArgumentParser(); s=p.add_subparsers(dest='command',required=True)
r=s.add_parser('register');r.add_argument('source');r.add_argument('direction');r.add_argument('frame');r.add_argument('--version',default='1');r.add_argument('--hint',default='');r.set_defaults(fn=register)
r=s.add_parser('inspect');r.add_argument('source');r.set_defaults(fn=inspect)
a=p.parse_args();a.fn(a)

