"""Export a ready four-cell intersection at final QA scale, without approval."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
from PIL import Image
from workflow import OUTPUT_ROOT,safe_output,sha256,read_json,save_image,write_json
def run(tile_name,row,col):
 assert 1<=row<=3 and 1<=col<=3
 tile=safe_output(OUTPUT_ROOT/tile_name);assert tile.parent==OUTPUT_ROOT
 out=safe_output(tile/'ready-intersection-qa'/f'r{row}_c{col}');assert not out.exists()
 out.mkdir(parents=True);board=Image.new('RGB',(512,512));maps=[]
 for r,c,box,xy in [(row,col,[883,883,1139,1139],[0,0]),(row,col+1,[115,883,371,1139],[256,0]),(row+1,col,[883,115,1139,371],[0,256]),(row+1,col+1,[115,115,371,371],[256,256])]:
  p=tile/f'native/r{r:02d}_c{c:02d}.png';g=Path(str(p)+'.generation.json');rec=read_json(g)
  assert sha256(p)==rec['sha256'];im=Image.open(p).convert('RGB');assert im.size==(1254,1254)
  crop=im.crop(box);board.paste(crop,xy)
  maps.append({'file':str(p),'sha256':rec['sha256'],'generationRecord':{'file':str(g),'sha256':sha256(g)},'sourceBoxXYXY':box,'destinationXY':xy,'decodedRgbSha256':hashlib.sha256(crop.tobytes()).hexdigest()})
 image=save_image(out/'intersection512.png',board)
 image.update(decodedRgbSha256=hashlib.sha256(board.tobytes()).hexdigest(),pixelMappings=maps,actuallyViewed=False,
   finalCoreBoxXYXY=[col*1024-256,row*1024-256,col*1024+256,row*1024+256])
 manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':tile_name,'row':row,'col':col,'output':image,'operation':'integer crop/paste only','resampling':'none','reviewStatus':'pending','formalAccepted':False}
 write_json(out/'manifest.json',manifest);print(json.dumps({'file':image['file'],'sha256':image['sha256']}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('tile');p.add_argument('row',type=int);p.add_argument('col',type=int)
 a=p.parse_args();run(a.tile,a.row,a.col)
