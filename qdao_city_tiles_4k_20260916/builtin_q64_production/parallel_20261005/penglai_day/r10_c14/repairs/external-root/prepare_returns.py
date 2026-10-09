from pathlib import Path
from PIL import Image
import numpy as np,sys
R=Path(__file__).resolve().parent;B=R.parents[2];sys.path.insert(0,str(B));import production as p
def a(f):return np.asarray(Image.open(f).convert('RGB'))
D=R/'joint-v1';spec=p.read(R/'evidence/inputs.json')
north=a(spec['north']['file']).copy();west=a(spec['west']['file']).copy();south=a(spec['withCorner']['file']).copy()
n=a(D/'north-joint.png');w=a(D/'west-joint.png')
nm=np.asarray(Image.open(D/'north-mask.png'))>0;wm=np.asarray(Image.open(D/'west-mask.png'))>0
north[3469:]=np.where(nm[:627,:,None],n[:627],north[3469:])
west[:,3469:]=np.where(wm[:,:627,None],w[:,:627],west[:,3469:])
south[:627]=np.where(nm[627:,:,None],n[627:],south[:627])
south[:,:627]=np.where(wm[:,627:,None],w[:,627:],south[:,:627])
for name,value in [('north',north),('west',west),('south',south)]:
    f=D/f'{name}-stage.png';Image.fromarray(value).save(f)
    p.derived(f,[spec['north']['file'],spec['west']['file'],spec['withCorner']['file'],D/'north-joint.png',D/'west-joint.png'],{'method':'exact native shared-edge masks into three staged tiles','formalAccepted':False})
# More context past previous strip return, every output native1254.
north_context=np.concatenate([north[3469:],south[:1800]],axis=0)
west_context=np.concatenate([west[:,3469:],south[:,:1800]],axis=1)
targets=[
('n-return1',north_context,(490,300,1744,1554),'Repair only the disconnected two pale-stone beveled grooves around x600..800, y350..750. Their cut-off left stubs must flow into the corresponding diagonal grooves on the right with smooth rounded continuous slab corners. Preserve all other grooves and stone counts, no floating stub.'),
('n-return2',north_context,(1580,430,2834,1684),'Repair the disconnected pale-stone groove around x570,y490 just behind the golden mooring ring. Its cut-off diagonal left part must flow naturally into the slab boundary at the right and below. Also smoothly continue the nearby bottom slab highlights through their tiny stepped returns. Preserve the complete ring and exact object layout.'),
('n-return3',north_context,(2420,250,3674,1504),'Repair tiny contour steps around x630,y460 on the left corner of the wooden box and the stone balustrade cap immediately under it. Preserve the original straight beveled edge direction, rounded corner and object count. Repair only short discontinuities, no geometry redesign.'),
('w-return1',west_context,(0,480,1254,1734),'Repair the tiny step in the ivory paving bevel just above the tabletop near x370,y680. Preserve continuous original diagonal highlight and joint; all objects and proportions unchanged.'),
('w-return2',west_context,(0,2720,1254,3974),'Repair the small stepped return in the narrow vertical stone joint just above the left wooden post near x370,y570. The groove must enter behind the post with continuous thickness and color, no horizontal cutoff. Smooth tiny timber highlight breaks across the middle. Preserve the large continuous masonry slab, do not add a new vertical mortar line in its center.')
]
records=[]
for name,canvas,box,detail in targets:
    x0,y0,x1,y1=box;f=R/'references'/f'{name}-input.png';Image.fromarray(canvas[y0:y1,x0:x1]).save(f);assert Image.open(f).size==(1254,1254)
    p.derived(f,[D/'north-stage.png',D/'west-stage.png',D/'south-stage.png'],{'method':'native crop from combined stage','axis':'north'if name[0]=='n'else'west','boxLTRB':box,'resampling':False})
    prompt='Use case: precise-object-edit. Image1 is the exact native1254 edit target. '+detail+' Match bright clean rounded full Taoist Q handpainted game map texture and material, image2 is approved PRIMARY style only, no UI. Keep canvas, camera, light and scale fixed. Preserve outermost150px and all unmentioned details. Do not blur or create doubled outlines. No text, labels, watermark, new objects or UI. Same1254 square.'
    call={'prompt':prompt,'referenced_image_paths':[f.as_posix(),'D:/work/image/designs/gameplay-ui/04-guild.png'],'transparent_background':False}
    (R/'prompts'/f'{name}.prompt.txt').write_text(prompt,encoding='utf8');p.write(R/'prompts'/f'{name}.call.json',call)
    records.append({'name':name,'axis':'north'if name[0]=='n'else'west','boxLTRB':box,'file':str(f),'sha256':p.sha(f)})
p.write(R/'evidence/returns-inputs.json',records);print('5 native return inputs')

