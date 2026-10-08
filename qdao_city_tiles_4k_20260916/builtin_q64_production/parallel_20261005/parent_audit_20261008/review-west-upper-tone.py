from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,numpy as np
A=Path(__file__).resolve().parent;T=A.parent/'parent_repairs_20261008/west-upper-tone'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'path':Path(p).as_posix(),'sha256':sha(p)}
def rgb(p):return np.array(Image.open(p).convert('RGB'))
mp=T/'final-manifest.json';M=json.loads(mp.read_text(encoding='utf-8-sig'));mh=sha(mp)
J=rgb(M['joined']['file']);assert sha(M['joined']['file'])==M['joined']['sha256']
context=rgb(T/'context.png');mask=np.array(Image.open(T/'mask.png').convert('L'));tm=np.array(Image.open(T/'trim-mask.png').convert('L'))
outside=(mask==0)&(tm==0);assert np.array_equal(J[outside],context[outside])
qs=[]
for q in M['qa']:
    assert sha(q['file'])==q['sha256'];l,t,r,b=q['cropLTRB'];assert np.array_equal(rgb(q['file']),J[t:b,l:r])
    qs.append(dict(q,actuallyViewed=True,method='tools.view_image(detail=original)',result='no_actionable_new_discontinuity_in_this_view'))
outputs=[];joined=Image.new('RGB',(1254,1254))
for o in M['outputs']:
    assert sha(o['file'])==o['sha256'];assert sha(o['source']['file'])==o['source']['sha256']
    src=rgb(o['source']['file']);out=rgb(o['file']);assert out.shape==(4096,4096,3)
    l,t,r,b=o['source']['cropLTRB'];outside=np.ones((4096,4096),dtype=bool);outside[t:b,l:r]=False
    assert np.array_equal(src[outside],out[outside])
    changed=int(np.any(src!=out,axis=2).sum());assert changed==o['changedPixels']
    joined.paste(Image.fromarray(out[t:b,l:r]),tuple(o['source']['pasteXY'][:2]))
    outputs.append({'image':ref(o['file']),'baseSource':ref(o['source']['file']),'outsideWindowExactlyUnchanged':True,'changedPixels':changed,'windowLTRB':[l,t,r,b]})
assert np.array_equal(np.array(joined),J);assert sha(mp)==mh
R={'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewer':'independent publish48 agent','sourceManifest':{'path':mp.as_posix(),'sha256':mh},'joined':ref(M['joined']['file']),'result':'pass_requested_local_scopes','actuallyViewedOriginalPixelImages':9,'qa':qs,'findings':[
{'id':'gray-material-common-line','locationInJoined':'x627, gray slab y340..850','finding':'Original straight vertical light/dark split is absent in gray-upper, gray-lower and full joined. A continuous softly brushed gray surface remains, without a new hard patch boundary in these views.'},
{'id':'gold-highlight-step','locationInJoined':'x627, y255 approximately','finding':'Diagonal gold/ivory band and its bright bevel traverse the former shared boundary continuously; the highlighted contour no longer shows the previous step in diagonal-trim.'},
{'id':'mask-returns','locationInJoined':'The eight recorded cropLTRB rectangles','finding':'Upper relief, diagonal/lower trim and left/right/bottom returns show no actionable new return-edge cut, duplicated contour or abrupt rectangular tone patch. Gold bands and dark grooves remain coherent.'}],
'mechanicalBindingChecks':{'qaCropsExactlyEqualJoined':True,'joinedExactlyReconstructedFromFinal4KTiles':True,'outsideBothAlphaMasksUnchangedInJoined':True,'sourceOutputs':outputs},'scope':'Only this1254 window and listed8 native QA crops. No acceptance of complete shared4096 edge, entire4K tile, whole city, navigation or client. Parent current selection remains untouched pending root final review.','formalAccepted':False,'wholeCityComplete':False,'childFilesModified':False,'parentIndexModified':False,'newCompleteCoordinates':0}
out=A/'west-upper-tone-independent-review.json';out.write_text(json.dumps(R,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'result':R['result'],'file':out.as_posix(),'sha256':sha(out),'imagesActuallyViewed':9,'mechanicalChecksPassed':True},ensure_ascii=False))
