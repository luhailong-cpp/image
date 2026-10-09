from pathlib import Path
from datetime import datetime,timezone
import sys,json,hashlib,shutil
import numpy as np
from PIL import Image
D=Path(__file__).resolve().parent;T=D.parent;OWN=T.parent
STARTS=[0,1024,2048,2842];X0=3469;X1=4723
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,v):
 p=Path(p);assert p.resolve().is_relative_to(D.resolve());p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def save(p,im,m):
 p=Path(p);assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);im.save(p);e={**ref(p),'pixels':list(im.size),**m};write(str(p)+'.generation.json',e);return e
def freeze():
 cp=D/'source-contract.json'
 if cp.exists():print(json.dumps(ref(cp)));return
 c15=read(T/'source-contract-v2/source-contract.json')['dayGeometrySnapshot']['snapshot']
 specs=[('day-c14',OWN.parent/'donghai_day/tiles/r08_c14.png','ed9ff4e38f96a1ad32a42fb185e4bc841626dea6add65f1d9bcfc899e79140e8'),('day-c15',Path(c15['file']),'70ce623a54fb8419b951b7372a88e95db2c8b5ae9e04845c2af2c1fd18312585'),('festival-c14',OWN/'r08_c14/west-final-v2/output/r08_c14.png','753b6304ec0a2721a62a03dcc20b19893a01365539878a64f9984a8ffa3629c4'),('festival-c15',T/'repairs/approved-sync-final/output/r08_c15.png','3d0b9871e8c95c88d0e9852f17b8dc9ae84c6c746f48605ac7c98628b67f2e25')]
 sources=[];ims={}
 for key,p,digest in specs:
  assert sha(p)==digest,(key,str(p));im=Image.open(p).convert('RGB');assert im.size==(4096,4096)
  dest=D/'snapshots'/(key+'.png');dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,dest);assert sha(dest)==digest
  sources.append({'id':key,'authority':ref(p),'snapshot':ref(dest)});ims[key]=im
  rec=Path(str(p)+'.generation.json')
  if rec.exists():shutil.copyfile(rec,D/'snapshots'/(key+'.source-generation.json'))
 guides=[]
 for i,y in enumerate(STARTS,1):
  pairrect=[3469,y,4723,y+1254];globalrect=[53248+3469,28672+y,53248+4723,28672+y+1254]
  item={'id':f's{i}','pairRectXYXY':pairrect,'globalRectXYXY':globalrect,'c14RectXYXY':[3469,y,4096,y+1254],'c15RectXYXY':[0,y,627,y+1254]}
  for kind in ['day','festival']:
   guide=Image.new('RGB',(1254,1254));guide.paste(ims[kind+'-c14'].crop((3469,y,4096,y+1254)),(0,0));guide.paste(ims[kind+'-c15'].crop((0,y,627,y+1254)),(627,0))
   item[kind]=save(D/'guides'/f'{kind}-s{i}.png',guide,{'operation':'unaltered same-window neighboring-tile pixel concatenation','pairRectXYXY':pairrect,'globalRectXYXY':globalrect,'resized':False,'sourceIds':[kind+'-c14',kind+'-c15']})
  guides.append(item)
 contract={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceKind':'independent OWN contract from current frozen DAY tile pixels; no pre-existing DAY c14/c15 shared-edge mask replay is claimed','sources':sources,'guides':guides,'pairPixels':[8192,4096],'authorizedPairRectXYXY':[3469,0,4723,4096],'patchYStarts':STARTS,'overlaps':[230,230,460],'frozenDaySharedEdgeNativeExists':False,'DAYSharedEdgeMasksApplied':False,'plannedIntegration':'Own native-pixel seams selected from generated patch overlap costs; own masks saved with exact pixels; optional bounded RGB difference fields max24; no warp or art resampling','geometryAuthority':'Frozen DAY c14 published current tile and c15 verified approved snapshot only','style':ref(Path('D:/work/image/designs/gameplay-ui/04-guild.png')),'DAYWritten':False,'globalRegistryModified':False,'formalAccepted':False}
 write(cp,contract);print(json.dumps(ref(cp)))
def prepare(i):
 contract=read(D/'source-contract.json');g=contract['guides'][i-1];R=D/'requests'/g['id'];req=R/'request.json'
 if req.exists():print(json.dumps(read(req)));return
 refs=[{**g['festival'],'role':'edit target: true c14/c15 festival same-window pixels, seam at x627'},{**g['day'],'role':'sole scene geometry authority, same-window DAY raw pixels; no day color transfer'},{**contract['style'],'role':'confirmed Q game-art style only; no UI content'}]
 if i>1:
  p=D/'native'/f's{i-1}.png';assert p.exists(),'Complete previous vertical native for real overlap continuity first'
  overlap=1254-(STARTS[i-1]-STARTS[i-2]);crop=[0,1254-overlap,1254,1254]
  ep=save(D/'guides'/f'previous-overlap-s{i}.png',Image.open(p).convert('RGB').crop(crop),{'derivedFrom':ref(p),'cropXYXY':crop,'resized':False,'role':'true overlapping previous bottom strip only'})
  refs.append({**ep,'role':f'previous native exact bottom {overlap}px strip; aligns only to target top {overlap}px; never add objects'})
 detail=''
 if i<=2:detail=' Explicit limited exception to unchanged geometry: the DAY and festival source themselves contain an impossible material splice where the left wooden horizontal bar ends abruptly at crop x627 and the right braided mooring rope begins, at world tile y990..1175. Within pair x3990..4230, y950..1240 only, render a small physically plausible rope tie/termination around the existing wooden bar end so the existing bar and existing rope connect naturally. Keep the outside endpoints, broad silhouette and scene occupancy fixed; do not extend a new rope across the whole bar or add a new object. This local source defect is separately recorded as DAY geometry synchronization pending. In this crop the affected y range is '+str(950-STARTS[i-1])+'..'+str(1240-STARTS[i-1])+'.'
 if i>=3:detail=' Remove the artificial near-horizontal water image-crop line at world tile y3187 near crop x627..755 (local y='+str(3187-STARTS[i-1])+') if visible. Continue natural rounded water ripples and warm reflected strokes across that line.'
 prompt='Use case: lighting-weather. Asset type: one native 1254 by 1254 Lantern Festival city-map common-edge repair. Image 1 is the exact current festival scene from two neighboring tiles joined at crop x627; image 2 is the sole DAY geometry authority at precisely the same world coordinates. Repaint only lighting, color and hand-painted brushwork to remove the artificial vertical tile-color/paint boundary at x627 and harmonize both sides into one continuous scene. Preserve every DAY object, board joint, rope coil, edge coordinate, silhouette, water boundary, shadow contour, barrel, timber, perspective and camera framing. Keep the scene continuous, and retain festival royal-blue water and painted wood, rich orange timber and soft gold/pink lantern reflections rather than restoring daytime cyan. Remove any abrupt copied-image cutoff, thin splice line, block-shaped color step or sawtooth that is not a real object edge. Do not invent geometry or extra objects.'+detail+' Image 3 is only the confirmed clean, rounded, rich Daoist Q hand-painted style reference. '+('Image 4 is the previous native window above; align colors and the true vertical overlap without shifting any feature.' if i>1 else '')+' Do not add text, UI, lanterns, props, a horizon, blur, global tint, outlines, sharpened seams, warped geometry, scale changes or zoom. Preserve the exact 1254 by 1254 field of view and return one opaque native image. Only local color/paint continuity may change; genuine geometry from the DAY same-window reference is fixed.'
 R.mkdir(parents=True,exist_ok=True);(R/'prompt.txt').write_text(prompt,encoding='utf8');write(R/'references.json',refs);write(req,{'prompt':prompt,'referenced_image_paths':[e['file'] for e in refs],'transparent_background':False});write(R/'prepared.json',{'sourceContract':ref(D/'source-contract.json'),'guide':g,'references':refs,'prompt':ref(R/'prompt.txt'),'geometryChangeAllowed':i<=2,'geometryException':{'pairRectXYXY':[3990,950,4230,1240],'reason':'Existing source wooden-bar/rope splice; retain endpoints and footprint','DAYSyncPending':True} if i<=2 else None});print(json.dumps(read(req)))
def record(i,raw):
 p=D/'native'/f's{i}.png';raw=Path(raw);assert not p.exists();im=Image.open(raw);assert im.size==(1254,1254);p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(raw,p)
 active=read(D/'active-requests.json') if (D/'active-requests.json').exists() else {}
 R=D/'requests'/active.get(f's{i}',f's{i}');prepared=read(R/'prepared.json');request=read(R/'request.json')
 write(str(p)+'.generation.json',{**ref(p),'pixels':[1254,1254],'createdAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin','tool':'image_gen.imagegen','configSnapshot':read(OWN/'batch-model-check.json')['configSnapshot'],'submittedParameters':{'model':None,'quality':None,**request},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin exposes no model/quality selectors or return metadata.','prompt':ref(R/'prompt.txt'),'request':ref(R/'request.json'),'references':read(R/'references.json'),'sourceContract':prepared['sourceContract'],'pairRectXYXY':prepared['guide']['pairRectXYXY'],'globalRectXYXY':prepared['guide']['globalRectXYXY'],'evidence':{'toolResultSourcePath':str(raw),'toolResultSha256':sha(raw)},'resizedAfterGeneration':False,'finalArtUpscaled':False,'geometryChangeAllowed':prepared['geometryChangeAllowed'],'geometryException':prepared.get('geometryException')})
 print(json.dumps(ref(p)))
if __name__=='__main__':
 action=sys.argv[1]
 if action=='freeze':freeze()
 elif action=='prepare':prepare(int(sys.argv[2]))
 elif action=='record':record(int(sys.argv[2]),sys.argv[3])
