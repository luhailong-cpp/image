import json,hashlib
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent;p='r03_c14_p13';v='v3'
base=z/'native'/f'{p}-v1.png';im=Image.open(base).convert('RGB')
plan=json.loads((z/'records'/f'{p}.plan.json').read_text(encoding='utf-8-sig'))
def ref(f,role):return {'path':str(f).replace('\\','/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'role':role}
edges=[]
for name,side,box,at in [('r03_c14_p12-v1.png','left',[1024,0,1254,1254],[0,0]),('r03_c14_p14-v1.png','right',[0,0,230,1254],[1024,0]),('r03_c14_p23-v1.png','bottom',[0,0,1254,230],[0,1024])]:
 f=z/'native'/name;a=Image.open(f).convert('RGB');assert a.size==(1254,1254);im.paste(a.crop(box),tuple(at));edges.append(dict(ref(f,'exact_native_'+side+'_230px'),cropBox=box,pasteAt=at))
gp=z/'guides'/f'{p}-{v}.three-neighbor-foot-repair.png';assert not gp.exists();im.save(gp)
plan.update(version=v,nativeEdgeSources=edges,repairOf=ref(base,'earlier native candidate'),repairMethod='Three-neighbor constrained foot termination above fixed bottom water/deck',previousLocalRepairs=1,formalAccepted=False)
plan['references']=plan['references'][:3]+[ref(gp,'edit target with stable native neighbors restored')]
plan['coordinateSplitSha256']=hashlib.sha256(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json').read_bytes()).hexdigest()
for dest,data in [(z/'records'/f'{p}-{v}.plan.json',plan),(Path(str(gp)+'.derived.json'),{'purpose':'guidance only never final pixels','operation':'native1:1 edge crops over previous candidate; bottom owns lower corners','sources':[ref(base,'candidate')],'nativeEdgeSources':edges})]:
 assert not dest.exists();dest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

