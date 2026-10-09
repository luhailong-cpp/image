from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def im(p):
 with Image.open(p) as a:a.load();assert a.size==(4096,4096);return a.convert('RGB')
def probes(west_path,east_path,folder):
 west_path=Path(west_path).resolve();east_path=Path(east_path).resolve();folder=Path(folder).resolve();assert folder.is_relative_to((R/'r10_c16').resolve());folder.mkdir(parents=True,exist_ok=True)
 west=im(west_path);east=im(east_path);nwp=R/'r09_c15/output/r09_c15.png';nep=R/'r09_c16/output/r09_c16.png'
 assert sha(nwp)=='33abbb4345add5b42b8020ce1c6dd4b40a44d4fdb7dd96fc3b37220006c5c6ff';assert sha(nep)=='75e40578e8c29233bd6b73fbf60a3ea0d7eec917769b93de51404ad34e99a5f9'
 sheets=[]
 def save(name,v):
  p=folder/(name+'.png');v.save(p);sheets.append({'file':str(p),'sha256':sha(p),'pixels':list(v.size),'resampled':False})
 band=Image.new('RGB',(256,4096));band.paste(west.crop((3968,0,4096,4096)),(0,0));band.paste(east.crop((0,0,128,4096)),(128,0));sheet=Image.new('RGB',(1024,1024))
 for i in range(4):sheet.paste(band.crop((0,i*1024,256,(i+1)*1024)),(i*256,0))
 save('west-r10-c15-c16-common-edge-full',sheet)
 for i,y in enumerate([0,1024,2048,2842],1):
  wide=Image.new('RGB',(896,1254));wide.paste(west.crop((3648,y,4096,y+1254)),(0,0));wide.paste(east.crop((0,y,448,y+1254)),(448,0));save('west-wide-'+str(i),wide)
 cross=Image.new('RGB',(1024,1024));cross.paste(im(nwp).crop((3584,3584,4096,4096)),(0,0));cross.paste(im(nep).crop((0,3584,512,4096)),(512,0));cross.paste(west.crop((3584,0,4096,512)),(0,512));cross.paste(east.crop((0,0,512,512)),(512,512));save('northwest-four-tiles',cross)
 meta={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'west':{'file':str(west_path),'sha256':sha(west_path)},'east':{'file':str(east_path),'sha256':sha(east_path)},'northwest':{'file':str(nwp),'sha256':sha(nwp)},'north':{'file':str(nep),'sha256':sha(nep)},'sheets':sheets,'visualReview':'pending','nativePixelQA':True,'formalAccepted':False};(folder/'external-manifest.json').write_text(json.dumps(meta,indent=2)+'\n',encoding='utf-8');print(json.dumps(meta))
if __name__=='__main__':probes(*sys.argv[1:4])
