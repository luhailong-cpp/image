"""Mechanical contact sheet only; excludes every preview pixel from delivery art."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT.parents[1]
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
ledger = json.loads((ROOT/'current-coverage-ledger.json').read_text(encoding='utf-8'))
stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out = ROOT/'previews'/stamp
out.mkdir(parents=True, exist_ok=False)
font_path = Path('C:/Windows/Fonts/arial.ttf')
font = ImageFont.truetype(str(font_path), 21) if font_path.exists() else ImageFont.load_default()
small = ImageFont.truetype(str(font_path), 16) if font_path.exists() else ImageFont.load_default()
present=[t for t in ledger['tiles'] if t['candidateExists']]
rows=[int(t['tile'][1:3]) for t in present];cols=[int(t['tile'][5:7]) for t in present]
rmin,rmax,cmin,cmax=min(rows),max(rows),min(cols),max(cols)
cell=min(384,2048//(cmax-cmin+1),1800//(rmax-rmin+1))
width=max(1000,(cmax-cmin+1)*cell);height=112+(rmax-rmin+1)*(cell+32)+64
sheet = Image.new('RGB', (width,height), '#162329')
draw = ImageDraw.Draw(sheet)
draw.text((20,16), f'TIANYONG FESTIVAL | r{rmin:02}-r{rmax:02} / c{cmin:02}-c{cmax:02} | CANDIDATE CONTACT SHEET', font=font, fill='#ffffff')
draw.text((20,49), f'{len(present)} / 256 coordinates have candidates. 0 production accepted. Resized preview only.', font=small, fill='#f6c472')
sources=[]
indexed={t['tile']:t for t in ledger['tiles']}
for row in range(rmin,rmax+1):
    for col in range(cmin,cmax+1):
        tile=indexed[f'r{row:02}_c{col:02}']
        x=(col-cmin)*cell;y=112+(row-rmin)*(cell+32)
        if not tile['candidateExists']:
            draw.rectangle((x,y,x+cell-1,y+cell-1),fill='#29353a')
            draw.text((x+10,y+10),tile['tile']+' MISSING',font=small,fill='#d5baba')
            continue
        c=tile['candidate'];p=ART/c['file']
        assert sha(p)==c['sha256'], str(p)
        with Image.open(p) as im:
            im.load();assert im.size==(4096,4096)
            thumb=im.convert('RGB').resize((cell,cell),Image.Resampling.LANCZOS)
        sheet.paste(thumb,(x,y))
        draw.rectangle((x,y-29,x+cell-1,y-1),fill='#233a40')
        draw.text((x+10,y-25),tile['tile']+'  candidate',font=small,fill='#e1e8df')
        sources.append({'tile':tile['tile'],'file':c['file'],'sha256':c['sha256'],'sourcePixels':[4096,4096],'displayPixels':[cell,cell]})
draw.text((20,height-33),'For coverage and composition inspection only. Seam acceptance uses separate native-pixel evidence.',font=small,fill='#ced8d5')
png=out/'candidate-contact-sheet-preview-only.png'
sheet.save(png)
record={'schemaVersion':1,'role':'resized_preview_not_production_art','operation':'mechanical contact sheet with coordinate labels','createdAtUtc':datetime.now(timezone.utc).isoformat(),'sources':sources,'ledgerSha256':sha(ROOT/'current-coverage-ledger.json'),'output':{'file':str(png),'sha256':sha(png)},'formalArtAccepted':False}
(out/'preview-record.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record['output']))
