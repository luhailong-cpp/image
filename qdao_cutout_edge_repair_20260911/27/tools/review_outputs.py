"""Read-only contact evidence from this batch's processed directional frames."""
from pathlib import Path
import argparse, json
from PIL import Image, ImageDraw, ImageFont

PACK=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('directions',nargs='+');p.add_argument('--output-dir',type=Path,default=PACK/'staged-v2');args=p.parse_args();out=args.output_dir
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18);result=[]
    for direction in args.directions:
        frames=[Image.open(out/'walk'/direction/f'{i:02}.png').convert('RGBA') for i in range(1,5)]
        page=Image.new('RGB',(1600,1250),'#eee7d9');draw=ImageDraw.Draw(page)
        for i,im in enumerate(frames):
            for row,bg in enumerate(['#f0ecdf','#142d26']):
                tile=Image.new('RGBA',(400,416),bg);thumb=im.resize((400,400),Image.Resampling.LANCZOS);tile.alpha_composite(thumb,(0,8));page.paste(tile.convert('RGB'),(i*400,row*450+30));draw.text((i*400+8,row*450+6),f'{direction} {i+1} '+['LIGHT','DARK'][row],font=font,fill='#14372d')
            tile=Image.new('RGBA',(400,320),'#f0ecdf');crop=im.crop((96,260,416,508)).resize((400,310),Image.Resampling.NEAREST);tile.alpha_composite(crop,(0,5));page.paste(tile.convert('RGB'),(i*400,930));draw.text((i*400+8,906),f'{direction} {i+1} LEGS 1.25x',font=font,fill='#14372d')
        dest=out/'processing'/f'{direction}-full-legs-review.jpg';page.save(dest,quality=98,subsampling=0);result.append(str(dest))
    print(json.dumps(result))

if __name__=='__main__':main()
