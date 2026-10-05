"""Auditable local native repair preparation, saving, joining and native QA."""
import argparse,datetime,hashlib,importlib.util,json,re,shutil,sys
from pathlib import Path
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;S=R.parents[1];A=S.parents[1];REPO=A.parent
sys.dont_write_bytecode=True;sys.path.insert(0,str(S/'continuation_20261004/c07-recovery/vendor'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
info=lambda p:{'file':str(p),'sha256':sha(p)}
def write(p,x):
 with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def image(p):
 with Image.open(p) as im:im.load();return np.array(im.convert('RGB'))
def prepare(args):
 source=Path(args.source).resolve();base=image(source);assert base.shape==(4096,4096,3)
 box=args.box;x0,y0,x1,y1=box;assert x1-x0==1254 and y1-y0==1254 and 0<=x0<x1<=4096 and 0<=y0<y1<=4096
 d=R/args.id;d.mkdir(exist_ok=False);target=d/'context.png';Image.fromarray(base[y0:y1,x0:x1]).save(target)
 xs=[x-x0 for x in [1024,2048,3072] if x0<x<x1];ys=[y-y0 for y in [1024,2048,3072] if y0<y<y1]
 prompt=f'''Use case: precise-object-edit. Make the smallest targeted repair to reference image 1, an exact native1254x1254 crop from a fixed4096 game-city tile. Output exactly1254x1254 with identical framing and geometry. Reference1 is the only geometry authority; reference2 is approved Daoist Q-style hand-painted finish only, not its UI/objects/letters; reference3 is a native ivory material sample only.
Remove artificial patch-grid discontinuities: target vertical local coordinates {xs}, horizontal local coordinates {ys}. {args.note} These lines are false rectangular material/lighting divisions and tiny stepped contours crossing a single continuous real stone face, gold trim or carved motif. Match the authentic contours above/below and left/right so each bevel and gold line is a single smooth trajectory, without a kink or doubled outline. Keep every genuine grout boundary, slab count, carved shape, gold strip and tiny fitting exactly where it is. Repair all visible false seam segments across the full crop, including wherever the seam reaches a canvas edge. Do not invent grout to hide a seam.
Retain exact original scale, camera, framing, perspective, shape, light direction and palette. Native sharp detail, warm ivory, calm blue-gray stone, thin warm gold and rounded clean bevels. No unrelated repainting, zoom, rotation, crop, stretching, altered patterns, extra objects, characters, writing, UI, borders, sharp white halos, cloud stains, grain, microcracks, blur or sharpening. Preserve outer attachment contours especially accurately; original real structure must exit each edge at precisely the same pixel positions. Maintain existing soft shading while eliminating abrupt rectangular tone bands. Highest available host-managed quality.'''
 refs=[target,REPO/'designs/gameplay-ui/04-guild.png',S/'next_tile_r08_c08/correction-20260923T114016880544Z/native-ivory-material-reference.png']
 req={'prompt':prompt,'referenced_image_paths':[str(p) for p in refs],'transparent_background':False}
 write(d/'request.json',req);(d/'prompt.txt').write_text(prompt,encoding='utf-8');(d/'config.snapshot.json').write_bytes((REPO/'config/image-generation.json').read_bytes())
 write(d/'references.json',[{**info(p),'role':role} for p,role in zip(refs,['exact_native_edit_target','approved_style_only','native_material_only'])])
 write(d/'preparation.json',{'createdAtUtc':now(),'source':info(source),'cropLTRB':box,'context':info(target),'resized':False,'purpose':args.note,'script':info(Path(__file__))})
 print(json.dumps({'directory':str(d),'request':str(d/'request.json'),'context':str(target)},ensure_ascii=False))
def archive(d,expected):
 response=read(d/'tool-response.json');request=read(d/'request.json');hint=response['response']['output_hint'];cached=Path(re.search(r' as (.+?\.png) by default\.',hint,re.S).group(1));native=d/'native.png'
 if not native.exists():
  with cached.open('rb') as a,native.open('xb') as b:shutil.copyfileobj(a,b)
 assert sha(native)==sha(cached)
 with Image.open(native) as im:im.load();pixels=[im.width,im.height];fmt=im.format
 refs=read(d/'references.json')
 for ref in refs:assert sha(ref['file'])==ref['sha256']
 rec={'schemaVersion':1,**info(native),'width':pixels[0],'height':pixels[1],'format':fmt,'generatedAt':None,'recordedAtUtc':now(),
 'observedStartedAtUtc':response['hostObservedStartedAtUtc'],'observedCompletionAtUtc':response['hostObservedFinishedAtUtc'],'tool':'image_gen.imagegen','route':'builtin',
 'configSnapshot':read(d/'config.snapshot.json'),'submittedParameters':{'model':None,'quality':None,'size':None,'transparent_background':False},'actualModel':None,'actualQuality':None,'backendModelVerified':False,
 'unverifiedReason':'Host-managed tool does not expose actual model, quality or server generation time. Raw returned dimensions decoded without local resizing.',
 'request':info(d/'request.json'),'prompt':info(d/'prompt.txt'),'references':refs,'evidence':{'response':info(d/'tool-response.json'),'cachedOriginal':info(cached),'byteIdenticalCopy':True},
 'requestedPixels':expected,'rawReturnedPixels':pixels,'requestedDimensionsMatched':pixels==expected,'localUpscalingPerformed':False,'formalAccepted':False}
 if (d/'preparation.json').exists():rec['editBefore']=read(d/'preparation.json')
 if not (d/'native.png.generation.json').exists():write(d/'native.png.generation.json',rec)
 return native,pixels
def apply(args):
 d=R/args.id;native,pixels=archive(d,[1254,1254]);assert pixels==[1254,1254]
 prep=read(d/'preparation.json');source=Path(prep['source']['file']);assert sha(source)==prep['source']['sha256'];before=image(source);x0,y0,x1,y1=prep['cropLTRB'];context=before[y0:y1,x0:x1];n=image(native)
 assert np.array_equal(context,image(d/'context.png'))
 yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
 all_dist={'left':xx,'right':1253-xx,'top':yy,'bottom':1253-yy};edges=[e for e,keep in [('left',x0>0),('right',x1<4096),('top',y0>0),('bottom',y1<4096)] if keep]
 dist=np.minimum.reduce([all_dist[e] for e in edges]);alpha=np.clip(dist/128.0,0,1);mask=np.rint(alpha*alpha*(3-2*alpha)*255).astype(np.uint8)
 hp=A/'builtin_q64_production/tools/mechanical_join.py';spec=importlib.util.spec_from_file_location('join_existing',hp);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
 joined,flow,tone,reg=helper.registered_join(context,n,mask,edges=tuple(edges),max_shift=4.0,flow_inner=160.0,flow_full=64.0,tone_inner=200.0,tone_full=80.0,match_tone=True)
 after=before.copy();after[y0:y1,x0:x1]=joined;changed=np.any(after!=before,axis=2);allowed=np.zeros((4096,4096),bool);allowed[y0:y1,x0:x1]=mask>0;assert not np.any(changed&~allowed)
 candidate=d/'r08_c07.png';assert not candidate.exists();Image.fromarray(after).save(candidate);Image.fromarray(joined).save(d/'context-after.png');Image.fromarray(mask).save(d/'mask.png');np.save(d/'flow.npy',flow,allow_pickle=False);np.save(d/'tone.npy',tone,allow_pickle=False)
 rects={'return-top':[x0-128,y0-128,x1+128,y0+192],'return-bottom':[x0-128,y1-192,x1+128,y1+128],'return-left':[x0-128,y0-128,x0+192,y1+128],'return-right':[x1-192,y0-128,x1+128,y1+128]};qa=[]
 for label,rect in rects.items():
  l,t,r,b=rect;l=max(0,l);t=max(0,t);r=min(4096,r);b=min(4096,b);p=d/(label+'.png');Image.fromarray(after[t:b,l:r]).save(p);qa.append({'id':label,**info(p),'cropLTRB':[l,t,r,b],'pixels':[r-l,b-t],'resized':False})
 rec={'schemaVersion':1,'createdAtUtc':now(),'candidate':{**info(candidate),'pixels':[4096,4096]},'derivedFrom':[info(source),{**info(native),'generation':info(d/'native.png.generation.json')}],
 'cropLTRB':prep['cropLTRB'],'registration':reg,'mask':{**info(d/'mask.png'),'outerFadePixels':128,'attachedEdges':edges},'flow':info(d/'flow.npy'),'tone':info(d/'tone.npy'),
 'sourceUnchanged':sha(source)==prep['source']['sha256'],'outsideMaskUnchanged':True,'changedPixels':int(changed.sum()),'nativeInputsUpscaled':False,'qa':qa,'script':info(Path(__file__)),'mechanicalHelper':info(hp),
 'formalAccepted':False,'internalAllPassed':False,'runtimeAccepted':False,'tileOuterEdgesChanged':[e for e in ['left','right','top','bottom'] if e not in edges]}
 write(d/'repair.json',rec)
 print(json.dumps({'candidate':str(candidate),'sha256':sha(candidate),'changedPixels':int(changed.sum()),'tileOuterEdgesChanged':rec['tileOuterEdgesChanged']},ensure_ascii=False))
def main():
 ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='mode',required=True)
 p=sp.add_parser('prepare');p.add_argument('--id',required=True);p.add_argument('--source',required=True);p.add_argument('--box',type=int,nargs=4,required=True);p.add_argument('--note',required=True)
 p=sp.add_parser('apply');p.add_argument('--id',required=True)
 p=sp.add_parser('archive-full')
 a=ap.parse_args()
 if a.mode=='prepare':prepare(a)
 elif a.mode=='apply':apply(a)
 else:
  d=R/'full-native-attempt';p,pixels=archive(d,[4096,4096]);write(d/'rejection.json',{'status':'rejected_dimensions_not_native4096','rawPixels':pixels,'requestedPixels':[4096,4096],'candidateUsed':False,'upscaled':False,'note':'Also redrew some carved motifs; not a geometry replacement.'});print(json.dumps({'rawPixels':pixels,'rejected':True}))
if __name__=='__main__':main()
