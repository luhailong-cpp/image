from pathlib import Path
import sys,json,hashlib
from PIL import Image
sys.path.insert(0,r'E:\work\image\qdao_chibi_roster_v12')
from process_roster import load_processor,DEFAULT_PROCESSOR,bounds
r=Path(r'E:\work\image\qdao_chibi_roster_v12\25_lion_drum_guard');p=r/'source'/'walk-E-draft.png';raw=Image.open(p).convert('RGBA');clean=load_processor(DEFAULT_PROCESSOR).remove_bg_magenta(raw.copy(),50,80);row_edges=[0,376,753,1118,1536];side=384
for i in range(8):
    col=i%2;row=i//2;x=col*512;y0,y1=row_edges[row:row+2];b=bounds(clean.crop((x,y0,x+512,y1)));assert b and b[0]>64 and b[2]<448 and b[1]>0 and b[3]<y1-y0,(i,b)
    top=y0+b[1];bottom=y0+b[3];box=(x+64,top,x+448,bottom);crop=raw.crop(box);assert crop.height<side
    out=r/'source'/f'E{i+1:02d}-draft-crop.png';canvas=Image.new('RGBA',(side,side),(255,0,255,255));py=(side-crop.height)//2;canvas.paste(crop,(0,py));canvas.save(out)
    meta={'operation':'extract full visible row subject at native pixel scale then pad only empty magenta to a square; translation only','source_path':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_native_size':list(raw.size),'source_grid':'nonuniform authored rows; actual alpha extents recorded','source_scan_box':[x,y0,x+512,y1],'source_subject_bbox_within_scan':b,'output_source_box':list(box),'output_paste_xy':[0,py],'uniform_raw_cell_scale':1.0,'no_visible_pixels_removed':True,'output_size':[side,side],'output_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'mirror_or_interpolation':False}
    out.with_suffix('.assembly.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
print('eight complete square review crops with native-scale color/geometry intact',side)
