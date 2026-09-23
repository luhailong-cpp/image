"""Review the explicitly selected E candidates without mutating runtime."""
from pathlib import Path
import json, hashlib, subprocess, sys
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
VERSIONS = {5: 3, 6: 2, 7: 2, 8: 3, 9: 6, 10: 2, 11: 2, 12: 3, 13: 4}
rows = []
for n in range(1, 17):
    g = R / '15-generation' / f'E{n:02}-walk-v{VERSIONS.get(n, 1)}'
    if not (g / 'raw.png').exists():
        print('missing raw', g.name)
        continue
    result = subprocess.run([sys.executable, str(R/'15-tools/archive_frame.py'),
        '--generation-dir', str(g), '--source', str(g/'raw.png'),
        '--request-json', str(g/'request.json'), '--receipt-json', str(g/'receipt.json'),
        '--direction', 'E', '--kind', 'walk', '--frame', str(n), '--process'],
        capture_output=True, text=True, encoding='utf8')
    if result.returncode:
        print(g.name, result.stderr[-300:])
        continue
    p = g/'processing-fixed088-v1/final.png'
    rows.append({'frame':n, 'generation':g.name, 'path':str(p),
                 'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
out = R/'15-review'
for name,bg in [('light',(242,235,214)),('dark',(26,40,48))]:
    sheet=Image.new('RGB',(1024,1128),bg)
    feet=Image.new('RGB',(1920,1120),bg)
    seam=Image.new('RGB',(1024,282),bg)
    images={}
    for row in rows:
        n=row['frame'];im=Image.open(row['path']).convert('RGBA')
        canvas=Image.new('RGBA',(1024,1024),(*bg,255));canvas.alpha_composite(im)
        small=canvas.convert('RGB').resize((256,256),Image.Resampling.LANCZOS)
        images[n]=small;x=((n-1)%4)*256;y=((n-1)//4)*282
        sheet.paste(small,(x,y));ImageDraw.Draw(sheet).text((x+6,y+260),row['generation'],fill=(80,150,180))
        x=((n-1)%4)*480;y=((n-1)//4)*280
        feet.paste(canvas.crop((300,690,780,970)),(x,y));ImageDraw.Draw(feet).text((x+6,y+5),f'E{n:02}',fill=(80,150,180))
    for col,n in enumerate([15,16,1,2]):
        if n in images: seam.paste(images[n],(col*256,0));ImageDraw.Draw(seam).text((col*256+6,260),f'E{n:02}',fill=(80,150,180))
    sheet.save(out/f'E-revised-candidates-{name}.png')
    feet.save(out/f'E-revised-feet-{name}.png')
    seam.save(out/f'E-revised-seam-{name}.png')
(out/'E-revised-candidate-map.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print('processed candidate count',len(rows))
