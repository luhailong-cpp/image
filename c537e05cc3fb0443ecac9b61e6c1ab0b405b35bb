from pathlib import Path
from PIL import Image,ImageDraw
import hashlib,json,datetime,collections
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
ST=ROOT/'qdao_ui_style_recut_v10/staged'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pixel(im):return hashlib.sha256(im.mode.encode()+str(im.size).encode()+im.tobytes()).hexdigest()
data=json.loads((ROOT/'qdao_ui_style_recut_v10/contracts/current_files.json').read_text(encoding='utf-8-sig'))
rows=[]; reps={}; groups=collections.defaultdict(list)
for i,r in enumerate(data['files']):
 p=r['path']; s=ST/p;o=ROOT/p
 if not s.exists(): rows.append(dict(path=p,family=r['family'],status='missing'));continue
 im=Image.open(s).convert('RGBA'); orig=Image.open(o).convert('RGBA'); h=pixel(im)
 row=dict(index=i,path=p,family=r['family'],size=list(im.size),size_matches=im.size==orig.size,staged_sha=sha(s),production_sha=sha(o),same_pixels=pixel(orig)==h,alpha_extrema=im.getchannel('A').getextrema(),bbox=im.getbbox(),representative=reps.get(h,p),status='pending_visual')
 rows.append(row)
 if h not in reps:reps[h]=p;groups[r['family']].append(row)
for family,rs in groups.items():
 batch=6 if family in ('layers','hud') else 12
 for pg in range(0,len(rs),batch):
  part=rs[pg:pg+batch]; cols=2 if family in ('layers','hud') else 3;w=1600;cw=w//cols;ch=280
  sheet=Image.new('RGB',(w,40+ch*((len(part)+cols-1)//cols)),(230,230,219));d=ImageDraw.Draw(sheet);d.text((14,12),family+' staged native ratio '+str(pg//batch+1),fill=(0,0,0))
  for j,r in enumerate(part):
   x=(j%cols)*cw;y=40+(j//cols)*ch
   for ty in range(y+28,y+ch,16):
    for tx in range(x,x+cw,16):
     d.rectangle((tx,ty,min(tx+15,x+cw-1),min(ty+15,y+ch-1)),fill=(64,71,67) if (tx//16+ty//16)%2 else (84,91,87))
   im=Image.open(ST/r['path']).convert('RGBA'); im.thumbnail((cw-24,ch-43));sheet.paste(im,(x+(cw-im.width)//2,y+32+(ch-43-im.height)//2),im)
   d.text((x+7,y+3),str(r['index'])+' '+Path(r['path']).name[:60],fill=(0,0,0));d.text((x+7,y+16),str(r['size']),fill=(0,0,0))
  target=OUT/f'ui-{family}-{pg//batch+1:02d}.jpg';sheet.save(target,quality=94)
  for r in part:r['contact']=str(target.relative_to(ROOT))
result=dict(captured_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='pending_visual',count=len(rows),unique_pixels=len(reps),same_pixels_as_production=sum(r.get('same_pixels',False) for r in rows),dimension_errors=[r['path'] for r in rows if r.get('size_matches') is False],records=rows)
(OUT/'ui-review.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='records'},ensure_ascii=False));print({k:len(v) for k,v in groups.items()})
