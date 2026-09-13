from PIL import Image
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parent

def assemble(direction,specs):
    size=443;out=Image.new('RGBA',(size*2,size*4),(255,0,255,255));records=[]
    for i,(name,cols,rows,index) in enumerate(specs):
        src=ROOT/name;im=Image.open(src).convert('RGBA');cw,ch=im.width//cols,im.height//rows
        if max(cw,ch)/min(cw,ch)>1.01:raise ValueError('non-square raw cell')
        box=(index%cols*cw,index//cols*ch,(index%cols+1)*cw,(index//cols+1)*ch)
        crop=im.crop(box);crop=crop.resize((size,size),Image.Resampling.LANCZOS)
        out.paste(crop,(i%2*size,i//2*size))
        rec={'output_frame':i+1,'source_path':str(src),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'source_native_size':list(im.size),'source_grid':[cols,rows],'source_box':list(box),'uniform_raw_cell_scale':size/cw,'output_cell_size':[size,size]}
        if src.with_suffix('.assembly.json').exists():rec['upstream_assembly']=json.loads(src.with_suffix('.assembly.json').read_text(encoding='utf8'))
        records.append(rec)
    target=ROOT/f'source/walk-{direction}-final.png';out.save(target)
    meta={'version':12,'operation':'authored cell extraction and ordering with separately generated corrections; whole raw-cell isotropic normalization only','output_path':str(target),'output_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'output_grid':[2,4],'output_size':list(out.size),'cells':records,'new_poses_generated_by_script':False,'mirror_or_interpolation':False}
    target.with_suffix('.assembly.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
    print(target)

if __name__=='__main__':
    direction=sys.argv[1];specs=json.loads((ROOT/f'source/{direction}-cells.json').read_text(encoding='utf-8-sig'));assemble(direction,specs)
