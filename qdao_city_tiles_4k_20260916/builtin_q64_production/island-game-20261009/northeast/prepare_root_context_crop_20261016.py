from native_work import *
ref=Path(current_references()[0]['file']);src=Image.open(ref)
p=ZONE/'guides/r03c09-context-layout-only-20261016.png'
if not p.exists():
 src.crop((690,160,805,280)).resize((575,600),Image.Resampling.NEAREST).save(p)
 write(p.with_suffix('.png.derivation.json'),{'source':str(ref),'sha256':sha(ref),'crop':[690,160,805,280],'resize':[575,600],'purpose':'enlarged original layout inspection only, not native artwork','finalArt':False})
print(str(p))

