from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np

out=Path(__file__).parent
N=out.parent;T=N.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return {'file':str(p),'sha256':sha(p)}
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def load(v):
 assert sha(v['file'])==v['sha256'];return Image.open(v['file']).convert('RGBA')
localfile=N/'local-source-checkpoint.json'
local=read(localfile)
assert local['fragment']['sha256']=='977e91bd54d5552ed008dfaca4268bf7bf079ead2d3a2c2a9678f84df39aefe6'
(out/'local-checkpoint-frozen.json').write_bytes(localfile.read_bytes())
rootfile=T/'source-checkpoint.json';root=read(rootfile)
(out/'root-checkpoint-frozen.json').write_bytes(rootfile.read_bytes())
src={v['tile']:v for v in root['candidateSet']}
active=load(local['fragment']);south=load(src['r08_c10']);west=load(src['r08_c09'])
idx={'nativeScale':1,'localCheckpoint':ref(out/'local-checkpoint-frozen.json'),'rootCheckpoint':ref(out/'root-checkpoint-frozen.json'),'fragment':local['fragment'],'southBase':src['r08_c10'],'southwestBase':src['r08_c09'],'returnApplications':[],'crops':[]}
for c in (4,3,2,1):
 mp=N/f'r04_c{c:02d}-v1/final-v1/manifest.json';m=read(mp)
 for p in m['patches']:
  if p['destinationTile'] not in ('r08_c10','r08_c09'):continue
  dest=south if p['destinationTile']=='r08_c10' else west
  box=p['destinationTileLTRB'];prior=load(p['requiredPriorSource']);asset=load(p['asset'])
  assert dest.crop(box).tobytes()==prior.crop(box).tobytes(),(c,p['name'],'stale source ROI')
  assert asset.size==(box[2]-box[0],box[3]-box[1])
  dest.paste(asset,(box[0],box[1]))
  idx['returnApplications'].append({'manifest':ref(mp),'patch':p,'requiredPriorRoiExact':True})
def save(name,img,positions):
 p=out/(name+'.png');img.save(p)
 idx['crops'].append(dict(ref(p),size=list(img.size),sourcePositions=positions))
for row,y in enumerate((1933,2560),1):
 for col,x in enumerate((0,1280,2560),1):
  b=(x,y,x+1536,y+1536)
  save(f'coverage-{row}-{col}',active.crop(b),[{'tile':'r07_c10','tileLocalLTRB':b}])
for i,x in enumerate((0,938,1876,2816),1):
 img=Image.new('RGBA',(1280,768));img.paste(active.crop((x,3712,x+1280,4096)),(0,0));img.paste(south.crop((x,0,x+1280,384)),(0,384))
 save(f'south-seam-{i}',img,[{'tile':'r07_c10','tileLocalLTRB':(x,3712,x+1280,4096)},{'tile':'r08_c10-derived-with-four-returns','tileLocalLTRB':(x,0,x+1280,384)}])
corner=Image.new('RGBA',(512,768));corner.paste(active.crop((0,3712,256,4096)),(256,0));corner.paste(south.crop((0,0,256,384)),(256,384));corner.paste(west.crop((3840,0,4096,384)),(0,384))
jm=read(N/'r04_c01-v1/final-v1/manifest.json');joined=load(jm['joined']);corner.paste(joined.crop((0,755,115,1139)),(141,0))
save('southwest-available-corner',corner,[{'tile':'r07_c10','tileLocalLTRB':(0,3712,256,4096)},{'tile':'r07_c09-unpublished-halo','source':jm['joined'],'cropLTRB':(0,755,115,1139)},{'tile':'r08_c09-derived-return','tileLocalLTRB':(3840,0,4096,384)},{'tile':'r08_c10-derived-returns','tileLocalLTRB':(0,0,256,384)}])
idx['coverage']={'requiredTileLocalLTRB':[0,1933,4096,4096],'coveredPixels':int((np.asarray(active)[1933:,:,3]==255).sum()),'allRequiredPixelsOpaque':bool(np.all(np.asarray(active)[1933:,:,3]==255)),'fullAreaCoveredBySixOverlappingNative1536Crops':True}
idx['derivedSouthPixelSha256']=hashlib.sha256(south.tobytes()).hexdigest()
idx['derivedSouthwestPixelSha256']=hashlib.sha256(west.tobytes()).hexdigest()
(out/'crop-index.json').write_text(json.dumps(idx,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'coverage':idx['coverage'],'crops':len(idx['crops']),'returnApplications':len(idx['returnApplications'])}))
