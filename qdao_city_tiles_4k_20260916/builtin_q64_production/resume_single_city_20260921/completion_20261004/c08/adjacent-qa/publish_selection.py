from pathlib import Path
from PIL import Image
import json,hashlib,datetime,numpy as np
R=Path(__file__).resolve().parent;sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
rec=json.loads((R/'coupled-v2-bindings.json').read_text());sources=rec['sources'];O=R/'coupled-v2'
def dump(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
# Fill individual derivation records for prior mechanical intermediates without inventing AI version.
for fn in ['tone-bindings.json','tone-v2-bindings.json','coupled-v1-bindings.json']:
 manifest=json.loads((R/fn).read_text())
 for k,v in manifest['sources'].items():
  p=Path(v['file']);g=Path(str(p)+'.generation.json')
  if not g.exists():dump(g,{'file':str(p),'sha256':v['sha256'],'exportPixels':v['pixels'],'recordedAtUtc':stamp,'derivedFrom':[manifest['derivedFrom'][k]],'operation':manifest['operation'],'assemblyManifest':str(R/fn),'actualModel':None,'actualQuality':None,'unverifiedReason':'Mechanical derivative; source model/quality remain as recorded in source history.'})
for k,v in sources.items():
 p=Path(v['file']);assert sha(p)==v['sha256'];assert Image.open(p).size==(4096,4096)
 g=Path(v['generationRecord']);d=json.loads(g.read_text())
 d['derivedFrom'][0]['generationRecord']=d['derivedFrom'][0]['file']+'.generation.json';dump(g,d)
for name in ['gold-top','corner-left','corner-right']:
 p=R/name/'native.png';g=Path(str(p)+'.generation.json');d=json.loads(g.read_text());d['width']=1254;d['height']=1254;d['format']='PNG'
 d['references'][0]['role']='native edit target, exact shared tile boundary context';d['evidence']['receiptHasActualModel']=False;d['evidence']['receiptHasActualQuality']=False;dump(g,d)
entries=[]
for p in sorted((O/'qa').glob('*.png')):
 entries.append({'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size),'inspectedAtNativePixels':True,'viewImageDetail':'original'})
for name in ['gold-top','corner-left','corner-right']:
 p=O/name/'perimeter.png';entries.append({'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size),'inspectedAtNativePixels':True,'viewImageDetail':'original'})
limits=[
 {'id':'old-material-step-west-upper','between':['r08_c07','r08_c08'],'coordinates':'shared x4096, row8 local y approximately930..1200','finding':'Visible pre-existing ivory/slate material and luminance step outside the three repair windows. Requires structural redraw, not acceptance by colour metrics.'},
 {'id':'old-corner-return-continuation','coordinates':'corner-left perimeter: x4096 near y3370; y4096 west of x3469; corner-right perimeter: x8192 near y3309','finding':'Old fine contour/colour discontinuities remain outside repaired corner interiors; repairs pass their central intersections but the complete borders do not.'},
 {'id':'old-east-lower-small-line','between':['r09_c08','r09_c09'],'coordinates':'row9 local y around1750..1850, thin highlight crossing','finding':'Small pre-existing discontinuity remains in ivory trim, not part of three repaired windows.'},
 {'id':'external-neighbours-and-runtime','finding':'Outer border neighbours, wholecity256 tiles, complete internal seam re-audit and nearest-camera runtime validation are not covered by this checkpoint.'}
]
review={'reviewedAtUtc':stamp,'reviewer':'finish_shared_edges','sources':sources,'nativeQa':entries,'actuallyViewedCounts':{'verticalFull4096Borders':4,'horizontalFull4096Borders':3,'fourTileJunctions1254':2,'repairPerimeterBoards':3},'passedRepairScopes':['gold-top: broken gold rim near central x627,y350 repaired; genuine gold slab division retained','corner-left: central cross and bevel continuity repaired; diagonal real slab joints retained','corner-right: central circular slate outline and cross repaired; genuine slanted paving division retained'],'registration':[{ 'name':r['name'],**r['registration']} for r in rec['repairs']],'fullSevenBordersAccepted':False,'remainingLimitations':limits,'formalAccepted':False,'wholeCityComplete':False}
dump(O/'visual-review.json',review)
preview=Image.new('RGB',(1536,1024))
for k,v in sources.items():
 rr=int(k[1:3])-8;cc=int(k[5:])-7
 preview.paste(Image.open(v['file']).resize((512,512),Image.Resampling.LANCZOS),(cc*512,rr*512))
preview.save(O/'overview-only.png')
selection={'updatedAtUtc':stamp,'status':'current_coupled_six_wip_ready_for_continuation','sources':sources,'selectedTiles':sources,'sourceManifest':str(R/'coupled-v2-bindings.json'),'visualReview':str(O/'visual-review.json'),'overview':str(O/'overview-only.png'),'allOutputsVerified4096Square':True,'wholeCityComplete':False,'formalAccepted':False,'completedNew4KTiles':0,'newBuiltinCallsThisResumption':2,'recoveredBuiltinReturnCalls':1,'actualModel':None,'actualQuality':None,'targetConfiguration':json.loads((R.parent/'config.snapshot.json').read_text()),'remainingLimitations':limits,'writeOwnership':{'owner':'finish_shared_edges','state':'released','scope':'completion_20261004/c08/adjacent-qa only','releasedAtUtc':stamp},'notes':['These six outputs form one coupled selection; do not mix individual older candidates into this local patch set.','Global pointers and independent expansion directory were not modified.','All three native AI outputs were preserved byte-identically in project and contain actual version/quality unknown evidence.']}
dump(R/'current-selection.json',selection)
print(json.dumps({'selection':str(R/'current-selection.json'),'qaBoardsInspected':len(entries),'verifiedTiles':len(sources),'formalAccepted':False},indent=2))
