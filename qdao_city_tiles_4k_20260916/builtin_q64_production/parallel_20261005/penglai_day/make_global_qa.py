"""Native crop boards for changed adjacent candidates and four-tile junctions."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime

B=Path(__file__).resolve().parent
Q=B/'qa/global-boundaries'

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value): Path(path).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')

def main():
    Q.mkdir(parents=True,exist_ok=True)
    assets=json.loads((B/'asset-index.json').read_text(encoding='utf8'))['currentCandidates']
    images={}; sources={}
    for key,item in assets.items():
        actual=sha(item['file']); assert actual==item['sha256'],key
        images[key]=Image.open(item['file']).convert('RGB');assert images[key].size==(4096,4096)
        sources[key]={'file':item['file'],'sha256':actual}
    changed=[]
    def save(name,board,keys,scope):
        record=Q/(name+'.json'); refs={key:sources[key] for key in keys}
        if record.exists() and json.loads(record.read_text(encoding='utf8')).get('sources')==refs: return
        path=Q/(name+'.png');board.save(path)
        write(record,{'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'file':str(path),'sha256':sha(path),'sources':refs,'operation':'Integer native pixel crops and placements only; labels outside image pixels. No resample.','scale':1,'scope':scope,'visualReview':'pending','formalAccepted':False})
        changed.append(name)
    for key,im in images.items():
        r=int(key[1:3]);c=int(key[5:7]);right=f'r{r:02}_c{c+1:02}';below=f'r{r+1:02}_c{c:02}';diagonal=f'r{r+1:02}_c{c+1:02}'
        if right in images:
            other=images[right]; board=Image.new('RGB',(1280,1052),(35,35,35));draw=ImageDraw.Draw(board)
            for n in range(4):
                x=n*320;y=n*1024
                draw.text((x+4,5),f'{key}/{right} y{y}',fill='white')
                board.paste(im.crop((3936,y,4096,y+1024)),(x,28))
                board.paste(other.crop((0,y,160,y+1024)),(x+160,28))
            save(f'{key}--{right}',board,[key,right],'Vertical shared edge, four adjacent native segments left to right. Segment split is presentation only.')
        if below in images:
            other=images[below];board=Image.new('RGB',(1024,1392),(35,35,35));draw=ImageDraw.Draw(board)
            for n in range(4):
                y=n*348;x=n*1024
                draw.text((4,y+5),f'{key}/{below} x{x}',fill='white')
                board.paste(im.crop((x,3936,x+1024,4096)),(0,y+28))
                board.paste(other.crop((x,0,x+1024,160)),(0,y+188))
            save(f'{key}--{below}',board,[key,below],'Horizontal shared edge, four native segments stacked top to bottom.')
        if right in images and below in images and diagonal in images:
            board=Image.new('RGB',(640,668),(35,35,35));ImageDraw.Draw(board).text((4,5),f'{key} / {right} / {below} / {diagonal}',fill='white')
            for name,box,xy in [(key,(3776,3776,4096,4096),(0,28)),(right,(0,3776,320,4096),(320,28)),(below,(3776,0,4096,320),(0,348)),(diagonal,(0,0,320,320),(320,348))]:board.paste(images[name].crop(box),xy)
            save(f'junction-{key}',board,[key,right,below,diagonal],'Four-tile crossing at native scale.')
    print(json.dumps({'newOrChangedBoards':changed,'formalAccepted':False}))

if __name__=='__main__': main()
