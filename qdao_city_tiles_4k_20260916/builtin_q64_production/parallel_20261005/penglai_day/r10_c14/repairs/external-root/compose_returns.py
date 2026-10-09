from pathlib import Path
from PIL import Image
import sys,numpy as np
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
def a(f):return np.asarray(Image.open(f).convert('RGB'))
D=R/'joint-v2';D.mkdir(exist_ok=True)
rects={'n-return1':[(450,320,1100,820,32)],'n-return2':[(567,412,680,513,12),(840,735,988,858,16)],'n-return3':[(400,290,811,595,25)],'w-return1':[(295,617,442,734,14)],'w-return2':[(310,493,449,661,16)]}
records=[]
for item in p.read(R/'evidence/returns-inputs.json'):
    name=item['name'];original=a(item['file']);new=a(R/'native'/f'{name}.png')
    yy,xx=np.mgrid[:1254,:1254];mask=np.zeros((1254,1254),np.float32)
    for x0,y0,x1,y1,fade in rects[name]:
        alpha=np.clip(np.minimum(np.minimum(xx-x0,x1-1-xx),np.minimum(yy-y0,y1-1-yy))/fade,0,1);mask=np.maximum(mask,alpha)
    result=np.clip(np.rint(original*(1-mask[:,:,None])+new*mask[:,:,None]),0,255).astype(np.uint8)
    f=D/f'{name}-composite.png';Image.fromarray(result).save(f);np.savez_compressed(D/f'{name}-mask.npz',alpha=mask)
    p.derived(f,[item['file'],R/'native'/f'{name}.png'],{'method':'exact coordinates local bounded alpha ROI; no image resize, warp or blur','rectanglesLTRBWithFeather':rects[name],'mask':str(D/f'{name}-mask.npz'),'formalAccepted':False})
    records.append({**item,'composite':str(f),'sha256':p.sha(f),'alpha':str(D/f'{name}-mask.npz'),'bounds':rects[name]})
p.write(D/'return-composites.json',records)
# Native close inspection boards, not enlarged.
Image.open(D/'n-return2-composite.png').crop((780,680,1030,930)).save(D/'n2-cap-native.png')
Image.open(D/'n-return3-composite.png').crop((540,500,770,730)).save(D/'n3-cap-native.png')
for name,box in [('n-return3',(639,597,680,642)),('n-return2',(888,785,949,832))]:
    source=D/f'{name}-composite.png';im=Image.open(source).convert('RGB');im.paste((255,0,255),box)
    f=R/'references'/f'{name}-tiny-hole.png';im.save(f);p.derived(f,[source],{'method':'magenta missing-content marker over tiny existing highlight step','boxLTRB':box,'finalPixelUseForbidden':True})
    prompt='Use case: precise-object-edit. Image1 is native1254 target with a tiny magenta missing area. Fill ONLY the magenta region by continuing the existing pale stone bevel and its clean narrow highlight smoothly between the surrounding unchanged endpoints. Remove the tiny jagged splice notch; preserve exact slope, corner shape, bevel width, material, count and all other pixels. No new outlines or cracks, no extra glowing wedge. Image2 is the approved PRIMARY bright clean rounded full Taoist Q handpainted style reference only; no UI. Same canvas1254, exact geometry and light. No text, magenta, border or watermark.'
    call={'prompt':prompt,'referenced_image_paths':[f.as_posix(),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False}
    (R/'prompts'/f'{name}-tiny.prompt.txt').write_text(prompt,encoding='utf8');p.write(R/'prompts'/f'{name}-tiny.call.json',call)
print('Return composites and tiny-hole targets prepared')

