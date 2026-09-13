"""Replace two whole independently generated neutral cells; never create poses procedurally."""
from pathlib import Path
from PIL import Image
import json,hashlib
root=Path(__file__).resolve().parent
basis=root/'source/idle-v2.png'
patch=root/'source/idle-EW-lotus-fixed.png'
original=Image.open(basis).convert('RGBA')
src=Image.open(patch).convert('RGBA')
cw,ch=original.width//4,original.height//2
sw,sh=src.width//2,src.height
out=original.crop((0,0,cw*4,ch*2))
records=[]
for index,destination in enumerate([2,6]):
    box=[index*sw,0,(index+1)*sw,sh]
    cell=src.crop(tuple(box))
    factor=min(cw/sw,ch/sh)
    nw,nh=round(sw*factor),round(sh*factor)
    cell=cell.resize((nw,nh),Image.Resampling.LANCZOS)
    tile=Image.new('RGBA',(cw,ch),(255,0,255,255))
    tile.paste(cell,((cw-nw)//2,(ch-nh)//2))
    out.paste(tile,(destination%4*cw,destination//4*ch))
    records.append({'direction':['E','W'][index],'source_path':str(patch),'source_crop':box,'source_native_size':list(src.size),'source_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'isotropic_whole_cell_scale':factor,'per_subject_fit':False})
path=root/'source/idle-corrected.png'
out.save(path)
provenance={'operation':'Replace whole image_gen neutral cells to restore missing rear waist lotus','basis_source':str(basis),'basis_sha256':hashlib.sha256(basis.read_bytes()).hexdigest(),'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'repairs':records,'new_poses_generated_by_script':False,'mirror_or_interpolation':False}
path.with_suffix('.assembly.json').write_text(json.dumps(provenance,indent=2),encoding='utf-8')
print('Wrote eight idle directions, two independently generated whole-cell corrections')

