from pathlib import Path
import subprocess,hashlib,json
from PIL import Image,ImageDraw
root=Path('E:/work/image/qdao_original_roster_v13'); repo=root.parent; commit='9adcf9291e4a867601868889a5965f3cd48630ba'; pack='character_move_8dir'
dest=root/'baseline'/pack; dest.mkdir(parents=True,exist_ok=True); records=[]
for line in subprocess.check_output(['git','-C',str(repo),'ls-tree','-r','-z',commit,'--',pack]).split(b'\0'):
 if not line: continue
 meta,path=line.split(b'\t',1); typ=meta.split()[1]; oid=meta.split()[2].decode(); rel=path.decode(); assert typ==b'blob'; data=subprocess.check_output(['git','-C',str(repo),'cat-file','blob',oid]); p=root/'baseline'/rel; p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists(): assert p.read_bytes()==data
 else:p.write_bytes(data)
 records.append({'path':rel,'git_blob':oid,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
(root/'baseline/character-move-8dir-extraction.json').write_text(json.dumps({'commit':commit,'files':records},indent=2),encoding='utf8')
review=root/'review/00_reference_topright_boy';review.mkdir(parents=True,exist_ok=True)
paths=[root/'baseline/q_daoist_character_pack_4096/00_reference_topright_boy_transparent_4096.png']+[dest/f'{d}_frame_{n:02d}.png' for d in ['south','east'] for n in range(1,5)]
canvas=Image.new('RGB',(1250,810),(29,40,42)); draw=ImageDraw.Draw(canvas)
for idx,p in enumerate(paths):
 r,c=divmod(idx,5); im=Image.open(p).convert('RGBA'); im.thumbnail((235,345)); x=c*250+(250-im.width)//2;y=r*405+30;canvas.paste(im,(x,y),im);draw.text((c*250+6,r*405+380),p.stem.replace('_frame_',' ').replace('_transparent_4096',''),fill='white')
canvas.save(review/'original-south-east-review.jpg',quality=64,optimize=True)
# Full portrait reference rendered into an opaque review image for transport only.
im=Image.open(paths[0]).convert('RGBA');im.thumbnail((680,680));bg=Image.new('RGB',im.size,(50,56,60));bg.paste(im,(0,0),im);bg.save(review/'original-portrait-review.jpg',quality=82,optimize=True)
print(json.dumps({'extracted':len(records),'review':str(review/'original-south-east-review.jpg'),'south_sha':[r['sha256'] for r in records if '/south_frame_' in r['path']]}))