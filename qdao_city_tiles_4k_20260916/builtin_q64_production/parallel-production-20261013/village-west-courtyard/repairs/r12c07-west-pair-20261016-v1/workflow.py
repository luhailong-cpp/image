from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,sys,shutil,importlib.util
R=Path(__file__).parent;B=R.parents[1];Q=B/'qa/r12c07-west-pair-20261016-v1'
W=B/'repairs/r12c06-resume-20261016-v1/north-hard-v1/context-native.png'
E=B/'qa/r12c07-resume2-r19-v1/context-native.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rec(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def write(p,j):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(j,f,ensure_ascii=False,indent=2)
def save(p,a):
 assert not p.exists();Image.fromarray(a).save(p);return rec(p)
if sys.argv[1]=='diagnose':
 Q.mkdir(parents=True,exist_ok=True);assert sha(W)=='f688156e4a82f4f0b0ef294b3f2ba76e5b36d42baaf009f902b0530ea986b3ef';assert sha(E)=='99f50735f137c049b46ad315c5ea11873f9a30f25014561dcee25aaaec3e6f72'
 west=np.array(Image.open(W).convert('RGB'));east=np.array(Image.open(E).convert('RGB'));items=[]
 for i in range(4):
  y=115+i*1024;join=np.concatenate([west[y:y+1024,3866:4211],east[y:y+1024,115:460]],axis=1);p=Q/f'W{i+1:02d}-actual-core-join-before.png';e=save(p,join);e.update(westContextBox=[3866,y,4211,y+1024],eastContextBox=[115,y,460,y+1024],globalBox=[24231,44941+y,24921,44941+y+1024],coreJoinX=345,cropIdentityMismatchPixels=int(np.count_nonzero(np.any(np.asarray(Image.open(p))!=join,axis=2))));items.append(e)
 donor=west[:,4096:4326].copy();d=save(R/'same-global-west-donor-230x4326.png',donor)
 write(Q/'diagnostic-inputs-v1.json',{'west':rec(W),'east':rec(E),'eastAssembly':rec(E.parent/'assembly.json'),'nativeScale':1,'coreJoinGlobalX':24576,'strips':items,'sameGlobalDonor':{**d,'westContextBox':[4096,0,4326,4326],'eastContextBox':[0,0,230,4326],'globalBox':[24461,44941,24691,49267]},'formalAccepted':False})
 print(json.dumps({'qaDirectory':str(Q),'stripCount':4,'donor':d}))
