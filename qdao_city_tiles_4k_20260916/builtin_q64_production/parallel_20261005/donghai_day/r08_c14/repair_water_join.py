import sys,json,shutil,hashlib
from pathlib import Path
from datetime import datetime,timezone
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;ROOT=T.parent;R=T/'repairs/water-join'
sys.path.insert(0,str(ROOT));import assembly_r08_c14 as a
P=T/'output/r08_c14.png';STYLE=Path('D:/work/image/designs/gameplay-ui/04-guild.png');X=1421
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,v):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def prep(i):
 R.mkdir(parents=True,exist_ok=True);y=(i-1)*1024;im=Image.open(P).convert('RGB').crop((X,y,X+1254,y+1254))
 refs0=[{'file':str(P),'sha256':sha(P),'role':'current complete candidate native source'}]
 if i==2:
  prev=R/'s1.png';im.paste(Image.open(prev).crop((0,1024,1254,1254)),(0,0));refs0.append({'file':str(prev),'sha256':sha(prev),'role':'previous repair top overlap'})
 q=R/f's{i}-input.png';im.save(q)
 save(str(q)+'.generation.json',{'file':str(q),'sha256':sha(q),'derivedFrom':refs0,'sourceRect':[X,y,X+1254,y+1254],'resized':False})
 refs=[{'file':str(q),'sha256':sha(q),'role':'native crop across faulty vertical water join, edit target'},{'file':str(STYLE),'sha256':sha(STYLE),'role':'user-confirmed Q style only, no UI'}]
 prompt='''Use case: precise-object-edit. Edit IMAGE 1 only. This is an exact native close crop of a finished bright clean Q-style hand-painted fishing village map. There is a faulty artificial vertical water-color and wave-pattern join near the middle x627, visible as an unnatural jagged long vertical boundary between cyan water on the left and blue water on the right. Repair this vertical seam: paint one continuous calm cyan-blue water surface with broad quiet organic low-contrast wave shapes flowing across the middle. Both left and right are the same body of water; there must be no vertical stripe, upright boundary, zigzag cut, or abrupt palette division anywhere. Match BOTH existing outer-side water palettes, with a natural gentle transition through the center; do not recolor the entire crop. Keep the outer 150 pixels left and right as close as possible. Topmost existing overlap may be an already fixed native crop: keep it consistent. Preserve exact camera, framing, any wooden object, basket or red banner and their pixel geometry. Do not add white netlike highlights, caustic web, foam, pale glare, noise, tiny sharp waves, new objects or UI. Image 2 is the primary user-approved art-material style only, no scene changes. Output only image 1 repaired, one opaque native1254x1254 square, no crop, resize, rotation or zoom.'''
 (R/f's{i}.txt').write_text(prompt,encoding='utf-8');save(R/f's{i}.references.json',refs)
 print(json.dumps({'name':f's{i}','prompt':prompt,'references':[e['file'] for e in refs]}))
def record(i,src):
 src=Path(src);out=R/f's{i}.png';shutil.copyfile(src,out);im=Image.open(out);assert im.size==(1254,1254)
 save(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'format':'PNG','generatedAt':datetime.now(timezone.utc).isoformat(),'timestampMeaning':'locally observed tool completion','tool':'image_gen.imagegen','route':'builtin','configSnapshot':read(Path('D:/work/image/config/image-generation.json')),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[e['file'] for e in read(R/f's{i}.references.json')]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool did not disclose model or quality','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src)},'references':read(R/f's{i}.references.json'),'prompt':str(R/f's{i}.txt'),'promptSha256':sha(R/f's{i}.txt'),'resizedAfterGeneration':False,'finalArtUpscaled':False})
 print(json.dumps({'saved':str(out),'sha256':sha(out)}))
