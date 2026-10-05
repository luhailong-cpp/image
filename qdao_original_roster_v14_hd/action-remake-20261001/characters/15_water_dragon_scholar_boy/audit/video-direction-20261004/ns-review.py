from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
from datetime import datetime,timezone
B=Path(r'D:/work/image/qdao_original_roster_v14_hd/action-remake-20261001/characters/15_water_dragon_scholar_boy');A=B/'audit/video-direction-20261004'
jobs=json.loads((A/'ns-jobs.json').read_text(encoding='utf-8'))
def bbox(im,box):
 a=im.getchannel('A').point(lambda v:255 if v>8 else 0);q=a.crop(box).getbbox()
 return None if q is None else [q[0]+box[0],q[1]+box[1],q[2]+box[0],q[3]+box[1]]
rows=[]; comparisons=Image.new('RGB',(1536,1664),(230,232,230));dc=ImageDraw.Draw(comparisons)
def rt(p):
 im=Image.open(p).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda v:0 if v<=8 else v))
 out=Image.new('RGBA',(1024,1024));out.alpha_composite(im.resize((940,940),Image.Resampling.LANCZOS),(42,49));return out
for i,j in enumerate(jobs):
 old=Image.open(j['target']).convert('RGBA');p=B/'sources/new'/f"{j['key']}.png";new=Image.open(p).convert('RGBA')
 assert old.size==new.size==(1254,1254)
 roi=(480,1010,675,1240) if j['supportFoot']=='left' else (620,970,820,1240)
 oldbb=bbox(old,roi);newbb=bbox(new,roi)
 gen=f"provenance/generation/{j['key']}.json";g=json.loads((B/gen).read_text(encoding='utf-8'));assert (B/g['evidence']['toolResult']).exists()
 assert g['references'][0]['sha256']==hashlib.sha256(Path(j['target']).read_bytes()).hexdigest()
 assert g['actualModel'] is None and g['actualQuality'] is None
 row={'slot':j['slot'],'candidateKey':j['key'],'file':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'generationRecord':gen,'sourceTarget':j['target'],'sourceTargetSha256':g['references'][0]['sha256'],'supportFoot':j['supportFoot'],'nativeCanvas':[1254,1254],'export':{'scaleCanvasTo':940,'offset':[42,49],'canvas':1024},'staticReviewed':True,'dynamicReviewed':False,'localMeasurement':{'roi':roi,'oldVisibleFootBBox':oldbb,'newVisibleFootBBox':newbb,'bottomDeltaNativePx':newbb[3]-oldbb[3]},'staticFinding':'只修支撑足踝下鞋掌；外侧鞋头已收回北向，足别与另一抬起腿保留。固定全画布导出待主线程执行。'}
 rows.append(row)
 for k,path in enumerate([j['target'],str(p)]):
  col=(i%2)*2+k;y=(i//2)*416;x=col*384;im=rt(path).resize((384,384),Image.Resampling.LANCZOS)
  comparisons.paste(im,(x,y+28),im);dc.text((x+5,y+5),j['slot']+(' OLD' if k==0 else ' AXIS'),fill='black')
comparisons.save(A/'ns-before-after-full.png')
selection={'updatedAt':datetime.now(timezone.utc).isoformat(),'rows':rows,'staticReviewed':True,'dynamicReviewed':False,'runtimeWritten':False,'route':'builtin image_gen.imagegen','configuredModel':'gpt-image-2.5-sunburst','configuredQuality':'max','actualModel':None,'actualQuality':None}
(A/'ns-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2),encoding='utf-8')
m=json.loads((B/'manifest.json').read_text(encoding='utf-8'))
board=Image.new('RGB',(1536,1664),(230,232,230));dc=ImageDraw.Draw(board);sequence=[]
for f in range(1,17):
 slot=f'run-N-{f:02}';row=next((x for x in rows if x['slot']==slot),None)
 if row:p=Path(row['file'])
 else:
  q=next(x for x in m['frames'] if x['slot']==slot);p=B/q['source']
  if not p.exists():
   g=json.loads((B/q['derivedFrom']['generationRecord']).read_text(encoding='utf-8'));p=Path(g['evidence']['hostOutput'])
  assert hashlib.sha256(p.read_bytes()).hexdigest()==q['derivedFrom']['sha256']
 out=rt(p);sequence.append(out.resize((512,512),Image.Resampling.LANCZOS));im=out.resize((384,384),Image.Resampling.LANCZOS)
 x=(f-1)%4*384;y=(f-1)//4*416;board.paste(im,(x,y+28),im);dc.text((x+5,y+5),slot+(' AXIS' if row else ' retained'),fill='black')
board.save(A/'ns-N-final-contact.png')
sequence[0].save(A/'ns-N-axis-1200ms.apng',save_all=True,append_images=sequence[1:],duration=75,loop=0,disposal=2,blend=0)
print(json.dumps([{'slot':r['slot'],'bottomDelta':r['localMeasurement']['bottomDeltaNativePx']} for r in rows]))

