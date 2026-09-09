"""Build a QA contact sheet from actual Unity captures, never concept renders."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json, hashlib, datetime

root = Path(__file__).resolve().parent
qa = root / 'qa'
screens = [
    ('01-login-native.png', '登录'), ('02-server-native.png', '选择服务器'),
    ('03-account-native.png', '账号登录'), ('04-role-select-native.png', '选择角色'),
    ('05-role-create-native.png', '创建角色'), ('06-main-city-native.png', '主城与操作入口'),
    ('07-attribute-native.png', '角色属性'), ('07b-attribute-eight-rows-native.png', '属性加点 · 八项'),
    ('08-battle-native.png', '战斗'), ('09-queue-native.png', '匹配'),
    ('10-spectate-native.png', '观战'), ('11-result-native.png', '战斗结算'),
]
available = [(qa/name, label) for name,label in screens if (qa/name).exists()]
font = ImageFont.truetype('E:/work/mmorpg-client/Assets/Resources/Fonts/SimKai.ttf', 30)
width, tile_w, tile_h, gap, header = 2000, 960, 456, 24, 90
rows = (len(available)+1)//2
board = Image.new('RGB', (width, header + rows*tile_h + gap), '#173F37')
draw = ImageDraw.Draw(board)
draw.text((32,25), '五行奇谈 · Unity 原生界面实拍', font=font, fill='#FFF5D4')
records = []
for i,(file,label) in enumerate(available):
    x, y = gap+(i%2)*(tile_w+gap), header+(i//2)*tile_h
    image = Image.open(file).convert('RGB')
    board.paste(ImageOps.contain(image,(tile_w,405),Image.Resampling.LANCZOS),(x,y))
    draw.text((x+8,y+411),label,font=font,fill='#FFF5D4')
    records.append({'file':str(file),'label':label,'size':list(image.size),
                    'sha256':hashlib.sha256(file.read_bytes()).hexdigest()})
out = root/'client-ui-overview.jpg'
board.save(out, quality=91)
(root/'screenshots.json').write_text(json.dumps({
    'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'source':'Native Unity UI rendered through official Unity MCP invocation of editor capture helpers',
    'screens': records, 'missing_expected':[name for name,_ in screens if not (qa/name).exists()],
    'overview':str(out), 'not_a_concept_mockup':True
},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'overview':str(out),'screens':len(records),'missing':[name for name,_ in screens if not (qa/name).exists()]},ensure_ascii=False))
