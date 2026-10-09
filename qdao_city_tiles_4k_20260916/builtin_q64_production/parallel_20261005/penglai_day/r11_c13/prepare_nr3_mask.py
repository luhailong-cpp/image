import helper as h
from PIL import Image,ImageDraw
R=h.ROOT;p=h.p;src=R/'repairs/north/joint-v2/qa/nr3-composite.png';im=Image.open(src).convert('RGB');d=ImageDraw.Draw(im)
boxes=[[354,613,1254,643],[124,225,153,270],[179,1105,217,1150]]
for box in boxes:d.rectangle((box[0],box[1],box[2]-1,box[3]-1),fill=(255,0,255))
f=R/'references/nr3-mask-input.png';im.save(f);p.derived(f,[src],{'method':'magenta defect-area inpainting guide only','boxesLTRB':boxes})
prompt='Use case: strict inpainting. Image1 is the exact target with THREE MAGENTA HOLES marking artificial join defects. Fill only these magenta pixels and immediately adjacent transition pixels. The long thin horizontal hole across y613..643 must contain seamless turquoise water, unchanged white foam endpoints, and gray quay stone at its left tip. Do NOT leave any horizontal boundary, seam, color stripe or magenta. Reconstruct natural diagonal water brushstrokes connecting above and below. The tiny upper-left hole repairs the straight gray wall vertical groove without a side step. The tiny bottom-left hole repairs the smooth straight diagonal cream quay rim without a step. Preserve every other pixel, objects and composition. Image2 PRIMARY approved Taoist Q style only. Same1254x1254 image. No new objects, text or added foam.'
h.savecall('nr3-mask',{'prompt':prompt,'referenced_image_paths':[f.as_posix(),h.STYLE],'transparent_background':False})
print('prepared')
