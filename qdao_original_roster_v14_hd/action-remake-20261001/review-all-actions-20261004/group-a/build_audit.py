import pathlib,json,hashlib,re,datetime,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
BASE=pathlib.Path(__file__).resolve().parents[2]
OUT=pathlib.Path(__file__).resolve().parent
IDS=['00_reference_topright_boy','01_ice_sword_girl','02_fire_talisman_boy','03_lotus_healer_girl','04_mountain_guardian_boy']
FONT=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',19)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
snapshot={'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'purpose':'independent read-only current export visual audit; sheets are QA derivatives','characters':{}}
for cid in IDS:
 root=BASE/'characters'/cid
 fn={'02_fire_talisman_boy':'inventory.json','03_lotus_healer_girl':'review/all-actions-selection.json','04_mountain_guardian_boy':'manifest.delivery.json'}.get(cid,'manifest.json')
 mp=root/fn;d=json.loads(mp.read_text(encoding='utf-8-sig'))
 if 'sequences' in d:
  rows=[dict(f,action=g['action'],direction=g['direction']) for g in d['sequences'] for f in g['frames']]
 elif 'groups' in d:
  rows=[dict(f,action=g['action'],direction=g['direction']) for g in d['groups'] for f in g['frames']]
 else: rows=d.get('frames',d.get('files',[]))
 groups={}; missing=[]; mismatches=[];frames=[]
 for row in rows:
  rel=row.get('path',row.get('file'));p=root/rel
  a=row.get('action');direction=row.get('direction')
  if a is None:
   _,a,direction,stem=pathlib.PurePosixPath(rel).parts
  n=row.get('frame',int(re.findall(r'\d+',p.stem)[-1]))
  info={'action':a,'direction':direction,'frame':n,'path':str(p),'expectedSha256':row.get('sha256')}
  if not p.exists(): missing.append(info);continue
  info.update(sha256=sha(p),mtimeNs=p.stat().st_mtime_ns)
  info['manifestMatch']=info['expectedSha256'] in (None,info['sha256'])
  if not info['manifestMatch']: mismatches.append(info)
  frames.append(info);groups.setdefault((a,direction),[]).append(info)
 for group,fs in groups.items():fs.sort(key=lambda r:r['frame'])
 dest=OUT/cid;dest.mkdir(parents=True,exist_ok=True)
 sheets=[]
 for a,dirs in [('run',['N','NE','E','SE','S','SW','W','NW']),('hit',['E','W']),('attack',['E','W']),('cast',['E','W'])]:
  for start in range(0,len(dirs),2):
   use=dirs[start:start+2]; width=256*8;h=64+4*284
   im=Image.new('RGB',(width,h),(244,239,224));draw=ImageDraw.Draw(im)
   draw.text((8,8),cid+' '+a+' '+','.join(use)+' CURRENT EXPORTS',(20,25,25),font=FONT)
   for j,direction in enumerate(use):
    fs=groups.get((a,direction),[])
    for k,info in enumerate(fs):
     x=j*1024+(k%4)*256;y=64+(k//4)*284
     src=Image.open(info['path']).convert('RGBA');src=src.resize((256,256),Image.Resampling.LANCZOS)
     im.paste(src,(x,y),src);draw.text((x+4,y+259),f'{direction}{info["frame"]:02}',(20,25,25),font=FONT)
   path=dest/(a+'-'+'-'.join(use)+'.jpg');im.save(path,quality=94);sheets.append({'path':str(path),'groups':[a+'/'+dd for dd in use]})
 snapshot['characters'][cid]={'manifest':str(mp),'manifestSha256':sha(mp),'frames':frames,'missing':missing,'mismatches':mismatches,'sheets':sheets,'groupCounts':{'/'.join(k):len(v) for k,v in groups.items()}}
(OUT/'snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({cid:{'frames':len(v['frames']),'missing':len(v['missing']),'mismatches':len(v['mismatches']),'sheets':len(v['sheets'])} for cid,v in snapshot['characters'].items()},ensure_ascii=False))
