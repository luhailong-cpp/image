from pathlib import Path
from PIL import Image
import hashlib,json,sys,shutil,datetime,importlib.util
import numpy as np
D=Path(__file__).resolve().parent
B=D.parents[1]
ROOT=Path('D:/work/image')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,j):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(j,f,ensure_ascii=False,indent=2)
def entry(p):return {'path':str(p),'sha256':sha(p)}
mode=sys.argv[1]
if mode=='inspect':
 spec=json.loads(sys.stdin.read());source=Path(spec['source']);d=Path(spec['directory']);d.mkdir(exist_ok=False);im=Image.open(source);items=[]
 for name,box in spec['boxes'].items():
  p=d/(name+'.png');im.crop(box).save(p);items.append({**entry(p),'contextBox':box,'cropIdentityMismatchPixels':int(np.count_nonzero(np.any(np.asarray(Image.open(p))!=np.asarray(im)[box[1]:box[3],box[0]:box[2]],axis=2)))})
 write(d/'crop-provenance.json',{'source':entry(source),'nativeScale':1,'crops':items});print(json.dumps({'directory':str(d),'count':len(items)}))
elif mode=='recover':
 qpath=B/'repairs/r12c07-resume-20261016-v1/C07-R17-v01.request.json';q=read(qpath)
 tool=Path('C:/Users/luyua/.codex/generated_images/01a142fa-243a-7c50-a079-2bca37cf0fcb/exec-90cd09a7-3923-49d9-8b9f-79d92c48afd0.png')
 out=D/'C07-R17-v01.native.png';assert not out.exists();im=Image.open(tool);assert im.size==(1254,1254)
 assert sha(q['source']['path'])==q['source']['sha256'] and sha(q['baseAssembly']['path'])==q['baseAssembly']['sha256']
 shutil.copy2(tool,out);assert sha(tool)==sha(out)
 g={'schemaVersion':1,'repairId':'C07-R17','file':str(out),'sha256':sha(out),'width':1254,'height':1254,'mode':im.mode,'sourceToolFile':str(tool),'sourceToolSha256':sha(tool),'request':entry(qpath),'coordinates':{k:q[k] for k in ['globalNativeBox','globalCoreBox','coreInNative']},'route':'builtin','actualModel':'not returned','actualQuality':'not returned','nativePixelsResampled':False,'recoveredAfterWorkerError':True,'associationEvidence':'Single later tool PNG in original worker directory, matching exact R17 native reference content; both images visually inspected. Original tool message is not present in current context.','toolFileModifiedUtc':datetime.datetime.fromtimestamp(tool.stat().st_mtime,datetime.timezone.utc).isoformat(),'formalAccepted':False}
 write(str(out)+'.generation.json',g)
 write(D/'recovery-v1.json',{'baseAssembly':q['baseAssembly'],'baseContext':q['source'],'recovered':entry(out),'request':entry(qpath),'generation':entry(str(out)+'.generation.json'),'oldWorker':'errored per coordinator; not resumed','priorChecks':'Reuse matching input-hash local reviews R13..R16, retain their open findings; no automatic whole-tile pass.'})
 print(json.dumps({'generation':entry(str(out)+'.generation.json'),'baseAssembly':q['baseAssembly']}))
elif mode=='qa-crops':
 d=Path(sys.argv[2]);a=read(d/'assembly.json');im=Image.open(d/'context-native.png');x,y,x1,y1=a['repairOverlay']['contextBox'];boxes={'top':[x,max(0,y-115),x1,y+345],'bottom':[x,y1-345,x1,min(im.height,y1+115)],'left':[max(0,x-115),y,x+345,y1],'right':[x1-345,y,min(im.width,x1+115),y1]};items=[]
 for k,box in boxes.items():
  p=d/(k+'-boundary-native.png');assert not p.exists();crop=im.crop(box);crop.save(p);assert np.array_equal(np.asarray(Image.open(p)),np.asarray(im)[box[1]:box[3],box[0]:box[2]])
  items.append({**entry(p),'contextBox':box,'cropIdentityMismatchPixels':0})
 write(d/'boundary-crops-v1.json',{'input':entry(d/'context-native.png'),'crops':items,'nativeScale':1});print(json.dumps(items))
elif mode=='review':
 spec=json.loads(sys.stdin.read());d=Path(spec.pop('directory'));a=read(d/'assembly.json')
 write(d/'visual-qa-v1.json',{**spec,'assembly':entry(d/'assembly.json'),'context':entry(d/'context-native.png'),'reviewedCrops':[entry(d/'repair-overlay-native.png')]+[entry(d/(n+'-boundary-native.png')) for n in ['top','bottom','left','right']],'sourceReplay':a['proof'],'nativeScale':1,'formalAccepted':False,'priorOtherFindingsRemainOpen':True})
