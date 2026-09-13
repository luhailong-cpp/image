"""Replace rejected cells with separately ImageGen-authored correction cells."""
from pathlib import Path
import hashlib,json,shutil
from PIL import Image
root=Path(__file__).resolve().parent
source=root/'source'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
fixes={2:{0:('fix-phase02-N.png',None,1,1)},4:{1:('fix-diagonal-poses.png',0,2,2)},5:{1:('fix-diagonal-poses.png',1,2,2)},6:{1:('fix-diagonal-poses.png',2,2,2)},7:{1:('fix-phase07-directions.png',1,4,2),5:('fix-phase07-directions.png',5,4,2)},8:{0:('fix-phase08-N.png',None,1,1),7:('fix-diagonal-poses.png',3,2,2)}}
for phase,replacements in fixes.items():
    output=source/f'phase{phase:02d}-turnaround.png'
    original=source/f'phase{phase:02d}-turnaround-original.png'
    if not original.exists():shutil.copy2(output,original)
    base=Image.open(original).convert('RGB'); cw,ch=base.width//4,base.height//2
    assert cw==ch
    canvas=Image.new('RGB',(cw*4,ch*2),(255,0,255)); records=[]
    for index in range(8):
        path=original; image=base; box=[index%4*cw,index//4*ch,(index%4+1)*cw,(index//4+1)*ch]
        if index in replacements:
            name,view,cols,rows=replacements[index]; path=source/name; image=Image.open(path).convert('RGB')
            if view is None:box=[0,0,image.width,image.height]
            else:
                w,h=image.width//cols,image.height//rows
                box=[view%cols*w,view//cols*h,(view%cols+1)*w,(view//cols+1)*h]
        crop=image.crop(box); scale=min(cw/crop.width,ch/crop.height)
        size=(round(crop.width*scale),round(crop.height*scale))
        if crop.size!=size:crop=crop.resize(size,Image.Resampling.LANCZOS)
        x=index%4*cw+(cw-size[0])//2; y=index//4*ch+(ch-size[1])//2
        canvas.paste(crop,(x,y))
        records.append({'view_index':index,'direction':['N','NE','E','SE','S','SW','W','NW'][index],'source_path':str(path),'source_sha256':sha(path),'source_native_size':list(image.size),'crop_box':box,'uniform_raw_cell_scale':scale,'output_paste_xy':[x,y],'separately_authored_correction':index in replacements})
    canvas.save(output)
    metadata={'version':12,'operation':'replace visually rejected raw cells with independently ImageGen-authored correction cells; isotropic cell resolution normalization only','output_path':str(output),'output_sha256':sha(output),'output_size':list(canvas.size),'output_grid':[4,2],'phase':phase,'sources':records,'new_poses_generated_by_script':False,'mirrored_frames':False,'repeated_or_interpolated_poses':False,'per_frame_body_fit':False}
    output.with_suffix('.assembly.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2),encoding='utf-8')
    print(phase,str(output),flush=True)
