"""Assemble authored poses using equal whole-cell geometry only."""
from PIL import Image
from pathlib import Path
import json,hashlib,io,os,uuid
ROOT=Path(__file__).resolve().parent
SOURCE=ROOT/'source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
config=json.loads((ROOT/'direction-sources.json').read_text())
for direction,poses in config.items():
 if len(poses)!=8:raise ValueError('Eight genuine poses required')
 canvas=Image.new('RGBA',(1772,886),(255,0,255,255)); records=[]
 for index,pose in enumerate(poses):
  path=SOURCE/pose['source'];im=Image.open(path).convert('RGBA');cw,ch=im.width//pose['cols'],im.height//pose['rows'];i=pose['index'];box=(i%pose['cols']*cw,i//pose['cols']*ch,(i%pose['cols']+1)*cw,(i//pose['cols']+1)*ch)
  frame=im.crop(box);factor=min(443/cw,443/ch);size=(round(cw*factor),round(ch*factor));frame=frame.resize(size,Image.Resampling.LANCZOS)
  canvas.paste(frame,(index%4*443+(443-size[0])//2,index//4*443+(443-size[1])//2))
  records.append(dict(pose,phase=index+1,source_path=str(path),source_sha256=sha(path),source_native_size=list(im.size),source_crop=list(box),uniform_whole_cell_scale=factor,per_subject_fit=False))
 path=SOURCE/f'walk-{direction}-final.png';buffer=io.BytesIO();canvas.save(buffer,format='PNG');tmp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp');tmp.write_bytes(buffer.getvalue());os.replace(tmp,path)
 path.with_suffix('.assembly.json').write_text(json.dumps({'version':12,'operation':'whole independently authored cells; chronological reorder and uniform cell resampling only','direction':direction,'output_sha256':sha(path),'output_grid':[4,2],'output_size':[1772,886],'sources':records,'mirroring':False,'interpolation_or_duplicate_pose':False},indent=2),encoding='utf-8')
 print('Assembled '+direction)
