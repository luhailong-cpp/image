import json,hashlib
from pathlib import Path
from PIL import Image
z=Path(__file__).resolve().parent.parent
p='r03_c14_p42'; v='v2'
base=z/'native'/f'{p}-v1.png'; layout=z/'guides'/f'{p}.native-edge-layout.png'
im=Image.open(base).convert('RGB'); guide=Image.open(layout).convert('RGB')
im.paste(guide.crop((0,0,900,250)),(0,0))
gp=z/'guides'/f'{p}-{v}.top-layout-repair.png'; assert not gp.exists(); im.save(gp)
def ref(f,role): return {'path':str(f).replace('\\','/'),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'role':role}
plan=json.loads((z/'records'/f'{p}.plan.json').read_text(encoding='utf-8-sig'))
plan['references']=plan['references'][:3]+[ref(gp,'edit target with original top 250 layout region restored for guidance only')]
plan['repairOf']=ref(base,'candidate with incorrect small repeated posts')
plan['coordinateSplitSha256']=hashlib.sha256(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json').read_bytes()).hexdigest()
for dest,data in [(z/'records'/f'{p}-{v}.plan.json',plan),(Path(str(gp)+'.derived.json'),{'purpose':'guidance only, never final pixels','operation':'integer crop original layout [0,0,900,250] pasted on native candidate; no drawing or final edits','sources':[ref(base,'candidate'),ref(layout,'layout guidance')]})]:
 assert not dest.exists(); dest.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')

