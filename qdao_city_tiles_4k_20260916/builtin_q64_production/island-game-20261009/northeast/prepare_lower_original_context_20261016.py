from native_work import *
src=Path(current_references()[0]['file']); out=ZONE/'guides/r03c09-lower-original-nearest-context-20261016.png';assert not out.exists()
im=Image.open(src);im.crop((705,232,772,286)).resize((670,540),Image.Resampling.NEAREST).save(out)
write(out.with_suffix('.png.derivation.json'),{'source':str(src),'sha256':sha(src),'crop':[705,232,772,286],'displayResize':[670,540],'role':'layout-only original context; NOT generated or final native art','finalArt':False})
print(str(out))

