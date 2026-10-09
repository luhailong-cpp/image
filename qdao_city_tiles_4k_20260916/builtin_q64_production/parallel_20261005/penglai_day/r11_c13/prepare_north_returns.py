import helper as h
from PIL import Image
R=h.ROOT;p=h.p;D=R/'repairs/north/joint-v1';src=D/'north-joint.png';im=Image.open(src).convert('RGB')
jobs=[('nr1',512,'At approximately x610,y650..1000 the diagonal white fabric stripe, light blue rounded rim and navy bottom silhouette have artificial 10-to-20-pixel stair-step notches across a vertical assembly join. Straighten those existing edges continuously to connect their exact endpoints on either side. Keep stripe width consistent and keep the same folds. Do not add a seam or stripe.'),('nr2',1800,'The straight dark right edge of the wooden upright at approximately x580,y1100 has a tiny rectangular notch introduced by the bottom repair boundary. Make this one edge straight and uninterrupted, with identical post width and its existing wood highlight; remove the notch only. Also preserve the gray stone vertical grooves and all crate contours exactly.'),('nr3',2842,'There is an artificial perfectly horizontal color band across the turquoise water near y627, from about x370 to1254. Make the water color and existing foam strokes continuous through this band. Preserve exact existing foam paths, mooring posts and wall silhouettes; add no new foam, patches, lines or objects.')]
record=[]
for n,x,detail in jobs:
    f=R/'references'/f'{n}-input.png';im.crop((x,0,x+1254,1254)).save(f);p.derived(f,[src],{'method':'exact native integer crop','boxLTRB':[x,0,x+1254,1254]})
    prompt='Use case: very local native image repair. Image1 is the exact1254-square target. Image2 is PRIMARY approved bright clean rounded Taoist Q painted style only. '+detail+' Change only the described defect and its immediate surroundings. Preserve all other pixels, viewpoint, colors, object counts and outer borders. Same1254x1254 crop, no text or UI.'
    h.savecall(n,{'prompt':prompt,'referenced_image_paths':[f.as_posix(),h.STYLE],'transparent_background':False});record.append({'name':n,'originXY':[x,0],'input':str(f)})
p.write(D/'return-plan.json',{'source':str(src),'sha256':p.sha(src),'jobs':record,'formalAccepted':False})
print('Prepared3 native return repairs')