elif sys.argv[1]=='prepare':
 s=json.loads(sys.stdin.read());name=s['name'];base=Path(s['base']);y=s['y'];ox=s.get('originX',-256);west=np.array(Image.open(W).convert('RGB'));east=np.array(Image.open(base).convert('RGB'))
 if ox==-256:ref=np.concatenate([west[y:y+1254,3840:4096],east[y:y+1254,:998]],axis=1);ref[:,:486]=west[y:y+1254,3840:4326]
 else:assert ox==0;ref=east[y:y+1254,:1254].copy();ref[:,:230]=west[y:y+1254,4096:4326]
 assert ref.shape==(1254,1254,3);rp=R/(name+'.reference-native.png');save(rp,ref)
 q={'name':name,'base':rec(base),'baseAssembly':rec(base.parent/'assembly.json'),'westAnchor':rec(W),'patchOriginInEastContext':[ox,y],'globalNativeBox':[24461+ox,44941+y,25715+ox,46195+y],'references':[rec(rp)],'nativeCompositeInstructions':f'Columns0..{229-ox} from same-global west native context; remainder from east. Same-global integer source selection only.','prompt':s['prompt'],'actualModel':'not returned','route':'builtin','rootInstructions':rec(Path('D:/work/image/AGENTS.md')),'split':rec(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json')),'formalAccepted':False};write(R/(name+'.request.json'),q);print(json.dumps(rec(R/(name+'.request.json'))))
elif sys.argv[1]=='archive':
 name,src=sys.argv[2:4];out=R/(name+'.native.png');assert not out.exists();im=Image.open(src);assert im.size==(1254,1254);shutil.copy2(src,out);write(R/(name+'.generation.json'),{'native':rec(out),'originalToolFile':rec(src),'request':rec(R/(name+'.request.json')),'width':1254,'height':1254,'route':'builtin','actualModel':'not returned','noResampling':True});print(json.dumps(rec(out)))
elif sys.argv[1]=='compose':
 name=sys.argv[2];out=Q/(name+'-v1');assert not out.exists();q=json.loads((R/(name+'.request.json')).read_text());basep=Path(q['base']['path']);assert sha(basep)==q['base']['sha256'];assert sha(W)==q['westAnchor']['sha256'];y=q['patchOriginInEastContext'][1]
 offset=-q['patchOriginInEastContext'][0];width=1254-offset;west=np.array(Image.open(W).convert('RGB'));base=np.array(Image.open(basep).convert('RGB'));gen=np.array(Image.open(R/(name+'.native.png')).convert('RGB'));old=base[y:y+1254,:width].copy();combined=gen[:,offset:].copy();combined[:,:230]=west[y:y+1254,4096:4326]
 sp=importlib.util.spec_from_file_location('assembly_native',B/'scripts/assembly-v4.py');mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
 right,_=mod.minimum_seam(old[:,width-230:],combined[:,width-230:]);right+=width-230
 top,_=mod.minimum_seam(old[:115].transpose(1,0,2),combined[:115].transpose(1,0,2))
 bottom,_=mod.minimum_seam(old[1024:].transpose(1,0,2),combined[1024:].transpose(1,0,2));bottom+=1024
 xx=np.arange(width)[None,:];yy=np.arange(1254)[:,None];take=(xx<right[:,None])&(yy>=top[None,:])&(yy<bottom[None,:]);anchor=take&(xx<230);generated=take&(xx>=230)
 result=base.copy();result[y:y+1254,:width][take]=combined[take];out.mkdir();save(out/'context-native.png',result);save(out/'r12_c07.candidate-native-4096.png',result[115:4211,115:4211]);save(out/'combined-reference-native.png',combined);np.save(out/'anchor-mask.npy',anchor.astype('uint8'));np.save(out/'generated-mask.npy',generated.astype('uint8'))
 replay=base.copy();part=replay[y:y+1254,:width];part[anchor]=west[y:y+1254,4096:4326][np.nonzero(anchor)[0],np.nonzero(anchor)[1]];part[generated]=gen[np.nonzero(generated)[0],np.nonzero(generated)[1]+offset]
 assert np.array_equal(replay,result)
 views={'center':[0,y,width,y+1254],'top':[0,max(0,y-115),width+115,y+345],'bottom':[0,y+909,width+115,min(4326,y+1369)],'left':[0,y,460,y+1254],'right':[width-345,y,width+115,y+1254]};crops=[]
 for n,box in views.items():
  x0,y0,x1,y1=box;p=out/(n+'-native.png');save(p,result[y0:y1,x0:x1]);crops.append({**rec(p),'contextBox':box,'cropIdentityMismatchPixels':0})
 join=np.concatenate([west[y:y+1254,3866:4211],result[y:y+1254,115:765]],axis=1);save(out/'actual-core-join-native.png',join)
 a={'name':name,'status':'pending-visual-QA','formalAccepted':False,'base':q['base'],'baseAssembly':q['baseAssembly'],'westAnchor':q['westAnchor'],'request':rec(R/(name+'.request.json')),'generation':rec(R/(name+'.generation.json')),'context':rec(out/'context-native.png'),'candidate':rec(out/'r12_c07.candidate-native-4096.png'),'globalContextBox':[24461,44941,28787,49267],'destinationBox':[0,y,width,y+1254],'anchorMask':rec(out/'anchor-mask.npy'),'generatedMask':rec(out/'generated-mask.npy'),'anchorSourceOriginInContext':[0,0],'anchorSourceWestCrop':[4096,0,4326,4326],'generatedSourceOriginInContext':[-offset,y],'method':'One common top/bottom/right hard mask jointly constrains immutable same-global anchor and generated pixels. No independent anchor rectangle is pasted after selection.','proof':{'hierarchicalFullContextReplayDifferentPixels':0,'uncoveredPixels':0,'upstreamChangedPixels':0,'noResize':True,'noBlend':True,'noBlur':True},'qaCrops':crops,'actualCoreJoin':rec(out/'actual-core-join-native.png'),'paths':{'top':top.tolist(),'bottom':bottom.tolist(),'right':right.tolist()},'script':rec(__file__)};write(out/'assembly.json',a);print(json.dumps({'assembly':rec(out/'assembly.json'),'context':a['context']}))
