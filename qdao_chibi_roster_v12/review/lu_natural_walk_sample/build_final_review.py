from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib,argparse
parser=argparse.ArgumentParser();parser.add_argument('--character',default='24_lu_dongbin');parser.add_argument('--source-root',default=r'E:\work\image\qdao_chibi_roster_v12\candidate-stable-body');args=parser.parse_args()
ROOT=Path(args.source_root)/args.character
OUT=ROOT/'review';OUT.mkdir(exist_ok=True)
DIRS=['N','NE','E','SE','S','SW','W','NW']
report={}
for direction in DIRS:
    poses=[Image.open(ROOT/'idle'/f'{direction}.png').convert('RGBA')]+[Image.open(ROOT/'walk'/direction/f'{i:02d}.png').convert('RGBA') for i in range(1,9)]
    board=Image.new('RGBA',(768,840),'#e8e3d9');draw=ImageDraw.Draw(board)
    for i,frame in enumerate(poses):
        x=i%3*256;y=i//3*280
        thumb=frame.resize((256,256),Image.Resampling.LANCZOS);board.alpha_composite(thumb,(x,y+24))
        draw.text((x+10,y+6),f'{direction} '+('IDLE' if i==0 else f'{i:02d}'),fill='#243d35')
    board.convert('RGB').save(OUT/f'{direction}-idle-walk.jpg',quality=94)
    report[direction]={'visible':len(poses),'walk_unique':len({hashlib.sha256(im.tobytes()).hexdigest() for im in poses[1:]}),'idle_unique':poses[0].tobytes() not in [p.tobytes() for p in poses[1:]]}
boards=[]
for phase in range(1,9):
    board=Image.new('RGBA',(1024,580),'#e8e3d9');draw=ImageDraw.Draw(board)
    for index,direction in enumerate(DIRS):
        x=index%4*256;y=index//4*290
        frame=Image.open(ROOT/'walk'/direction/f'{phase:02d}.png').convert('RGBA').resize((256,256),Image.Resampling.LANCZOS)
        board.alpha_composite(frame,(x,y+30));draw.text((x+12,y+8),direction,fill='#243d35')
    boards.append(board.convert('RGB'))
boards[0].save(OUT/'eight-directions.gif',save_all=True,append_images=boards[1:],duration=60,loop=0,disposal=2)
boards[0].save(OUT/'eight-directions-phase01.jpg',quality=95)
(ROOT/'review/contact-evidence.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print('Built 8 contact boards and real 8-frame direction grid GIF')
