from pathlib import Path
from PIL import Image
import json,hashlib,shutil
root=Path(__file__).resolve().parent;folder=root/'source';target=folder/'walk-N.png';original=folder/'walk-N-original.png'
if not original.exists():shutil.copy2(target,original)
base=Image.open(original).convert('RGB');w=base.width//2;h=base.height//4;assert w==h
out=base.copy();records=[]
for phase in [2,3,4]:
 p=folder/f'fix-phase{phase:02d}-N.png';im=Image.open(p).convert('RGB');assert im.width==im.height;scale=w/im.width;j=phase-1;out.paste(im.resize((w,h),Image.Resampling.LANCZOS),(j%2*w,j//2*h));records.append({'phase':phase,'source_path':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_native_size':list(im.size),'source_crop':[0,0,im.width,im.height],'uniform_raw_cell_scale':scale,'paste_xy':[j%2*w,j//2*h]})
out.save(target)
meta={'operation':'Replace only three rejected NORTH gait cells with separately ImageGen-authored poses; isotropic cell resolution normalization only','output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'output_size':list(out.size),'grid':[2,4],'original_source':str(original),'original_sha256':hashlib.sha256(original.read_bytes()).hexdigest(),'corrections':records,'script_drawn_art':False,'mirrored':False,'copied_or_interpolated_gait':False,'per_frame_body_fit':False}
target.with_suffix('.assembly.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print('N phases02/03/04 replaced with opposite support leg.')

