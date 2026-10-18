from pathlib import Path
import json
from PIL import Image
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import r06_c14_extension as b
Z=Path(__file__).resolve().parent.parent
p='r03_c13_p44'
target=Z/'native'/f'{p}-v1.png'
a=Image.open(target).convert('RGB')
box=[740,190,1006,1024]
a.paste(a.crop(box).resize((360,834),Image.Resampling.BICUBIC),(740,190))
plan=json.loads((Z/'records'/f'{p}.plan.json').read_text())
for e in plan['nativeEdgeSources']:
 a.paste(Image.open(e['path']).convert('RGB').crop(e['cropBox']),e['pasteAt'][:2])
gp=Z/'guides'/f'{p}-v3.aligned-native-guide.png'
assert not gp.exists();a.save(gp)
def wr(f,d):
 assert not f.exists();f.write_text(json.dumps(d,indent=2)+'\n')
wr(Path(str(gp)+'.derived.json'),{'finalArt':False,'purpose':'nonfinal generation geometry guide only','source':b.ref(target,'native prior candidate'),'operation':'BICUBIC horizontal expansion of cropped foreground timber guide box; then original exact left/bottom native anchors opaque pasted. These guide pixels never used for final candidate.','sourceBox':box,'guideResizedPixels':[360,834],'guidePasteAt':[740,190],'nativeEdgeSources':plan['nativeEdgeSources']})
plan['createdAtUtc']=b.now();plan['references']=plan['references'][:3]+[b.ref(gp,'aligned native geometry repair guide only')];plan['repairTarget']=b.ref(target,'prior native candidate');plan['repairGuide']=b.ref(gp,'nonfinal aligned geometry guide');plan.update(b.config_evidence())
wr(Z/'records'/f'{p}-v3.plan.json',plan)
print(str(gp))

