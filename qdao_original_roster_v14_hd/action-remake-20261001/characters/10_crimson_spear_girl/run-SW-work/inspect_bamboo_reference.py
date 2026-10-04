from pathlib import Path
from PIL import Image,ImageDraw
import json,re,hashlib
root=Path(__file__).resolve().parent
ref=root.parent.parent/'09_bamboo_archer_girl'
m=json.loads((ref/'manifest.json').read_text(encoding='utf8'))
print('manifest top keys: '+str(list(m)))
found=set()
def scan(x):
 if isinstance(x,dict):
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
 elif isinstance(x,str):
  s=x.replace('\\','/')
  if re.fullmatch(r'runtime/run/(SE|SW)/\d\d\.png',s):found.add(s)
scan(m)
log=[]
for direction in ['SE','SW']:
 paths=sorted(p for p in found if f'/run/{direction}/' in p)
 assert len(paths)==16,(direction,len(paths))
 board=Image.new('RGB',(1280,1360),(232,235,237));d=ImageDraw.Draw(board)
 for i,p in enumerate(paths):
  fp=ref/p;im=Image.open(fp).convert('RGBA');log.append(dict(path=fp.as_posix(),sha256=hashlib.sha256(fp.read_bytes()).hexdigest(),size=list(im.size)))
  im.thumbnail((320,320));x=i%4*320;y=i//4*340;board.paste(im,(x,y),im);d.text((x+7,y+320),direction+f'{i+1:02} SOURCE09 read-only',fill=(20,20,20))
 board.save(root/f'09-reference-{direction}-contact.jpg',quality=92)
(root/'09-reference-record.json').write_text(json.dumps(dict(scope='read-only actual user-accepted09 current manifest runtime; gait reference only, not identity/weapon or automatic cross-direction frame matching',entries=log),ensure_ascii=False,indent=2),encoding='utf8')
print('verified32 paths from manifest; diagnostic contacts saved inside10 own directory')
