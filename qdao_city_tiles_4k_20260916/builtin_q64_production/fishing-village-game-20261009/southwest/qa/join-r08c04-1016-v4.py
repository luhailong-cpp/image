import sys,json,hashlib,datetime,importlib.util
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
z=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/fishing-village-game-20261009/southwest');q=z/'qa';pre='join-r08c04-1016-v4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ref(p):return {'path':p.as_posix(),'sha256':sha(p)}
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def png(name,a):
 p=q/(pre+'-'+name+'.png');assert not p.exists();Image.fromarray(a).save(p);assert np.array_equal(np.asarray(Image.open(p)),a);return dict(ref(p),size=[a.shape[1],a.shape[0]])
base=q/'repair-r08c04-1016-v3-trace.json';bt=rd(base);corner=q/'west-corner-r08r09c04c05-v3-export-trace.json'
inp=[('r08_c04',Path(bt['context']['path']),bt['context']['sha256']),('r08_c05',q/'west-corner-r08r09c04c05-v3-r08_c05-context-native.png','036a7b4f61ed34de0bd15176dea4bba12c3a83d3b6471122485313309bae8ea8'),('r09_c04',q/'west-corner-r08r09c04c05-v3-r09_c04-context-native.png','ad64f8dd37b6227a09753a160ec8d58a047d45fb334ecbef03e2c2fa1ee88fe3'),('r09_c05',q/'west-corner-r08r09c04c05-v3-r09_c05-context-native.png','8596cd1b265fd45a5de5a98b80adfa5e8e5f842cbcb875160dc384f013c6ce0c')]
a=[]
for tile,p,s in inp:
 assert sha(p)==s;ar=np.asarray(Image.open(p).convert('RGB')).copy();assert ar.shape==(4326,4326,3);a.append(ar)
original,e,s,se=a;target=original.copy();eo=e.copy();so=s.copy()
hp=z/'tools/seam_helpers.py';sp=importlib.util.spec_from_file_location('join_seams',hp);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod)
ep=mod._minimum_vertical_seam(target[:,4096:4211],e[:,:115]);emask=np.arange(230)[None,:]>=ep[:,None]
target[:,4096:4326]=np.where(emask[:,:,None],e[:,:230],target[:,4096:4326]);e[:,:115]=target[:,4096:4211]
spth=mod._minimum_vertical_seam(target[4096:4211].transpose(1,0,2),s[:115].transpose(1,0,2));smask=np.arange(230)[:,None]>=spth[None,:]
target[4096:4326]=np.where(smask[:,:,None],s[:230],target[4096:4326]);s[:115]=target[4096:4211]
e[:,:115]=target[:,4096:4211]
assert np.array_equal(target[:,4096:4326],e[:,:230]),'East halo mismatch'
assert np.array_equal(target[4096:4326],s[:230]),'South halo mismatch'
assert np.array_equal(e[115:4211,115:4211],eo[115:4211,115:4211])
assert np.array_equal(s[115:4211,115:4211],so[115:4211,115:4211])
assert np.array_equal(e[4096:4326],se[:230]),'Existing c05 horizontal overlap changed'
assert np.array_equal(s[:,4096:4326],se[:,:230]),'Existing r09 vertical overlap changed'
# Every selected target pixel is exactly from one of the three source contexts.
ids=np.zeros((4326,4326),np.uint8);ids[:,4096:4326][emask]=1;ids[4096:4326][smask]=2
assert np.array_equal(target[ids==0],original[ids==0])
for i,src,box in [(1,eo[:,:230],[4096,0,4326,4326]),(2,so[:230],[0,4096,4326,4326])]:
 l,t,r,b=box;chosen=ids[t:b,l:r]==i;assert np.array_equal(target[t:b,l:r][chosen],src[chosen])
nid=q/(pre+'-source-ids.npy');assert not nid.exists();np.save(nid,ids,allow_pickle=False)
trace={'schemaVersion':1,'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'pending_visual_qa','inputs':[{'tile':tile,'context':{'path':p.as_posix(),'sha256':h}} for tile,p,h in inp],'provenance':[ref(base),ref(corner)],'method':'Hard native pixel source selection, minimum-error path restricted to new r08_c04 own-side 115 pixels; adjacent accepted cores fixed. Synchronize neighbour halo only.','eastPathWithinOwn115':ep.tolist(),'southPathWithinOwn115':spth.tolist(),'sourceIds':ref(nid),'script':ref(Path(__file__)),'seamHelper':ref(hp),'noResize':True,'noFeather':True,'noDrawing':True,'tiles':[],'qa':[]}
for tile,ar in [('r08_c04',target),('r08_c05',e),('r09_c04',s)]:
 trace['tiles'].append({'tile':tile,'context':png(tile+'-context-native',ar),'candidate':png(tile+'-candidate-4096',ar[115:4211,115:4211]),'coreChanged':tile=='r08_c04'})
tc=target[115:4211,115:4211];ec=e[115:4211,115:4211];sc=s[115:4211,115:4211];sec=se[115:4211,115:4211]
for side,neighbor in [('east',ec),('south',sc)]:
 for i,start in enumerate([0,800,1600,2400,3196],1):
  crop=np.concatenate([tc[start:start+900,-345:],neighbor[start:start+900,:345]],axis=1) if side=='east' else np.concatenate([tc[-345:,start:start+900],neighbor[:345,start:start+900]],axis=0)
  trace['qa'].append(dict(png(side+'-part'+str(i)+'-100pct',crop),side=side,part=i,nativePixelsResampled=False))
cornercrop=np.concatenate([np.concatenate([tc[-500:,-500:],ec[-500:,:500]],axis=1),np.concatenate([sc[:500,-500:],sec[:500,:500]],axis=1)],axis=0)
trace['qa'].append(dict(png('four-corner-100pct',cornercrop),side='four_corner',nativePixelsResampled=False))
trace['validation']={'adjacentCoresUnchanged':True,'east230HaloExact':True,'south230HaloExact':True,'existingC05Horizontal230OverlapUnchanged':True,'existingR09Vertical230OverlapUnchanged':True,'allTargetPixelsMatchRecordedNativeSource':True,'allSavedPixelsVerified':True,'onlyNewTileCandidateChanged':True}
p=q/(pre+'-trace.json');assert not p.exists();p.write_text(json.dumps(trace,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'trace':ref(p),'tiles':trace['tiles'],'qaCount':len(trace['qa'])}))

