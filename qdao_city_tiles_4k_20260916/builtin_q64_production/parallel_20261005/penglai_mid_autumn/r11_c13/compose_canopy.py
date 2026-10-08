from prepare_structure import *
from PIL import ImageDraw,ImageFilter
base=R/'structure-north-healed.png';ai=R/'canopy-focused-generated.png'
focus=read(str(ai)+'.generation.json')['planningFrameGlobalXYWH'];k=1254/focus[2]
extent=[(FRAME[0]-focus[0])*k,(FRAME[1]-focus[1])*k,(FRAME[0]+S-focus[0])*k,(FRAME[1]+S-focus[1])*k]
layer=Image.open(ai).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,extent,Image.Resampling.BICUBIC)
mask=Image.new('L',(1254,1254),0);d=ImageDraw.Draw(mask)
# Select only already AI-painted canopy/nearby frame. No code draws or warps scene geometry.
d.rectangle([56,83,700,290],fill=255);mask=mask.filter(ImageFilter.GaussianBlur(5));mask.paste(0,(0,320,1254,1254));mask.paste(0,(735,0,1254,1254))
mp=R/'canopy-planning-selection-mask.png';image_save(mask,mp,[ai],dict(kind='selection mask only for AI-painted focused planning pixels',globalFrameXYWH=FRAME,maskRectangleLTRB=[56,83,700,290],gaussianRadius=5,hardBottomExclusive=320,hardRightExclusive=735,codeDrawnSceneGeometry=False))
out=R/'structure-canopy-corrected.png';im=Image.composite(layer,Image.open(base).convert('RGB'),mask)
image_save(im,out,[base,ai,mp],dict(kind='select locally AI-painted continuous canopy at exact global coordinates',globalFrameXYWH=FRAME,focusedGlobalFrameXYWH=focus,aiSourceExtentForFullOutput=extent,resampling='BICUBIC planning reduction only',mask=ref(mp),geometryWarp=False,codeDrawnSceneGeometry=False,productionPixels=False))
assert ImageChops.difference(im.crop((0,320,1254,1254)),Image.open(base).crop((0,320,1254,1254))).getbbox() is None
print(out)
