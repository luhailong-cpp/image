from prepare_repair import *
import argparse

p=argparse.ArgumentParser();p.add_argument('source');args=p.parse_args();source=Path(args.source)
v=HERE/'v6';request=read(v/'repair.request.json');mapping=read(v/'mapping.json')
assert sha(TILE/'native/p14.png')==request['sourceNative']['sha256']
raw=v/'host-result-shifted-canvas.png';assert not raw.exists();im=Image.open(source);assert im.size==(1254,1254) and im.convert('RGBA').getchannel('A').getextrema()==(255,255)
shutil.copyfile(source,raw)
write(str(raw)+'.generation.json',dict(file=str(raw),sha256=sha(raw),generatedAt=datetime.now(timezone.utc).isoformat(),width=1254,height=1254,format='PNG',tool='image_gen.imagegen',route='builtin',configSnapshot=request['configSnapshot'],submittedParameters=request['submittedParameters'],actualModel=None,actualQuality=None,unverifiedReason='Host exposes no model/quality selectors or returned values',evidence={'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'resultId':source.stem},prompt=request['prompt'],promptSha256=request['promptSha256'],references=request['references'],globalWorkCanvasXYWH=mapping['canvasGlobalXYWH'],sourceUpscaled=False,resizedAfterGeneration=False,approvedForPromotion=False,nativeFileModified=False))
prior=HERE/'v5/host-result.png';proposal_pixels=Image.open(prior).convert('RGB');proposal_pixels.paste(im.convert('RGB').crop((0,512,1254,1254)),(0,0))
proposal=v/'proposal-p14.png';proposal_pixels.save(proposal)
write(str(proposal)+'.generation.json',dict(file=str(proposal),sha256=sha(proposal),createdAt=datetime.now(timezone.utc).isoformat(),width=1254,height=1254,format='PNG',globalPatchXYWH=mapping['originalP14GlobalXYWH'],derivedFrom=[ref(raw),ref(prior)],operation=dict(kind='native exact pixel crop and paste of builtin AI repair; no resizing, no feather or extra color transform',sourceCropLTRB=[0,512,1254,1254],destinationXY=[0,0],unchangedPriorRows=[742,1254],mapping=mapping),actualModel=None,actualQuality=None,sourceUpscaled=False,resizedAfterGeneration=False,approvedForPromotion=False,nativeFileModified=False))
sources={};ops=[]
for op in read(TILE/'native/p14.request.json')['contextRegions']:
    assert sha(op['file'])==op['sha256'];sources[op['source']]=np.asarray(Image.open(op['file']).convert('RGB'));ops.append(op)
layout=engine.Layout();context,known=engine.materialize_context(layout,ops,sources);owner=engine.owner_mask(known,['right','top'],layout)
merged,flow,tone,report=engine.register_native(context,np.asarray(proposal_pixels),known,owner,['right','top'],layout,max_shift=6.,tone_cap=18.,return_depth=256)
preview=v/'bounded-preview.png';Image.fromarray(merged).save(preview)
write(str(preview)+'.generation.json',dict(**ref(preview),source=ref(proposal),operation='Diagnostic exact production6/18/256 NE registration; no acceptance',nativeScale=1,formalAccepted=False))
write(v/'diagnostic.json',dict(report=report,source=ref(proposal),preview=ref(preview),formalAccepted=False,automaticVisualPass=False))
for name,box in [('north-join',(0,0,1254,460)),('east-join',(780,0,1254,1254)),('rock-join',(0,0,420,600)),('north-return',(0,250,1139,490)),('east-return',(740,115,1020,1254)),('ne-corner',(894,0,1254,360)),('repair-paste-boundary',(0,582,1254,902))]:
    path=v/('qa-'+name+'.png');Image.fromarray(merged).crop(box).save(path)
    write(str(path)+'.generation.json',dict(**ref(path),source=ref(preview),operation={'cropLTRB':box},nativeScale=1,actuallyViewed=False,formalAccepted=False))
write(v/'proposal-pending.json',dict(createdAt=datetime.now(timezone.utc).isoformat(),nativeSource=request['sourceNative'],proposal=ref(proposal),hostShiftedCanvas=ref(raw),preview=ref(preview),approvedForPromotion=False,nativeFileModified=False,actuallyViewed=False))
print(json.dumps({'proposal':str(proposal),'sha256':sha(proposal),'rawSupportMax':report['rawSupportMaxDisplacementVector'],'clippedSupportFraction':report['clippedSupportFraction']}))
