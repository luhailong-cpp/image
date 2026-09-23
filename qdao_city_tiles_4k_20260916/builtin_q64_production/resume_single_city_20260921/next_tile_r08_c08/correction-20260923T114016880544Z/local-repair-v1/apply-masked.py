from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import numpy as np,importlib.util,json,hashlib,sys
HERE=Path(__file__).resolve().parent;RUN=HERE.parent;P=RUN.parent;SESSION=P.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):
 with p.open('x',encoding='utf8',newline='\n') as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
 return info(p)
sys.path.insert(0,str(SESSION/'tools/vendor'))
helperpath=SESSION.parent/'tools/mechanical_join.py';spec=importlib.util.spec_from_file_location('c08_masked_join',helperpath);helper=importlib.util.module_from_spec(spec);sys.dont_write_bytecode=True;spec.loader.exec_module(helper)
base=RUN/'diagnostic-20260923T114940236668Z/r08_c08.png';assert sha(base)=='727526a5f7b8b1fe75e29052a2f7d34ec0c45ec79f07cd5a851e2ae96e838911'
before=np.asarray(Image.open(base).convert('RGB'));after=before.copy();allowed=np.zeros((4096,4096),bool)
OUT=HERE/'masked-result';OUT.mkdir();entries=[]
for name in ['band-c03','band-c04','carving-left']:
 pre=read(HERE/(name+'.preflight.json'));rec=read(HERE/(name+'.generation.json'));nativepath=HERE/(name+'.native.png');assert sha(nativepath)==rec['sha256']
 for ref in pre['references']:assert sha(ref['file'])==ref['sha256']
 contextpath=HERE/(name+'.context.png');context=np.asarray(Image.open(contextpath).convert('RGB'));native=np.asarray(Image.open(nativepath).convert('RGB'));assert context.shape==native.shape==(1254,1254,3)
 x,y,x2,y2=pre['canvasBoxLTRB'];assert y==3454
 yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
 smooth=lambda a:(lambda t:t*t*(3-2*t))(np.clip(a,0,1))
 a=smooth((yy-384)/56)*smooth((641-yy)/28)
 if x>0:a*=smooth(xx/64)
 if x2<4096:a*=smooth((1253-xx)/64)
 a[yy>=642]=0;mask=np.rint(a*255).astype('uint8')
 # Registration operates only on generated pixels; fixed source is never blurred.
 result,flow,tone,registration=helper.registered_join(context,native,mask,max_shift=6.0,match_tone=True)
 assert np.array_equal(result[mask==0],context[mask==0])
 height=4096-y;localmask=mask[:height]/255.0
 # Use current candidate under feather, keeping already-applied overlap contributions.
 new=np.rint(after[y:4096,x:x2].astype(float)*(1-localmask[:,:,None])+result[:height].astype(float)*localmask[:,:,None]).clip(0,255).astype('uint8')
 # result already contains the source through mask. Above second composition only
 # feathers overlaps conservatively; this is explicit double feather, never a blur.
 after[y:4096,x:x2]=new;allowed[y:4096,x:x2]|=mask[:height]>0
 Image.fromarray(mask).save(OUT/(name+'.mask.png'));Image.fromarray(result).save(OUT/(name+'.context-after.png'))
 np.save(OUT/(name+'.flow.npy'),flow,allow_pickle=False);np.save(OUT/(name+'.tone.npy'),tone,allow_pickle=False)
 nz=np.argwhere(mask>0);entries.append({'name':name,'native':info(nativepath),'generation':info(HERE/(name+'.generation.json')),'preflight':info(HERE/(name+'.preflight.json')),'context':info(contextpath),'canvasBoxLTRB':pre['canvasBoxLTRB'],'mask':info(OUT/(name+'.mask.png')),'maskNonzeroGlobalLTRB':[int(x+nz[:,1].min()),int(y+nz[:,0].min()),int(x+nz[:,1].max()+1),int(y+nz[:,0].max()+1)],'registration':registration,'flow':info(OUT/(name+'.flow.npy')),'tone':info(OUT/(name+'.tone.npy'))})
changed=np.any(after!=before,axis=2);assert not np.any(changed&~allowed);assert np.array_equal(after[:3838],before[:3838]);assert np.array_equal(after[-1],before[-1])
Image.fromarray(after).save(OUT/'r08_c08.png');candidate=info(OUT/'r08_c08.png');nz=np.argwhere(changed)
record=write(OUT/'repair.json',{'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r08_c08','status':'local_repair_candidate_pending_visual_review','candidate':candidate,'sourceCandidate':info(base),'sourceAssembly':info(base.parent/'assembly.json'),'script':info(__file__),'helper':info(helperpath),'nativeRepairCount':3,'repairs':entries,'method':'Original native AI repair pixels registered within max6px and local tone corrections, composed with explicitly recorded smoothstep masks; double feather at return bounds; no upscaling; no source-image blur','outsideUnionMaskPixelsUnchanged':True,'unchangedAboveTileY':3838,'lastTileRowUnchanged':True,'fixedBottomNeighborUnmodified':True,'changedPixelCount':int(changed.sum()),'changedBoundsLTRB':[int(nz[:,1].min()),int(nz[:,0].min()),int(nz[:,1].max()+1),int(nz[:,0].max()+1)],'actualModel':None,'actualQuality':None,'formalAccepted':False,'visualAcceptancePassed':False,'runtimeAccepted':False})
print(json.dumps({'candidate':candidate,'repair':record,'baseAssembly':info(base.parent/'assembly.json'),'changedPixels':int(changed.sum())}))
