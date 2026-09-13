"""Reinsert independent image_gen poses and reorder accepted whole cells, preserving source provenance."""
from pathlib import Path
import json, hashlib
from PIL import Image
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source'
OUT=SOURCE/'phase-corrected'
DIRECTIONS=['N','NE','E','SE','S','SW','W','NW']
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads((ROOT/'cell-repairs.json').read_text(encoding='utf-8-sig'))
OUT.mkdir(exist_ok=True)
for phase in range(1,9):
    basis=SOURCE/f'phase-{phase:02d}.png'
    raw=Image.open(basis).convert('RGBA')
    cw,ch=raw.width//4,raw.height//2
    canvas=raw.crop((0,0,cw*4,ch*2))
    records=[]
    for repair in config:
        if repair['phase']!=phase: continue
        path=SOURCE/repair['source']
        src=Image.open(path).convert('RGBA')
        rows,cols=repair['rows'],repair['cols']
        sw,sh=src.width//cols,src.height//rows
        index=repair['index']
        x,y=index%cols*sw,index//cols*sh
        crop=src.crop((x,y,x+sw,y+sh))
        factor=min(cw/sw,ch/sh)
        nw,nh=round(sw*factor),round(sh*factor)
        tile=Image.new('RGBA',(cw,ch),(255,0,255,255))
        crop=crop.resize((nw,nh),Image.Resampling.LANCZOS)
        tile.paste(crop,((cw-nw)//2,(ch-nh)//2))
        dst=DIRECTIONS.index(repair['direction'])
        canvas.paste(tile,(dst%4*cw,dst//4*ch))
        records.append(dict(repair,source_path=str(path),source_sha256=sha(path),source_native_size=list(src.size),source_crop=[x,y,x+sw,y+sh],isotropic_whole_cell_scale=factor,per_subject_fit=False))
    path=OUT/f'phase-{phase:02d}.png'
    canvas.save(path)
    provenance={'version':12,'operation':'reinsert whole independently authored image_gen cells and reorder phase cells only','output_sha256':sha(path),'output_size':list(canvas.size),'basis_source':str(basis),'basis_sha256':sha(basis),'basis_native_size':list(raw.size),'repairs':records,'new_poses_generated_by_script':False,'mirror_or_interpolation':False}
    path.with_suffix('.assembly.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),encoding='utf-8')
print('Wrote 8 corrected source grids with auditable cell provenance')
