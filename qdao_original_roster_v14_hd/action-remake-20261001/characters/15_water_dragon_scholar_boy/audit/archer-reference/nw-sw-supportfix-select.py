from pathlib import Path
import json,hashlib
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parents[2]
s=json.loads((B/'audit/archer-reference/nw-sw-grounding-selection.json').read_text(encoding='utf-8-sig'))
mapping={}
for n in [5,6,7,8]:mapping[f'run/NW/{n:02}']=f'run-NW-{n:02}-supportfix-v2'
for n in [9,10]:mapping[f'run/NW/{n:02}']=f'run-NW-{n:02}-supportfix-v1'
for n in range(5,13):mapping[f'run/SW/{n:02}']=f'run-SW-{n:02}-supportfix-v1'
mapping.update({'run/NW/05':'run-NW-05-supportfix-v3','run/NW/06':'run-NW-06-supportfix-v3','run/NW/07':'run-NW-07-supportfix-v4','run/NW/08':'run-NW-08-supportfix-v4','run/NW/10':'run-NW-10-supportfix-v2','run/SW/05':'run-SW-05-supportfix-v2','run/SW/06':'run-SW-06-supportfix-v2'})
for r in s['rows']:
 key=mapping.get(r['slot'])
 if key:
  r['supersededBySupportFix']={k:r.get(k) for k in ['candidateKey','file','sha256','generationRecord']}
  g=json.loads((B/f'provenance/generation/{key}.json').read_text(encoding='utf-8-sig'))
  r.update(candidateKey=key,file=str(B/f'sources/new/{key}.png'),sha256=g['sha256'],generationRecord=f'provenance/generation/{key}.json',export={'native':1254,'scaleCanvasTo':940,'offset':[42,49],'canvas':1024})
 r['staticReviewResult']='已查看原图；分足与位置段仍须当前连图复审，不继承旧全过结论'
 r['supportFootVerified']=None
s.update(scope='NW/SW support correction candidates; open spatial issues recorded separately',updatedAt=datetime.now(timezone.utc).isoformat(),dynamicPlaybackObserved=False)
(B/'audit/archer-reference/nw-sw-supportfix-selection.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
font=ImageFont.truetype('C:/Windows/Fonts/msyh.ttc',18)
for direction in ['NW','SW']:
 c=Image.new('RGB',(1280,1408),(225,230,227));d=ImageDraw.Draw(c)
 for i,r in enumerate(r for r in s['rows'] if f'/{direction}/' in r['slot']):
  im=Image.open(r['file']).convert('RGBA')
  assert hashlib.sha256(Path(r['file']).read_bytes()).hexdigest()==r['sha256']
  if im.width==1254:
   o=Image.new('RGBA',(1024,1024));o.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49));im=o
  thumb=im.resize((320,320),Image.Resampling.LANCZOS);x=i%4*320;y=i//4*352;c.paste(thumb,(x,y+24),thumb)
  d.text((x+8,y+1),f"{direction} {i+1:02} {r['grounding']['supportFoot']} / "+('new' if r['slot'] in mapping else 'retained'),font=font,fill=(20,35,35))
 c.save(B/f'audit/archer-reference/nw-sw-{direction}-supportfix-contact.png')
print('32 rows written, 14 support-fix candidates, no master/runtime edits')