def integrate():
 before=read(R/'s1-input.png.generation.json')['derivedFrom'][0];assert sha(P)==before['sha256']
 base=np.array(Image.open(P).convert('RGB'));s1=np.array(Image.open(R/'s1.png').convert('RGB'));s2=np.array(Image.open(R/'s2.png').convert('RGB')) if (R/'s2.png').exists() else None;fn=a.load_seam_function();masks=[]
 def mix(old,new,axis,label):
  u,v=(old,new) if axis=='v' else (old.transpose(1,0,2),new.transpose(1,0,2));path=fn(u,v);mask=a.seam_alpha(path,u.shape[1]);result=a.blend(u,v,mask)
  q=R/(label+'-mask.png');Image.fromarray(mask).save(q);masks.append({'file':str(q),'sha256':sha(q),'transitionPixels':2,'resized':False})
  return result if axis=='v' else result.transpose(1,0,2)
 strip=np.concatenate([s1[:1024],mix(s1[1024:],s2[:230],'h','patch-join'),s2[230:]],axis=0) if s2 is not None else s1.copy()
 h,w=strip.shape[:2];old=base[:h,X:X+w].copy();e=150
 strip[:,:e]=mix(old[:,:e],strip[:,:e],'v','left-insert');strip[:,-e:]=mix(strip[:,-e:],old[:,-e:],'v','right-insert');strip[-e:]=mix(strip[-e:],old[-e:],'h','bottom-insert')
 result=base.copy();result[:h,X:X+w]=strip
 assert np.array_equal(result[:, :X],base[:,:X]) and np.array_equal(result[:,X+w:],base[:,X+w:]) and np.array_equal(result[h:],base[h:])
 shutil.copyfile(T/'output/assembly-manifest.json',R/'base-assembly-manifest.json')
 Image.fromarray(result).save(P)
 extended=np.array(Image.open(T/'output/extended-context.png').convert('RGB'));extended[115:4211,115:4211]=result;Image.fromarray(extended).save(T/'output/extended-context.png')
 out={'file':str(P),'sha256':sha(P),'pixels':[4096,4096]}
 save(R/'integration.json',{'operation':'native repair insertion with two-pixel minimum-error seam paths','source':dict(before,availability='superseded',historicalManifest=str(R/'base-assembly-manifest.json'),historicalManifestSha256=sha(R/'base-assembly-manifest.json'),pixelValidation='historical-record-only-not-current-pixels'),'patches':[read(R/f's{i}.png.generation.json') for i in ([1,2] if s2 is not None else [1])],'output':out,'changedPixelsRestrictedToRect':[X,0,X+w,h],'outsideRectExactlyUnchanged':True,'masks':masks,'sourceResampling':False,'upscale':False,'colorCorrection':False,'formalAccepted':False})
 qa_only()
 print(json.dumps(out))
def qa_only():
 im=Image.open(P).convert('RGB');ex=Image.open(T/'output/extended-context.png').convert('RGB');west,wi=a.checked_west();qa=a.write_qa(im,ex,west)
 out={'file':str(P),'sha256':sha(P),'pixels':[4096,4096]}
 h=read(R/'integration.json')['changedPixelsRestrictedToRect'][3]
 bands=[('left-upper',[X-32,0,X+182,1254]),('right-upper',[X+1072,0,X+1286,1254]),('bottom',[X,h-182,X+1254,h+32])]
 if h>1254:bands.extend([('left-lower',[X-32,1024,X+182,h]),('right-lower',[X+1072,1024,X+1286,h])])
 for label,box in bands:
  q=R/(label+'-qa.png');im.crop(box).save(q);qa.append({'file':str(q),'sha256':sha(q),'sourceRect':box,'pixelScale':1,'kind':'native repair insertion edge','resized':False})
 save(T/'qa/assembly/water-join-qa-metadata.json',{'candidate':out,'qa':qa})
 m=read(R/'base-assembly-manifest.json');m.update(output=out,postAssemblyRepair={'record':str(R/'integration.json'),'recordSha256':sha(R/'integration.json')},nativeAssemblyBase={'historicalManifest':str(R/'base-assembly-manifest.json'),'sha256':sha(R/'base-assembly-manifest.json')},extendedContext={'file':str(T/'output/extended-context.png'),'sha256':sha(T/'output/extended-context.png'),'pixels':[4326,4326]})
 save(T/'output/assembly-manifest.json',m)
 q=read(T/'qa/assembly/manifest.json');q.update(qa=qa,candidateSha256=sha(P),visualInspection='pending');save(T/'qa/assembly/manifest.json',q)
if __name__=='__main__':
 if '--east' in sys.argv:
  R=T/'repairs/water-join-east';X=2445;sys.argv.remove('--east')
 if sys.argv[1]=='prepare':prep(int(sys.argv[2]))
 elif sys.argv[1]=='record':record(int(sys.argv[2]),sys.argv[3])
 elif sys.argv[1]=='integrate':integrate()
 elif sys.argv[1]=='qa':qa_only()
