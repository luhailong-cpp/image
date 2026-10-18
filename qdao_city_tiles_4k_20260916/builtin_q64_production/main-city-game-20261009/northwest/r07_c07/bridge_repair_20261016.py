from pathlib import Path
import json,sys,hashlib,shutil
from PIL import Image
T=Path(__file__).resolve().parent;R=T.parents[4]
P=T/'candidate/hard-native16-20261016-d2798e0634074d26/candidate.png'
W=T.parent/'r07_c06/candidate/r07_c06-candidate-native-roi-v10.png'
def sha(f):return hashlib.sha256(Path(f).read_bytes()).hexdigest()
def read(f):return json.loads(Path(f).read_text(encoding='utf-8-sig'))
def write(f,o):
 f.parent.mkdir(parents=True,exist_ok=True);assert not f.exists();f.write_text(json.dumps(o,ensure_ascii=False,indent=2),encoding='utf-8')
def rules():
 r=(R/'AGENTS.md').read_text(encoding='utf-8-sig');m=read(R/'docs/MAP_PARALLEL_SPLIT_20261013.json')
 assert T.name not in {v for b in m['batches'] if b['map']=='main-city-game-20261009' and b['status']=='allocated_root_reserved' for v in b['tiles']}
 return dict(agentsSha256=sha(R/'AGENTS.md'),splitSha256=sha(R/'docs/MAP_PARALLEL_SPLIT_20261013.json'),actuallyRead=True)
def prepare(name,y):
 d=T/'repairs'/name;d.mkdir(parents=True,exist_ok=False);im=Image.new('RGB',(1254,1254));a=Image.open(P).convert('RGB');w=Image.open(W).convert('RGB')
 im.paste(w.crop((3981,y-627,4096,y+627)),(0,0));im.paste(a.crop((0,y-627,1139,y+627)),(115,0));f=d/'input.png';im.save(f)
 write(d/'input.derivation.json',dict(file=str(f),sha256=sha(f),role='unscaled same-world native composite edit target',worldBox=[24576-115,24576+y-627,24576+1139,24576+y+627],tileLocalBox=[-115,y-627,1139,y+627],inputs=[dict(file=str(P),sha256=sha(P),sourceBox=[0,y-627,1139,y+627],targetBox=[115,0,1254,1254]),dict(file=str(W),sha256=sha(W),sourceBox=[3981,y-627,4096,y+627],targetBox=[0,0,115,1254])],resampled=False))
 print(str(f))
def request(name,scene):
 d=T/'repairs'/name;e=rules();prompt='Use case: precise-object-edit. Edit the single exact1254x1254 opaque native game-map image at its existing camera and world coordinates, no resize or reframing. It is a same-world crop spanning a tile seam at image y=627. '+scene+' Preserve all scene layout, objects, materials, decorative identity, and the crisp detailed Chinese Taoist chibi hand-painted natural daylight style. Outside the specified repair area keep the existing pixels visually unchanged. The left115columns are fixed neighboring artwork: do not change them. No text, new decorations, new props, blur, soft blending, filter or collage frame. Output one full native1254x1254 PNG.'
 local_y=read(d/'input.derivation.json')['tileLocalBox'][1]
 if local_y<0:prompt=prompt.replace('seam at image y=627','seam at image y='+str(-local_y))
 args=dict(prompt=prompt,referenced_image_paths=[str(d/'input.png')],transparent_background=False)
 write(d/'arguments.json',args);(d/'prompt.txt').write_text(prompt,encoding='utf-8')
 write(d/'request.json',dict(arguments=args,rules=e,reference=dict(file=str(d/'input.png'),sha256=sha(d/'input.png')),worldBox=read(d/'input.derivation.json')['worldBox'],route='builtin',actualModel=None,actualQuality=None))
 print(json.dumps(args))
def ingest(name,host):
 d=T/'repairs'/name;host=Path(host);f=d/'native.png';assert not f.exists();im=Image.open(host)
 assert im.size==(1254,1254) and im.format=='PNG' and im.convert('RGBA').getchannel('A').getextrema()==(255,255)
 shutil.copyfile(host,f);assert sha(host)==sha(f)
 write(d/'generation.json',dict(file=str(f),sha256=sha(f),hostOutputPath=str(host),hostSha256=sha(host),copyByteIdentical=True,size=[1254,1254],route='builtin',tool='image_gen.imagegen',actualModel=None,actualQuality=None,worldBox=read(d/'input.derivation.json')['worldBox'],request=dict(file=str(d/'request.json'),sha256=sha(d/'request.json')),prompt=dict(file=str(d/'prompt.txt'),sha256=sha(d/'prompt.txt')),receipt=dict(file=str(d/'tool-receipt.json'),sha256=sha(d/'tool-receipt.json')),resampled=False,finalArtUpscaled=False,formalAccepted=False))
 print(json.dumps(dict(file=str(f),sha256=sha(f))))
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='prepare':prepare(sys.argv[2],int(sys.argv[3]))
 if cmd=='request':request(sys.argv[2],sys.argv[3])
 if cmd=='ingest':ingest(sys.argv[2],sys.argv[3])

