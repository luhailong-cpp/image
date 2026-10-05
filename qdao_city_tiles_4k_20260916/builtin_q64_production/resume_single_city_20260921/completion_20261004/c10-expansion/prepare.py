from pathlib import Path
import hashlib,json,sys
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
S=R.parents[1]
ROOT=next(p for p in R.parents if (p/'config/image-generation.json').is_file())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
state=R/'state';state.mkdir(exist_ok=True)
if not (state/'canvas.png').exists():
 im=Image.new('RGBA',(4326,4326),(0,0,0,0))
 lower=S/'completion_20261004/c10-seed/joined-v1/r09_c10.png'
 fragment=S/'completion_20261004/c10-seed/joined-v1/r08_c10-native-fragment-1254x627.png'
 left=S/'completion_20261004/c09/tone-candidate-v1/r08_c09.png'
 assert sha(lower)=='82a70d8fa3063a1be15cc87b98c16490ca550b48234bbd524f72efcd8927ba0f'
 im.paste(Image.open(lower).convert('RGBA').crop((0,0,4096,115)),(115,4211))
 im.paste(Image.open(fragment).convert('RGBA'),(1024,3584))
 im.paste(Image.open(left).convert('RGBA').crop((3981,0,4096,4096)),(0,115))
 im.save(state/'canvas.png')
 (state/'provenance.json').write_text(json.dumps({'globalCanvasLTRB':[36749,28557,41075,32883],'inputs':[info(lower),info(fragment),info(left)],'operations':[]},indent=2),encoding='utf-8')
r,c=int(sys.argv[1]),int(sys.argv[2]);shift=int(sys.argv[3]) if len(sys.argv)>3 else 0;name=f'r{r:02}_c{c:02}'+('_seed' if shift else '')
O=R/name;O.mkdir(exist_ok=False)
x,y=(c-1)*1024,(r-1)*1024+shift
if shift and Image.open(state/'canvas.png').height<4838:
 old=Image.open(state/'canvas.png').convert('RGBA');larger=Image.new('RGBA',(4326,4838),(0,0,0,0));larger.paste(old,(0,0))
 lower=S/'completion_20261004/c10-seed/joined-v1/r09_c10.png'
 larger.paste(Image.open(lower).convert('RGBA').crop((0,115,4096,627)),(115,4326))
 larger.save(state/'canvas.png')
 pr=json.loads((state/'provenance.json').read_text());pr['globalCanvasLTRB']=[36749,28557,41075,33395];pr['lower627ContextSource']=info(lower)
 (state/'provenance.json').write_text(json.dumps(pr,indent=2),encoding='utf-8')
im=Image.open(state/'canvas.png').convert('RGBA').crop((x,y,x+1254,y+1254))
im.save(O/'context.png')
master=ROOT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
box=[36749+x,28557+y,36749+x+1254,28557+y+1254]
Image.open(master).convert('RGB').resize((1254,1254),Image.Resampling.BICUBIC,box=tuple(v*3/32 for v in box)).save(O/'layout-reference-only.png')
a=np.array(im)[:,:,3]
assert np.any(a==0) and np.any(a==255)
prompt='''Outpaint the FIRST image into its transparent missing region. Return one complete opaque 1254 by 1254 pixel scene crop, same framing. Its visible opaque regions are actual native finished artwork: preserve those shapes, exact object positions, material, lighting, bevel thickness and camera scale. Smoothly continue every clipped border, stone slab and carving across the transparency boundary. The second image is ONLY the canonical broad layout reference at exactly the same world coordinates. Use it to position the missing landscape, while the FIRST image supplies authoritative detailed boundaries and exact native scale. Never paste, enlarge or trace blurry pixels from the second reference. Produce newly rendered crisp details for the missing region. Transparency edges and image crop edges are not objects and MUST NOT become straight artificial paving joints. No separate inset panel or rectangular colour band at an old missing-region boundary. Bright clean round plump Q-style Daoist fantasy map ground, soft sculpted smooth warm ivory and gold stone, neutral slate, restrained gentle handpainted shading, no granular grunge. Third reference supplies user-approved rendering STYLE ONLY, do not import its UI, objects, text, layout or characters. Preserve the established scene composition; no extra flower ornament, no invented buildings, foliage, people, symbols, cracks or dirt. Preserve the opaque original region as closely as possible. No text, frame, watermark, blur, black region, or transparency in the output.'''
refs=[str(O/'context.png'),str(O/'layout-reference-only.png'),str(ROOT/'designs/gameplay-ui/04-guild.png')]
prompt+=' Important: use smooth clean stone, with only very subdued low-contrast cloudy shading. Do not add bold marble veins, large mottled polygons or crack-like grain. Native known regions govern all contour endpoints: do not move them to match the blurred layout reference.'
payload={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}
(O/'prompt.txt').write_text(prompt,encoding='utf-8')
(O/'request.json').write_text(json.dumps({'patch':name,'globalCropLTRB':box,'canvasCropLTRB':[x,y,x+1254,y+1254],'nativeContextPixels':int((a==255).sum()),'missingPixels':int((a==0).sum()),'payload':payload},indent=2),encoding='utf-8')
(O/'preparation.json').write_text(json.dumps({'references':[info(p) for p in refs],'master':info(master),'stateBefore':info(state/'canvas.png'),'sourceNativeUpscaled':False,'layoutReferencePixelsMayEnterOutput':False,'stateProvenance':json.loads((state/'provenance.json').read_text())},indent=2),encoding='utf-8')
(R/'config.snapshot.json').write_text((ROOT/'config/image-generation.json').read_text(),encoding='utf-8')
print(json.dumps({'patch':str(O),'known':int((a==255).sum()),'missing':int((a==0).sum()),'box':box}))
