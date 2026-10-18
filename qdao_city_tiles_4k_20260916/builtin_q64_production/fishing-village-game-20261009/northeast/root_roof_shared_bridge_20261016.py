from PIL import Image
from pathlib import Path
import json
import root_north_20261012 as n
b=n.b;Z=n.Z;p='r04_c12_roof-right-bridge01';v='v1'
left=Z/'native/r04_c12_p43-v5.png';right=Z/'native/r04_c12_p44-v1.png'
a=Image.new('RGB',(1254,1254));a.paste(Image.open(left).convert('RGB').crop((512,0,1139,1254)),(0,0));a.paste(Image.open(right).convert('RGB').crop((115,0,742,1254)),(627,0))
gp=Z/'guides'/f'{p}-{v}.native-target.png';assert not gp.exists();a.save(gp)
src=[dict(b.ref(left,'native left roof'),cropBox=[512,0,1139,1254],pasteAt=[0,0]),dict(b.ref(right,'native right roof'),cropBox=[115,0,742,1254],pasteAt=[627,0])]
co={'id':p,'coreGlobalBox':[47616,15360,48640,16384],'nativeGlobalBox':[47501,15245,48755,16499],'expectedSize':[1254,1254],'nativeCoreBox':[115,115,1139,1139]}
n.atomic(str(gp)+'.derived.json',{'purpose':'AI edit guide only, never final pixels','operation':'integer native crop and opaque paste, seam at x627','sources':src,'coordinates':co,'finalArt':False})
refs=[b.ref(b.C['layoutReference'],'layout only'),b.ref(b.C['detailStyleReference'],'materials only'),b.ref(b.C['primaryStyleReference'],'Q Daoist style only'),b.ref(gp,'exact shared seam edit target')]
pp=Z/'records'/f'{p}-{v}.plan.json';assert not pp.exists();n.atomic(pp,{'patchId':p,'coordinates':co,'references':refs,'nativeEdgeSources':[],'expectedNativeSize':[1254,1254],'createdAtUtc':b.now(),'route':'builtin','tool':'image_gen.imagegen','actualModel':None,'actualQuality':None,'repairMethod':'new seam centered native reconstruction','plannedContributionBox':[377,270,877,1100],'preserveBorders':'left/right377; top270 and bottom154 fixed; exact final core edge anchors retained'})
print(str(gp))

