"""Reference-only boards from genuine source cells; never creates deliverable poses."""
import argparse,json,hashlib
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--character',required=True);p.add_argument('--direction',required=True,choices=['N','NE','E','SE','S','SW','W','NW']);p.add_argument('--frames',default='1,5,9,13');p.add_argument('--name',default='endpoints');a=p.parse_args()
 assert all(c.isalnum() or c in '_-' for c in a.character+a.name)
 frames=[int(x) for x in a.frames.split(',')];assert len(frames)==len(set(frames)) and all(1<=x<=16 for x in frames)
 out=ROOT/'candidate'/a.character;records=json.loads((out/'processing/frame-sources.json').read_text(encoding='utf-8-sig'));dest=ROOT/'generation'/a.character/(a.direction+'-'+a.name);dest.mkdir(parents=True,exist_ok=True);cells=[];evidence=[]
 for frame in frames:
  r=records[f'walk/{a.direction}/{frame:02d}.png']['source'];path=out/r['path'];assert sha(path)==r['sha256'];raw=Image.open(path).convert('RGBA');cell=raw.crop(r['cell_xyxy']);factor=512/max(cell.width,cell.height);size=(round(cell.width*factor),round(cell.height*factor));cell=cell.resize(size,Image.Resampling.LANCZOS);canvas=Image.new('RGBA',(512,512),(255,0,255,255));offset=((512-cell.width)//2,(512-cell.height)//2);canvas.alpha_composite(cell,offset);name=f'{frame:02d}-source-cell.png';canvas.save(dest/name);cells.append(canvas);evidence.append({'frame':frame,'source_path':str(path),'source_sha256':sha(path),'cell_xyxy':r['cell_xyxy'],'whole_cell_reference_scale':factor,'canvas_offset':list(offset),'reference':name,'reference_sha256':sha(dest/name)})
 if len(cells)==4:
  for letter,order in [('A',[0,1,2,3]),('B',[1,2,3,0])]:
   board=Image.new('RGBA',(1024,1024),(255,0,255,255))
   for slot,index in enumerate(order):y,x=divmod(slot,2);board.paste(cells[index],(x*512,y*512))
   board.save(dest/f'{letter}.png')
 (dest/'reference-provenance.json').write_text(json.dumps({'purpose':'reference layout only, not animation exports','common_scale':1,'subject_bbox_scaling':False,'operation':'complete original native cells uniformly normalize to512 then center in512canvas and reorder','frames':evidence},indent=2)+'\n',encoding='utf-8');print(dest)
if __name__=='__main__':main()
