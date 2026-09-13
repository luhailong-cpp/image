from PIL import Image
from pathlib import Path
import hashlib,json
root=Path(r'E:\work\image\qdao_chibi_roster_v12\24_lu_dongbin')
p=root/'source/walk-E-vertical.png'
raw=Image.open(p).convert('RGBA');cw,ch=raw.width//2,raw.height//4
out=Image.new('RGBA',(cw*2,ch*4),(255,0,255,255))
order=[0,1,2,7,4,5,6,3];cells=[]
for i,j in enumerate(order):
    src=p;im=raw;box=(j%2*cw,j//2*ch,(j%2+1)*cw,(j//2+1)*ch)
    if i==5:
        src=root/'source/E06-arm-fixed.png';im=Image.open(src).convert('RGBA');box=(0,0,im.width,im.height)
    crop=im.crop(box);sz=crop.size
    crop=crop.resize((cw,ch),Image.Resampling.LANCZOS)
    out.paste(crop,(i%2*cw,i//2*ch))
    cells.append({'output_frame':i+1,'source_path':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_native_size':list(im.size),'source_box':list(box),'uniform_raw_cell_scale':cw/sz[0],'output_cell_size':[cw,ch]})
target=root/'source/walk-E-final.png';out.save(target)
meta={'version':12,'operation':'authored cell extraction, real phase ordering, one authored arm correction; isotropic whole raw-cell resize only','output_path':str(target),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'output_grid':[2,4],'output_size':list(out.size),'cells':cells,'new_poses_generated_by_script':False,'mirror_or_interpolation':False}
target.with_suffix('.assembly.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
print(target)
