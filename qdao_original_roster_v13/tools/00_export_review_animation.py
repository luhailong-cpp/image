from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
root=Path(r'E:\work\image\qdao_original_roster_v13')
dest=root/'review/00_reference_topright_boy'
shots=dest/'browser-final-candidate'
for name in ['S-09-enlarged','mobile-390']:
 im=Image.open(shots/(name+'.png')).convert('RGB'); im.thumbnail((1100,1100));im.save(shots/(name+'-review.jpg'),quality=88)
ds=['N','NE','E','SE','S','SW','W','NW'];frames=[]
for i in range(1,17):
 sheet=Image.new('RGB',(1024,576),(38,44,45));draw=ImageDraw.Draw(sheet)
 for k,d in enumerate(ds):
  x=(k%4)*256;y=(k//4)*288
  im=Image.open(root/f'candidate/00_reference_topright_boy/walk/{d}/{i:02d}.png').convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
  sheet.paste(im,(x,y),im);draw.text((x+8,y+264),f'{d} / {i:02d}',fill='white')
 frames.append(sheet)
palette=Image.new('RGB',(1024,576*4))
for k in range(4):palette.paste(frames[k*4],(0,k*576))
pal=palette.quantize(colors=256)
q=[f.quantize(palette=pal,dither=Image.Dither.FLOYDSTEINBERG) for f in frames]
for dur,label in [(30,'normal'),(60,'half-speed')]:
 q[0].save(dest/f'all-eight-directions-{label}.gif',save_all=True,append_images=q[1:],duration=dur,loop=0,optimize=False,disposal=2)
manifest=root/'candidate/00_reference_topright_boy/manifest.json'
(dest/'animated-review-provenance.json').write_text(json.dumps({'purpose':'review-only display exports, never used as animation source','input_manifest_sha256':hashlib.sha256(manifest.read_bytes()).hexdigest(),'directions':ds,'operation':'actual final transparent frames uniformly downsampled512to256, composited labelled2x4grid; GIF256color shared palette','normal_frame_ms':30,'half_speed_frame_ms':60,'synthetic_poses':0},indent=2),encoding='utf-8')
print(dest)
