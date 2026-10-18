from pathlib import Path
import sys,json,hashlib,datetime
from PIL import Image
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T.parent))
import production_v2 as p
N={'north':(T.parent/'r06_c07/candidate/r06_c07-candidate-hard-4c0d654c3aae.png','e3184ae204d0cd8f0ea701bf6b3281449bb1489bb1489c18514f525869f37d72326609'), 'west':(T.parent/'r07_c06/candidate/r07_c06-candidate-native-roi-v10.png','77f0dd8a35c954a08eaf2f6102e8e7e1c9dcb38e895305fa8070ab6734c2e16b')}
N['north']=(N['north'][0],'e3184ae204d0cd8f0ea701bf6b3281449bb1489c18514f525869f37d72326609')
def pixels(im):return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()
def write(f,obj):
 f.parent.mkdir(parents=True,exist_ok=True)
 if f.exists():assert p.read(f)==obj;return
 f.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
sel=p.read(T/'selection.json'); assert len(sel)==16
sources=[]
im=Image.new('RGB',(4096,4096))
for rr in range(4):
 for cc in range(4):
  pid=f's{rr+1:02d}_{cc+1:02d}';f=Path(sel[pid]);v=p.validate_native(f,T,pid)
  core=Image.open(f).convert('RGB').crop((115,115,1139,1139));dest=[cc*1024,rr*1024,(cc+1)*1024,(rr+1)*1024];im.paste(core,dest[:2])
  sources.append(dict(v,id=pid,crop=[115,115,1139,1139],destination=dest,corePixelSha256=pixels(core),nativeSize=[1254,1254],resampled=False))
key=hashlib.sha256(json.dumps([(s['id'],s['sha256']) for s in sources]).encode()).hexdigest()[:16]
D=T/'candidate'/('hard-native16-20261016-'+key);Q=T/'qa'/D.name;D.mkdir(parents=True,exist_ok=True);Q.mkdir(parents=True,exist_ok=True)
out=D/'candidate.png'
if out.exists():assert pixels(Image.open(out))==pixels(im)
else:im.save(out)
verified=0
for s in sources:
 assert pixels(im.crop(s['destination']))==s['corePixelSha256'];verified+=1024*1024
write(D/'provenance.json',dict(tile=T.name,worldBox=p.tile_box(T.name),output=dict(file=str(out),sha256=p.sha(out),size=[4096,4096]),nativeSources=sources,missingNativePatches=[],sourceResampled=False,sourceUpscaled=False,byteExactNativeCorePixels=verified,fullNativeCoverageVerified=verified==4096**2,formalAccepted=False))
reuse={}
for review in (T/'qa/source-review').glob('*/review.json'):
 try:r=p.read(review)
 except Exception:continue
 for c in r.get('cropReviews',[]):
  if 'file' not in c:continue
  f=Path(c['file'])
  if f.exists() and p.sha(f)==c['sha256']:
   reuse.setdefault(pixels(Image.open(f)),[]).append(dict(reviewFile=str(review),file=str(f),sha256=c['sha256'],status=c['status'],finding=c.get('finding'),actuallyViewed=r.get('actuallyViewed',False)))
crops=[]
def save(name,img,kind,box):
 f=Q/(name+'.png');img.save(f);h=pixels(img);matches=reuse.get(h,[])
 crops.append(dict(name=name,file=str(f),sha256=p.sha(f),pixelSha256=h,kind=kind,tileBox=box,nativePixelScale=1,matchingPriorReviews=matches,status='needs_review'))
for x in [1024,2048,3072]:
 for rr in range(4):b=[x-160,rr*1024,x+160,(rr+1)*1024];save(f'v{x}_r{rr+1}',im.crop(b),'internal_vertical',b)
for y in [1024,2048,3072]:
 for cc in range(4):b=[cc*1024,y-160,(cc+1)*1024,y+160];save(f'h{y}_c{cc+1}',im.crop(b),'internal_horizontal',b)
for y in [1024,2048,3072]:
 for x in [1024,2048,3072]:b=[x-160,y-160,x+160,y+160];save(f'j{x}_{y}',im.crop(b),'internal_junction',b)
for side,(f,h) in N.items():
 assert p.sha(f)==h;neighbor=Image.open(f).convert('RGB')
 for k in range(4):
  if side=='north':
   a=Image.new('RGB',(1024,320));a.paste(neighbor.crop((k*1024,3936,(k+1)*1024,4096)),(0,0));a.paste(im.crop((k*1024,0,(k+1)*1024,160)),(0,160))
  else:
   a=Image.new('RGB',(320,1024));a.paste(neighbor.crop((3936,k*1024,4096,(k+1)*1024)),(0,0));a.paste(im.crop((0,k*1024,160,(k+1)*1024)),(160,0))
  save(f'{side}_seg{k+1}',a,'external_'+side,None)
 for k in [1024,2048,3072]:
  a=Image.new('RGB',(320,320))
  if side=='north':a.paste(neighbor.crop((k-160,3936,k+160,4096)),(0,0));a.paste(im.crop((k-160,0,k+160,160)),(0,160))
  else:a.paste(neighbor.crop((3936,k-160,4096,k+160)),(0,0));a.paste(im.crop((0,k-160,160,k+160)),(160,0))
  save(f'{side}_joint{k}',a,'external_'+side+'_junction',None)
assert len(crops)==47
write(Q/'manifest.json',dict(candidate=dict(file=str(out),sha256=p.sha(out)),internalCount=33,externalCount=14,neighbors={k:dict(file=str(f),sha256=h) for k,(f,h) in N.items()},crops=crops,formalAccepted=False))
write(T/'local-resume-checkpoint-20261016-native16.json',dict(tile=T.name,selectedCores=16,sourceCoverage='full_native_16_of_16',candidate=str(out),candidateSha256=p.sha(out),provenance=str(D/'provenance.json'),qaManifest=str(Q/'manifest.json'),qaCropCount=47,formalAccepted=False,status='needs_consolidated_visual_QA_and_local_repairs'))
print(json.dumps(dict(candidate=str(out),qa=str(Q),nativePixelsVerified=verified,crops=len(crops),exactPriorMatching=sum(bool(c['matchingPriorReviews']) for c in crops))))

