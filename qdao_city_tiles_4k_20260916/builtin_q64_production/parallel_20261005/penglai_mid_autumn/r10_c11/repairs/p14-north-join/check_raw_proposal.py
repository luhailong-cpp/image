from prepare_repair import *

sources={};ops=[]
for op in read(TILE/'native/p14.request.json')['contextRegions']:
    sources[op['source']]=np.asarray(Image.open(op['file']).convert('RGB'));ops.append(op)
layout=engine.Layout();context,known=engine.materialize_context(layout,ops,sources);owner=engine.owner_mask(known,['right','top'],layout)
raw=HERE/'host-result.png';pixels=np.asarray(Image.open(raw).convert('RGB'))
merged,flow,tone,report=engine.register_native(context,pixels,known,owner,['right','top'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
preview=save_image('host-direct-bounded-preview.png',merged,{'kind':'Diagnostic exact6/18/256 applied to untouched AI host result; not binary local mask proposal'},[ref(raw)])
write(HERE/'host-direct-diagnostic.json',dict(report=report,preview=ref(preview),formalAccepted=False,automaticVisualPass=False))
for name,box in [('north-join',(0,0,1254,460)),('east-join',(780,0,1254,1254)),('rock-join',(0,0,420,600)),('north-return',(0,250,1139,490)),('east-return',(740,115,1020,1254))]:
    save_image('qa-host-direct-'+name+'.png',Image.fromarray(merged).crop(box),{'cropLTRB':box,'nativeScale':1,'diagnosticPreview':True},[ref(preview)])
print(json.dumps({'preview':str(preview),'report':report}))
