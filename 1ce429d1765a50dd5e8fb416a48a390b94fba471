"""Produce side-by-side review thumbnails, never overwrite source artworks."""
from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps
from grade_core import grade_image, metrics
ROOT=Path(__file__).resolve().parents[2]
V8=ROOT/'qdao_exposure_refinement_v8'
SAMPLES=[
('Login','qdao_ui_redesign_v5/01_login_2560x1080.png','screen'),
('Server selection','qdao_ui_redesign_v5/02_server_select_2560x1080.png','screen'),
('Clean login background','client_ui_refresh_20260908/additional/login_background.png','scene'),
('UI content panel','qdao_ui_redesign_v5/components/png/content_panel.png','ui'),
('Character attributes','designs/attribute-panels/v2-painted/01-character-ui-no-affinity.png','ui_soft'),
('White fox','qdao_ui_redesign_v5/pet/ling_yue_nine_tailed_fox-transparent_1254.png','character'),
('Main city map','tianyong_city_6x6/Previews/tianyong_city_master_preview_2048.png','preserve'),
]
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
records=[]
for i,(label,p,preset) in enumerate(SAMPLES,1):
    with Image.open(ROOT/p) as src:
        src.load();out=grade_image(src,preset)
        board=Image.new('RGB',(1440,414),(37,43,43));draw=ImageDraw.Draw(board)
        for j,im in enumerate([src,out]):
            rgba=im.convert('RGBA');rgba.thumbnail((700,356),Image.Resampling.LANCZOS)
            cell=Image.new('RGBA',rgba.size,(105,109,106,255));cell.alpha_composite(rgba)
            board.paste(cell.convert('RGB'),(j*720+(720-cell.width)//2,48+(356-cell.height)//2))
        draw.text((18,12),f'{label} | Original',font=font,fill='white')
        draw.text((738,12),f'Refined | {preset}',font=font,fill='white')
        dest=V8/'review'/f'comparison-{i:02}.jpg';board.save(dest,quality=90)
        records.append(dict(label=label,path=p,preset=preset,before=metrics(src),after=metrics(out),comparison=dest.relative_to(V8).as_posix()))
(V8/'review/preview_metrics.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf8')
print(json.dumps(records,indent=2))
