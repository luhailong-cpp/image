from workflow import ROOT,read,write,sha,patch,now
from PIL import Image
from pathlib import Path
import sys
pid,v,kind,note=sys.argv[1:5];names=sys.argv[5:]
assert pid[:7] in ['r13_c13','r14_c13','r13_c14','r12_c14']
box=patch(pid)['nativeGlobalBox'];base=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(base).convert('RGB');parts=[]
for name in names:
 np=ROOT/'native'/name;rec=read(Path(str(np)+'.generation.json'));nb=rec['coordinate']['nativeGlobalBox']
 cb=[nb[0]+115,nb[1]+115,nb[0]+1139,nb[1]+1139]
 inter=[max(box[0],cb[0]),max(box[1],cb[1]),min(box[2],cb[2]),min(box[3],cb[3])]
 assert inter[2]>inter[0] and inter[3]>inter[1]
 crop=[inter[0]-nb[0],inter[1]-nb[1],inter[2]-nb[0],inter[3]-nb[1]];dest=[inter[0]-box[0],inter[1]-box[1]]
 assert inter[2]<=box[0]+115 or inter[0]>=box[0]+1139 or inter[3]<=box[1]+115 or inter[1]>=box[1]+1139
 im.paste(Image.open(np).convert('RGB').crop(crop),tuple(dest));parts.append({'file':str(np),'sha256':sha(np),'sourceCrop':crop,'destination':dest,'globalIntersection':inter,'onlySelectedCore':True})
g=ROOT/'guides'/f'{pid}.core-context-{v}.png';assert not g.exists();im.save(g)
write(Path(str(g)+'.generation.json'),{'file':str(g),'sha256':sha(g),'atUtc':now(),'operation':'Unscaled selected-neighbor-core edges pasted only in target outer halo; no unselected neighbor halo used','layoutBase':str(base),'layoutSha256':sha(base),'placements':parts,'usableAsFinalArt':False})
common='Edit ONLY image 1 in its exact crop and scale. Output one opaque 1254 x 1254 square. This is a magnified small patch of a polished hand-painted Daoist Q game map. The sharp 115-pixel-wide outer edge strips are real adjoining map pixels, preserve their locations and extend their exact contours into the whole interior. The blurry center is a layout guide only: fully redraw it at native sharp detail while preserving its exact object geometry. Remove every guide boundary, do not retain rectangular color divisions or straight strip edges. '
if kind=='water':
 prompt=common+'Entire image is turquoise sea water: create connected sharp natural water caustics matching the scale, color and brightness of the real edge strips. No land, boat, architecture, plants, people, symbols or miniature scene. No letters, frame, diagram, watermark. '+note;refs=[{'file':str(g),'sha256':sha(g),'role':'only target and composition authority'}]
else:
 prompt=common+note+' Use the other references solely for material and painting style, never their composition. No additional boat, land, buildings, miniature scene, people, letters, diagram, frame or watermark. Preserve clear daylight, rounded polished warm wood and clean cyan sea. Continue every real edge smoothly across the image.';refs=[{'file':str(g),'sha256':sha(g),'role':'only target and composition authority'}]+read(ROOT/'references.json')
pp=ROOT/'prompts'/f'{pid}_{v}.core.prompt.txt';assert not pp.exists();pp.write_text(prompt,encoding='utf-8')
args={'prompt':prompt,'referenced_image_paths':[r['file'] for r in refs],'transparent_background':False}
write(ROOT/'prompts'/f'{pid}_{v}.core.args.json',args);write(ROOT/'prompts'/f'{pid}_{v}.core.request.json',{'args':args,'references':refs,'promptPath':str(pp),'actualModel':None,'actualQuality':None});print(g)