elif mode=='prepare':
 spec=json.loads(sys.stdin.read());a=read(spec['baseAssembly']);source=Path(spec['source']) if 'source' in spec else Path(spec['baseAssembly']).parent/a['context']['path'];box=spec['box'];rid=spec['id'];out=D/(rid+'.source-native-crop.png');assert not out.exists();Image.open(source).crop(box).save(out)
 origin=a.get('globalContextBox',[24461,44941,28787,49267]);gb=[origin[i%2]+box[i] for i in range(4)]
 q={'schemaVersion':1,'repairId':rid,'source':{**entry(source),'contextCropBox':box},'baseAssembly':entry(spec['baseAssembly']),'references':[{**entry(out),'role':'actual integer native crop; no resize'}],'globalNativeBox':gb,'globalCoreBox':[gb[0]+115,gb[1]+115,gb[2]-115,gb[3]-115],'coreInNative':[115,115,1139,1139],'arguments':{'prompt':spec['prompt'],'referenced_image_paths':[str(out)],'transparent_background':False},'route':'builtin','actualModel':'not returned','actualQuality':'not returned','instructions':entry(ROOT/'AGENTS.md'),'split':entry(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'formalAccepted':False}
 write(D/(rid+'.request.json'),q);print(json.dumps(entry(D/(rid+'.request.json'))))
elif mode=='archive':
 rid,sp=sys.argv[2:4];qpath=D/(rid+'.request.json');q=read(qpath);src=Path(sp);out=D/(rid+'.native.png');assert not out.exists();im=Image.open(src);assert im.size==(1254,1254)
 shutil.copy2(src,out)
 g={'schemaVersion':1,'repairId':rid,'file':str(out),'sha256':sha(out),'width':1254,'height':1254,'mode':im.mode,'sourceToolFile':str(src),'sourceToolSha256':sha(src),'request':entry(qpath),'coordinates':{k:q[k] for k in ['globalNativeBox','globalCoreBox','coreInNative']},'route':'builtin','actualModel':'not returned','actualQuality':'not returned','nativePixelsResampled':False,'formalAccepted':False}
 write(str(out)+'.generation.json',g);print(json.dumps({'generation':entry(str(out)+'.generation.json'),'baseAssembly':q['baseAssembly']}))
elif mode=='overlay':
 rid,outstr=sys.argv[2:4];out=Path(outstr);q=read(D/(rid+'.request.json'));g=read(D/(rid+'.native.png.generation.json'));x,y,x1,y1=q['source']['contextCropBox'];assert not out.exists()
 assert sha(q['source']['path'])==q['source']['sha256'];assert sha(q['baseAssembly']['path'])==q['baseAssembly']['sha256'];assert sha(g['file'])==g['sha256']
 base=np.array(Image.open(q['source']['path']).convert('RGB'));native=np.array(Image.open(g['file']).convert('RGB'));old=base[y:y1,x:x1].copy();assert native.shape==(1254,1254,3)
 sp=importlib.util.spec_from_file_location('assembly_native',B/'scripts/assembly-v4.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
 left,_=mod.minimum_seam(old[:,:230],native[:,:230]);right,_=mod.minimum_seam(old[:,1024:],native[:,1024:]);right+=1024
 top,_=mod.minimum_seam(old[230:345].transpose(1,0,2),native[230:345].transpose(1,0,2));top+=230
 bottom,_=mod.minimum_seam(old[1024:].transpose(1,0,2),native[1024:].transpose(1,0,2));bottom+=1024
 xx=np.arange(1254)[None,:];yy=np.arange(1254)[:,None];mask=(xx>=left[:,None])&(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:]);result=base.copy();result[y:y1,x:x1][mask]=native[mask]
 out.mkdir();Image.fromarray(result).save(out/'context-native.png');Image.fromarray(result[115:4211,115:4211]).save(out/'r12_c07.candidate.png');Image.fromarray(result[y:y1,x:x1]).save(out/'repair-overlay-native.png');Image.fromarray(mask.astype('uint8')*255).save(out/'repair-source-mask.png');np.save(out/'mask-uint8.npy',mask.astype('uint8'))
 replay=base.copy();loaded=np.load(out/'mask-uint8.npy').astype(bool);replay[y:y1,x:x1][loaded]=native[loaded];proof={'hierarchicalFullContextReplayDifferentPixels':int(np.count_nonzero(np.any(replay!=result,axis=2))),'uncoveredPixels':0,'method':'Hash-bound base assembly plus integer selected native source; base retains its complete linked history.','top570ChangedPixels':int(np.count_nonzero(np.any(base[:570]!=result[:570],axis=2))),'noResize':True,'noBlend':True,'noBlur':True}
 a={'schemaVersion':1,'globalContextBox':[24461,44941,28787,49267],'tile':'r12_c07','baseAssembly':q['baseAssembly'],'baseContext':q['source'],'generation':entry(D/(rid+'.native.png.generation.json')),'context':entry(out/'context-native.png'),'tiles':[entry(out/'r12_c07.candidate.png')],'repairOverlay':{'contextBox':[x,y,x1,y1],'mask':entry(out/'mask-uint8.npy'),'source':entry(g['file']),'sourceOriginInContext':[x,y],'method':'four-sided binary DP source selection; top path in rows230..344 preserves north repair','leftPath':left.tolist(),'rightPath':right.tolist(),'topPath':top.tolist(),'bottomPath':bottom.tolist(),'selectedPixelCount':int(mask.sum())},'proof':proof,'formalAccepted':False,'status':'pending-visual-QA','script':entry(__file__)}
 write(out/'assembly.json',a);print(json.dumps({'assembly':entry(out/'assembly.json'),'proof':proof}))
