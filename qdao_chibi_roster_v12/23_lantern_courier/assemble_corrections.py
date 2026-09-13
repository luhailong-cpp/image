"""Insert independently authored correction cells without changing approved poses."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
root=Path(__file__).resolve().parent
source=root/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
fixes=json.loads((root/'corrections.json').read_text(encoding='utf-8-sig'))
for direction,changes in fixes.items():
    target=source/f'walk-{direction}.png'; original=source/f'walk-{direction}-original.png'
    if not original.exists():shutil.copy2(target,original)
    base=Image.open(original).convert('RGB'); cols,rows=(2,4) if direction in ['N','S'] else (4,2)
    cw,ch=base.width//cols,base.height//rows;out=base.copy(); records=[]
    for phase,fix in changes.items():
        p=source/fix['file'];im=Image.open(p).convert('RGB');box=[0,0,im.width,im.height]
        if 'cell' in fix:
            fc,fr=fix['grid'];w,h=im.width//fc,im.height//fr;i=fix['cell'];box=[i%fc*w,i//fc*h,(i%fc+1)*w,(i//fc+1)*h]
        crop=im.crop(box); scale=min(cw/crop.width,ch/crop.height);size=(round(crop.width*scale),round(crop.height*scale));crop=crop.resize(size,Image.Resampling.LANCZOS)
        j=int(phase)-1;x=j%cols*cw+(cw-size[0])//2;y=j//cols*ch+(ch-size[1])//2
        out.paste((255,0,255),(j%cols*cw,j//cols*ch,(j%cols+1)*cw,(j//cols+1)*ch));out.paste(crop,(x,y))
        records.append({'phase':int(phase),'source_path':str(p),'source_sha256':sha(p),'source_native_size':list(im.size),'source_crop':box,'uniform_raw_cell_scale':scale,'paste_xy':[x,y]})
    temp=target.with_name(target.stem+'-assembly-temp.png')
    out.save(temp)
    temp.replace(target)
    target.with_suffix('.assembly.json').write_text(json.dumps({'operation':'Replace rejected cells with separately ImageGen-authored corrections; isotropic raw-cell resolution normalization only','output_sha256':sha(target),'output_size':list(out.size),'grid':[cols,rows],'original_source':str(original),'original_sha256':sha(original),'corrections':records,'script_drawn_art':False,'mirrored':False,'copied_or_interpolated_gait':False,'per_frame_body_fit':False},indent=2),encoding='utf-8')
    print(direction,'corrections assembled',flush=True)

