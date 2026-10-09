from pathlib import Path
from PIL import Image
import numpy as np,sys
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
D=R/'joint-v4'
west=Image.open(D/'r10_c13-candidate.png').convert('RGB');east=Image.open(D/'r10_c14-candidate.png').convert('RGB')
f=R/'references/w-wood-return-input.png';im=Image.new('RGB',(1254,1254));im.paste(west.crop((3072,1470,4096,2724)),(0,0));im.paste(east.crop((0,1470,230,2724)),(1024,0));im.save(f)
p.derived(f,[D/'r10_c13-candidate.png',D/'r10_c14-candidate.png'],{'method':'native full-context crop across remaining horizontal color-step in table wood','globalTileRelativeRectXYWH':[3072,1470,1254,1254],'resampling':False})
prompt='Use case: precise-object-edit. Image1 is exact native1254 context of a wooden table and stone balustrade. The lower wood wall near the center-left has an artificial straight horizontal rectangular color cutoff around y575. Remove ONLY this rectangular pigment band, restore continuous natural original vertical wood grain and warm sunlight through it. Preserve every exact original timber edge, panel count, corner, groove, stone cap contour, lighting and shadow. No redesigned objects, no new joints, no blur. Image2 is approved PRIMARY style only: bright clean full rounded Taoist Q handpainted game map, never UI. Preserve outermost150px and all unrelated pixels. Same1254 canvas. No text, watermark or border.'
(R/'prompts/w-wood-return.prompt.txt').write_text(prompt,encoding='utf8')
p.write(R/'prompts/w-wood-return.call.json',{'prompt':prompt,'referenced_image_paths':[f.as_posix(),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False})
print(str(f))

