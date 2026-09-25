"""Temporary QA composites; never modifies any sprite or creates action frames."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'10-delivery-preview/revisions/s-full-review-20260923'
OUT=ROOT/'10-work/review-s-20260923'
OUT.mkdir(exist_ok=True)
for start in (1,5,9,13):
    board=Image.new('RGB',(2160,660),'#242a31')
    for col,frame in enumerate(range(start,start+4)):
        im=Image.open(SOURCE/f'walk/S/{frame:02}.png').convert('RGBA')
        crop=im.crop((400,650,670,960)).resize((540,620),Image.Resampling.NEAREST)
        board.paste(crop,(col*540,20),crop)
        ImageDraw.Draw(board).text((col*540+8,642),f'S{frame:02}: final PNG legs at 2x, nearest QA only',fill='white')
    board.save(OUT/f'legs-{start:02}.png')
for name,bg in (('dark','#242a31'),('light','#f6f1e7')):
    im=Image.open(SOURCE/'idle/S.png').convert('RGBA')
    board=Image.new('RGB',im.size,bg);board.paste(im,(0,0),im)
    board.save(OUT/f'idle-{name}.png')
print(OUT)
