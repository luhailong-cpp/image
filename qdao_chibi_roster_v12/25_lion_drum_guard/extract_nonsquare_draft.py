from pathlib import Path
import sys,json,hashlib,numpy as np
from PIL import Image
sys.path.insert(0,r'E:\work\image\qdao_chibi_roster_v12')
from process_roster import load_processor,DEFAULT_PROCESSOR,bounds
r=Path(__file__).resolve().parent;d=sys.argv[1];p=r/'source'/f'walk-{d}-draft.png';raw=Image.open(p).convert('RGBA');clean=load_processor(DEFAULT_PROCESSOR).remove_bg_magenta(raw.copy(),50,80);aa=np.array(clean)[:,:,3]>8;cw=raw.width//2;side=min(cw,raw.height//4)
for col in range(2):
    ys=np.flatnonzero(aa[:,col*cw:(col+1)*cw].any(axis=1));runs=[]
    for y in ys:
        if not runs or y>runs[-1][1]+1:runs.append([int(y),int(y)])
        else:runs[-1][1]=int(y)
    assert len(runs)==4,(col,runs)
    for row,(top,last) in enumerate(runs):
        i=row*2+col;x=col*cw;dx=(cw-side)//2;bottom=last+1;b=bounds(clean.crop((x,top,x+cw,bottom)));assert b and b[0]>dx and b[2]<dx+side and bottom-top<side,(i,b)
        box=(x+dx,top,x+dx+side,bottom);crop=raw.crop(box);out=r/'source'/f'{d}{i+1:02d}-draft-crop.png';canvas=Image.new('RGBA',(side,side),(255,0,255,255));py=(side-crop.height)//2;canvas.paste(crop,(0,py));canvas.save(out)
        meta={'operation':'extract entire alpha row subject at native pixel scale then pad empty magenta to a square; translation only','source_path':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_native_size':list(raw.size),'source_grid':'two columns and four separated alpha runs per column','source_scan_box':[x,top,x+cw,bottom],'source_subject_bbox_within_scan':b,'output_source_box':list(box),'output_paste_xy':[0,py],'uniform_raw_cell_scale':1.0,'no_visible_pixels_removed':True,'output_size':[side,side],'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'mirror_or_interpolation':False}
        out.with_suffix('.assembly.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print(d,'eight complete square native-scale review cells',side)
