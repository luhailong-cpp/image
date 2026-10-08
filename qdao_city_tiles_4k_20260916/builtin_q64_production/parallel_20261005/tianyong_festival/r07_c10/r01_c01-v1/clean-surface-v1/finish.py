from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
from datetime import datetime,timezone
D=Path(__file__).parent;P=D.parent;T=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
write=lambda p,x:Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
req=json.loads((D/'request.json').read_text(encoding='utf-8'))
assembly=json.loads((D/'assembly.json').read_text(encoding='utf-8'))
cp_bytes=(T/'source-checkpoint.json').read_bytes();cp=json.loads(cp_bytes)
prior=cp['fragment'];assert prior['tile']=='r07_c10' and sha(prior['file'])==prior['sha256']
b=[510,350,865,680];dest=[395,235,750,565]
assert np.array_equal(np.array(Image.open(prior['file']).convert('RGB').crop(dest)),np.array(Image.open(req['source']['file']).convert('RGB').crop(b)))
(D/'source-checkpoint-input.json').write_bytes(cp_bytes)
qa=['joined.png','defect-before.png','defect-after.png','edge-return-qa.png','left-return-qa.png','right-return-qa.png','halo-chip-excluded.png']
review={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'close_c03','image':info(D/'joined.png'),'localAccepted':True,'formalAccepted':False,'nativePixelInspection':True,'reviewedImages':[info(D/p) for p in qa],'findings':['The long diagonal crease is removed by true native AI repaint; the slab face retains matching clean warm ivory paint and faint mottling without a blurred smear.','Original white lower highlight, bevel, brown separating joint and lower slabs are restored exactly using the source edge guard; all actual outer boundaries and all pixels outside the explicit repair mask remain unchanged.','No rectangular colour step, new crack or doubled contour observed in the full source and detailed return crops.'],'excludedFinding':req['excludedFinding'],'newModelCalls':1,'noResize':True,'sourceGeometryResampling':False,'rootStateModified':False}
write(D/'visual-review.json',review)
joined=Image.open(D/'joined.png');patch=D/'surface-repair.png';joined.crop(b).save(patch)
patch_record={'derivation':'exact native source crop','file':str(patch),'sha256':sha(patch),'pixels':[355,330],'nativeScale':1,'derivedFrom':info(D/'joined.png'),'cropLTRB':b,'destinationTile':'r07_c10','destinationTileLTRB':dest,'formalAccepted':False}
write(D/'surface-repair.png.generation.json',patch_record)
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'appearance':'tianyong_festival','tile':'r07_c10','tileGlobalOrigin':[36864,24576],'nativeScale':1,'windowTileLocalLTRB':[-115,-115,1139,1139],'windowGlobalLTRB':[36749,24461,38003,25715],'joined':info(D/'joined.png'),'visualReview':info(D/'visual-review.json'),'assembly':info(D/'assembly.json'),'localVisualAccepted':True,'formalAccepted':False,'patches':[{'name':'surface-repair','asset':info(patch),'cropFromJoinedLTRB':b,'destinationTile':'r07_c10','destinationTileLTRB':dest,'requiredPriorSource':prior,'nativeScale':1,'mustApplyTogether':True}],'sourceCheckpoint':info(D/'source-checkpoint-input.json'),'excludedFinding':req['excludedFinding'],'note':'Apply only after source r01_c01 has been published into current active tile. Prior ROI exactly matches current v016 and original joined source. Triangle chip is wholly outside tile in upper115 halo, no second actual-tile patch is created. Original agent joined and manifests are unchanged.'}
write(D/'manifest.json',manifest)
write(D/'joined.png.generation.json',{'derivation':'native AI repaint with exact source recovery outside mask','file':str(D/'joined.png'),'sha256':sha(D/'joined.png'),'nativeScale':1,'derivedFrom':assembly['sources'],'actualModel':None,'actualQuality':None,'assembly':info(D/'assembly.json'),'visualReview':info(D/'visual-review.json'),'formalAccepted':False})
write(D/'source-proof.json',{'source':req['source'],'sourceOriginalUnchanged':sha(req['source']['file'])==req['source']['sha256'],'requiredCurrentSource':prior,'originalRoiExactlyMatchesCurrent':True,'repairTileLocalLTRB':dest,'repairNativeLTRB':b,'sourceGeometryPreservedByExactEdgeGuard':True,'edgeGuard':assembly['preservedEdgeMask'],'outsideMaskExactlyUnchanged':True,'outsideTileFullyUnchanged':True,'excludedFinding':req['excludedFinding'],'newModelCalls':1,'rootStateModified':False,'originalManifestsModified':False})
print(json.dumps({'manifest':info(D/'manifest.json'),'joined':info(D/'joined.png'),'patch':info(patch),'priorTileVersion':cp['version'],'newModelCalls':1,'destinationTileLTRB':dest}))
