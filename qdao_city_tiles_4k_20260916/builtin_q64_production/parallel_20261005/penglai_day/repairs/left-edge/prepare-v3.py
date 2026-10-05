from repair import *
from PIL import ImageDraw
base=Image.open(R/'target-native.png').convert('RGB')
previous=Image.open(R/'repair-v2.png').convert('RGB')
base.paste(previous.crop((627,0,830,1254)),(627,0))
base.save(R/'target-v3-context.png')
derived(R/'target-v3-context.png',[R/'target-native.png',R/'repair-v2.png'],{'method':'exact native composite including reference-only halo','replacementRectLTRB':[627,0,830,1254]})
masked=base.copy()
ImageDraw.Draw(masked).rectangle((627,0,829,1253),fill=(255,0,255))
masked.save(R/'target-v3-gap.png')
derived(R/'target-v3-gap.png',[R/'target-v3-context.png'],{'method':'mark native repair area with explicit magenta inpainting gap','gapRectLTRB':[627,0,830,1254],'resampling':None,'notProductionArt':True})
