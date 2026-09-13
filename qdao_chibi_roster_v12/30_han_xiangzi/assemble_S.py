from pathlib import Path
from PIL import Image
import hashlib,json
r=Path(__file__).resolve().parent
main=r/'source/walk-S-attempt02.png'
pose=r/'source/walk-S-pose05.png'
a=Image.open(main).convert('RGB'); b=Image.open(pose).convert('RGB'); c=a.width//4
out=Image.new('RGB',(c*4,c*2),(255,0,255));records=[]
for i in range(8):
    source=pose if i==4 else main
    box=(0,0,b.width,b.height) if i==4 else (i%4*c,i//4*c,i%4*c+c,i//4*c+c)
    crop=(b if i==4 else a).crop(box)
    cell=crop.resize((c,c),Image.Resampling.LANCZOS)
    out.paste(cell,(i%4*c,i//4*c))
    records.append({'frame':i+1,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_box':box,'isotropic_raw_cell_scale':c/crop.width})
dest=r/'source/walk-S.png';out.save(dest)
dest.with_suffix('.assembly.json').write_text(json.dumps({'version':12,'operation':'Crop seven authored source cells; replace missing opposite contact with separately authored single pose; isotropic raw-cell resolution normalization only','output_path':str(dest),'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'output_grid':[4,2],'sources':records,'new_poses_generated_by_script':False,'mirror_or_interpolation':False},ensure_ascii=False,indent=2),encoding='utf-8')
print(dest)
