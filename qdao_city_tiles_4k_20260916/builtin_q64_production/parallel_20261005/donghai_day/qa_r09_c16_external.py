"""Native-pixel external QA probes and honest initial review."""
from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent;T=R/'r09_c16'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def im(p):
 with Image.open(p) as v:v.load();return v.convert('RGB')
def probes(candidate,folder):
 candidate=Path(candidate);folder=Path(folder);folder.mkdir(parents=True,exist_ok=True)
 p=read(T/'plan.json');west=p['neighbors']['west'];north=p['neighbors']['north']
 assert sha(west['file'])==west['sha256'] and sha(north['file'])==north['sha256']
 a=im(candidate);w=im(west['file']);n=im(north['file'])
 assert a.size==w.size==n.size==(4096,4096)
 common=Image.new('RGB',(256,4096));common.paste(w.crop((3968,0,4096,4096)),(0,0));common.paste(a.crop((0,0,128,4096)),(128,0))
 sheet=Image.new('RGB',(1024,1024))
 for i in range(4):sheet.paste(common.crop((0,i*1024,256,(i+1)*1024)),(i*256,0))
 wp=folder/'west-r09-c15-c16-common-edge-full.png';sheet.save(wp)
 nw=R/'r08_c15/output/r08_c15.png';assert sha(nw)=='70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'
 cross=Image.new('RGB',(1024,1024))
 cross.paste(im(nw).crop((3584,3584,4096,4096)),(0,0))
 cross.paste(n.crop((0,3584,512,4096)),(512,0))
 cross.paste(w.crop((3584,0,4096,512)),(0,512))
 cross.paste(a.crop((0,0,512,512)),(512,512))
 cp=folder/'northwest-four-tiles.png';cross.save(cp)
 save(folder/'external-manifest.json',{'candidate':str(candidate),'candidateSha256':sha(candidate),'nativePixelQA':True,'resized':False,'west':west,'north':north,'northwest':{'file':str(nw),'sha256':sha(nw)},'sheets':[{'file':str(q),'sha256':sha(q)} for q in (wp,cp)],'visualReview':'pending'})
 print(json.dumps({'west':str(wp),'cross':str(cp)}))
def initial():
 base=T/'output/r09_c16.png';assert sha(base)=='ff169961a00d04558464d4436397938b02ac4e53fd492f7a74122b49eda53095'
 qa=T/'qa/assembly';names=['overview-preview-1024','north-r08-r09-common-edge-full']+[f'internal-{o}-{axis}{v}-full' for o,axis in [('vertical','x'),('horizontal','y')] for v in (1024,2048,3072)]+[f'intersection-x{x}-y{y}' for y in (1024,2048,3072) for x in (1024,2048,3072)]+['corner-'+c for c in ('nw','ne','sw','se')]
 save(T/'qa/root-initial-review.json',{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','actualVisualInspection':True,'candidateSha256':sha(base),'result':'repair-required','observations':['Visible water tonal cuts along x1024/x2048 in upper half and y1024 left two thirds; lighter water cuts at remaining internal boundaries.','Lantern backing timber has a y3072 tonal cut; structure silhouettes otherwise coherent.','Four standalone corners clean. North seam generally coherent but water vertical interior cuts reach that band; requires re-review after correction.'],'viewedSheets':[{'file':str(qa/(n+'.png')),'sha256':sha(qa/(n+'.png'))} for n in names],'formalAccepted':False})
 files=[T/'native'/f'r01_c{c:02d}.png' for c in range(1,5)]
 save(T/'qa/top-row-generation-review.json',{'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'root','actualVisualInspection':True,'files':[{'file':str(q),'sha256':sha(q)} for q in files],'observations':['All four actual builtin outputs viewed before record; existing quiet water and top hull contact rim retained; no invented objects.','Generation-level review does not establish final seam acceptance.'],'formalAccepted':False})
if __name__=='__main__':
 if sys.argv[1]=='initial':initial();probes(T/'output/r09_c16.png',T/'qa/assembly')
 elif sys.argv[1]=='probes':probes(sys.argv[2],sys.argv[3])
