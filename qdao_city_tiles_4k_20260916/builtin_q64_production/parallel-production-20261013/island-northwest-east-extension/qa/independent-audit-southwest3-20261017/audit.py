from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib,datetime,sys
R=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/island-game-20261009/southwest')
O=Path(__file__).resolve().parent
tile=sys.argv[1]; bound={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def bind(p,h=None):
 p=Path(p);v=sha(p);assert h is None or v==h,str(p);bound[str(p)]={'path':str(p),'sha256':v};return v
def read(p,h=None):bind(p,h);return json.loads(Path(p).read_text(encoding='utf-8-sig'))
mp=R/'current-native-map.json';m=read(mp);art=m['candidateArtifacts'][tile];rp=Path(art['sourceReport']);d=read(rp)
candidate=Path(art['path']);bind(candidate,art['sha256']);co=np.array(Image.open(candidate).convert('RGB'));assert co.shape==(4096,4096,3)
mo=next(x for x in d['outputs'] if x['path'].endswith('-source-id-mask.png'));bind(mo['path'],mo['sha256']);mask=np.array(Image.open(mo['path']));assert mask.shape==(4096,4096)
inputs=d['inputs'];assert set(np.unique(mask))==set(x['sourceId'] for x in inputs)
base=[x for x in inputs if 'row'in x and 'column'in x];assert len(base)==16;assert {(x['row'],x['column']) for x in base}=={(y,x) for y in range(1,5) for x in range(1,5)}
selectedMatch=all(m[tile][x['row']-1][x['column']-1]==x['stem'] for x in base);assert selectedMatch
tx,ty,_,_=d['candidateGlobalBox'];src=[]
for x in inputs:
 bind(x['path'],x['sha256']);g=read(x['record'],x['recordSha256']);assert g['sha256']==x['sha256'];im=np.array(Image.open(x['path']).convert('RGB'));assert im.shape==(1254,1254,3)
 ys,xs=np.nonzero(mask==x['sourceId']);sx=xs+tx-x['nativeGlobalBox'][0];sy=ys+ty-x['nativeGlobalBox'][1];assert sx.min()>=0 and sy.min()>=0 and sx.max()<1254 and sy.max()<1254;assert np.array_equal(co[ys,xs],im[sy,sx]),x['stem']
 src.append({**x,'actualDimensions':[1254,1254],'contributedPixels':int(len(xs)),'exactSameGlobalCoordinatePixels':True,'generationHashBinding':True})
review=None
if art.get('review'):review=read(art['review'])
current=read(mp);matches=current[tile]==m[tile] and current['candidateArtifacts'][tile]['path']==art['path'] and current['candidateArtifacts'][tile].get('sha256')==art['sha256'];mutated=[p for p,x in bound.items() if sha(p)!=x['sha256']]
report={'auditedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tile':tile,'classification':'old candidate newly independently verified; no new generation','candidate':bound[str(candidate)],'originalAssemblyTimeUtc':d['createdAtUtc'],'sourceReport':bound[str(rp)],'sourceIdMask':bound[str(Path(mo['path']))],'currentNativeMap':bound[str(mp)],'uniqueCorePositions':16,'nativeSourceCount':len(inputs),'allNative1254':True,'sameCoordinateIntegerPixelReplay':True,'resampling':False,'baseSelectionMatches':selectedMatch,'currentArtifactMatches':matches,'mutatedInputs':mutated,'canCountCompleteCandidate':matches and not mutated,'internalPass':False,'formalAccepted':False,'qaStateFromCurrentArtifact':art,'sources':src,'boundInputs':list(bound.values()),'note':'Exact 4096 coverage from native sources verified through source-id mask, including any native repair overlay. This mechanical audit does not certify visual geometry, joins or internal acceptance.'}
f=O/(tile+'-audit-v1.json');assert not f.exists();f.write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'tile':tile,'canCount':report['canCountCompleteCandidate'],'originalAssemblyTimeUtc':d['createdAtUtc'],'candidateSha256':art['sha256'],'report':str(f),'reportSha256':sha(f),'sourceReportSha256':sha(rp),'nativeSources':len(inputs),'bindings':len(bound)}))

