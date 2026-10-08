from prepare_repair import *
import argparse

p=argparse.ArgumentParser();p.add_argument('source');args=p.parse_args()
source=Path(args.source);request=read(HERE/'repair.request.json')
assert sha(TILE/'native/p14.png')==request['sourceNative']['sha256'],'Native changed before proposal save'
image=Image.open(source);assert image.size==(1254,1254) and image.convert('RGBA').getchannel('A').getextrema()==(255,255)
raw=HERE/'host-result.png';assert not raw.exists();shutil.copyfile(source,raw)
record=dict(file=str(raw),sha256=sha(raw),generatedAt=datetime.now(timezone.utc).isoformat(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=request['configSnapshot'],submittedParameters=request['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host tool exposes no model/quality selectors or returned model/quality metadata',evidence={'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'resultId':source.stem},prompt=request['prompt'],promptSha256=request['promptSha256'],references=request['references'],sourceUpscaled=False,resizedAfterGeneration=False,approvedForPromotion=False,nativeFileModified=False)
write(str(raw)+'.generation.json',record)
# The proposal changes only the authorized hole pixels. Exact original draft pixels outside
# those holes, and exact real incoming neighbor context, are mechanically protected.
target=np.asarray(Image.open(HERE/'actual-context-target.png').convert('RGB')).copy()
new=np.asarray(image.convert('RGB'));mask=np.zeros((1254,1254),bool)
for x0,y0,x1,y1 in request['transparentRepairRectsLTRB']:mask[y0:y1,x0:x1]=True
target[mask]=new[mask]
proposal=save_image('proposal.png',target,dict(kind='Binary exact AI fill compositing; no blend/warp; only documented L-shaped inpaint pixels adopted',adoptedRectanglesLTRB=request['transparentRepairRectsLTRB'],outsideRepairUnchanged=True),[ref(raw),ref(HERE/'actual-context-target.png')])
sources={};ops=[]
for op in read(TILE/'native/p14.request.json')['contextRegions']:
    sources[op['source']]=np.asarray(Image.open(op['file']).convert('RGB'));ops.append(op)
layout=engine.Layout();context,known=engine.materialize_context(layout,ops,sources);owner=engine.owner_mask(known,['right','top'],layout)
merged,flow,tone,report=engine.register_native(context,target,known,owner,['right','top'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
preview=save_image('proposal-bounded-registration-preview.png',merged,{'kind':'Exact6/18/256 diagnostic only, actual native incoming context protected'},[ref(proposal)]+request['references'])
np.save(HERE/'proposal-diagnostic.flow.npy',flow);np.save(HERE/'proposal-diagnostic.tone.npy',tone)
write(HERE/'proposal-diagnostic.json',dict(report=report,proposal=ref(proposal),preview=ref(preview),formalAccepted=False,automaticVisualPass=False))
for name,box in [('north-join',(0,0,1254,460)),('east-join',(780,0,1254,1254)),('rock-join',(0,0,420,600)),('north-return',(0,250,1139,490)),('east-return',(740,115,1020,1254))]:
    save_image('qa-'+name+'.png',Image.fromarray(merged).crop(box),{'cropLTRB':box,'nativeScale':1,'diagnosticPreview':True},[ref(preview)])
write(HERE/'proposal-pending.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),nativeSource=request['sourceNative'],proposal=ref(proposal),hostResult=ref(raw),preview=ref(preview),approvedForPromotion=False,nativeFileModified=False,actuallyViewed=False))
print(json.dumps({'proposal':str(proposal),'sha256':sha(proposal),'hostSourceSaved':str(raw),'nativeFileModified':False}))
