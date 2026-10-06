from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image,ImageDraw,ImageFont
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
SPRING=ROOT/'r08_c10/regional/native.png'
DAY=ROOT.parent/'lanxian_day/r08_c10/regional/regional.png'
C09=ROOT/'r08_c09/repairs/join-endpoint/candidate_4096.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(SPRING)=='00b1d3047f8dc300c996ef995b69c88e2038eb170054aebf3c06bfb66e6f26f8'
assert sha(DAY)=='1bafb2cf30bb86e801677acd9eb3b728e946a691ba745e001db0eefcf3d972ab'
assert sha(C09)=='eacc709f26e6224c3b24e493bb4a3a60b8eb44cda18afa787e208f5a1805ff38'
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',17)
day=Image.open(DAY).convert('RGB');spring=Image.open(SPRING).convert('RGB')
boxes={'planter-post-base':[350,400,1010,930],'canopy-trunk':[360,110,820,610],'northwest-ring':[20,0,415,610]}
manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'role':'QA exact crops only; no production art',
    'sources':[{'file':str(p),'sha256':sha(p)} for p in [DAY,SPRING,C09]],'resampling':None,'warp':None,
    'c10Comparisons':[],'c09InteriorSamples':[]}
for name,b in boxes.items():
    w=b[2]-b[0];h=b[3]-b[1]
    board=Image.new('RGB',(2*w,h+30),'#efebe0');d=ImageDraw.Draw(board)
    d.text((8,5),'Day - actual regional pixels',font=font,fill='black')
    d.text((w+8,5),'Spring - actual regional pixels',font=font,fill='black')
    board.paste(day.crop(b),(0,30));board.paste(spring.crop(b),(w,30))
    p=OUT/f'c10-{name}-comparison.png';board.save(p)
    manifest['c10Comparisons'].append({'file':str(p),'sha256':sha(p),'bothSourceCropLTRB':b})
im=Image.open(C09).convert('RGB')
for row in range(4):
    board=Image.new('RGB',(1280,1340),'#efebe0');d=ImageDraw.Draw(board)
    for col in range(4):
        x=col*1024+192;y=row*1024+192;b=(x,y,x+640,y+640)
        dx=(col%2)*640;dy=(col//2)*670
        d.text((dx+8,dy+5),f'c09 interior r{row+1:02d} c{col+1:02d} - 1:1',font=font,fill='black')
        board.paste(im.crop(b),(dx,dy+30))
        manifest['c09InteriorSamples'].append({'row':row+1,'column':col+1,'sourceCropLTRB':list(b),
            'board':str(OUT/f'c09-interior-row{row+1:02d}.png'),'boardImageRectLTRB':[dx,dy+30,dx+640,dy+670]})
    board.save(OUT/f'c09-interior-row{row+1:02d}.png')
manifest['c09SampleAreaFraction']=16*640*640/(4096*4096)
(OUT/'derivation.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(OUT),'c09SampleAreaFraction':manifest['c09SampleAreaFraction']}))
