import pathlib,json,hashlib,datetime,sys
from PIL import Image,ImageDraw,ImageFont
sys.stdout.reconfigure(encoding='utf-8')
OUT=pathlib.Path(__file__).resolve().parent;BASE=OUT.parents[1]
CID='17_ghost_script_calligrapher_boy';ROOT=BASE/'characters'/CID
MANIFEST=ROOT/'manifest.json';OLD=BASE/'review-all-actions-20261004/group-c/source-evidence.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
data=json.loads(MANIFEST.read_text(encoding='utf-8-sig'))
old=json.loads(OLD.read_text(encoding='utf-8-sig'))
lookup={(r['action'],r['direction'],r['frame']):r for r in old['frames'] if r['character']==CID}
report={'atUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'manifestPath':str(MANIFEST),'manifestSha256':sha(MANIFEST),'priorQaEvidencePath':str(OLD),'frames':[],'groups':[]}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
for g in data['sequences']:
 fs=[]
 for f in g['frames']:
  p=ROOT/f['file'];a=g['action'];d=g['direction'];n=f['frame'];actual=sha(p);prev=lookup.get((a,d,n))
  item={'action':a,'direction':d,'frame':n,'path':str(p),'sha256':actual,'manifestSha256':f['sha256'],'manifestMatch':actual==f['sha256'],'priorQaSha256':prev['sha256'] if prev else None,'priorQaMatch':bool(prev and actual==prev['sha256']),'mtimeNs':p.stat().st_mtime_ns}
  report['frames'].append(item);fs.append(item)
 changed=[f for f in fs if not f['priorQaMatch']]
 if changed:
  im=Image.new('RGB',(4*256,64+284*((len(fs)+3)//4)),(244,239,224));draw=ImageDraw.Draw(im)
  draw.text((8,8),CID+' '+a+'/'+d+' CURRENT',(20,25,25),font=font)
  for k,f in enumerate(fs):
   x=k%4*256;y=64+k//4*284;src=Image.open(f['path']).convert('RGBA').resize((256,256),Image.Resampling.LANCZOS);im.paste(src,(x,y),src);draw.text((x+5,y+258),f'{d}{f["frame"]:02}',(20,25,25),font=font)
  sheet=OUT/(a+'-'+d+'-current-full.jpg');im.save(sheet,quality=95)
 else: sheet=BASE/'review-all-actions-20261004/group-c'/CID/(g['action']+'-'+g['direction']+'-full.png')
 report['groups'].append({'action':g['action'],'direction':g['direction'],'count':len(fs),'changedFromPriorQa':[f['frame'] for f in changed],'sheetPath':str(sheet)})
(OUT/'snapshot.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'frames':len(report['frames']),'manifestMismatches':sum(not f['manifestMatch'] for f in report['frames']),'changedQa':{g['action']+'/'+g['direction']:g['changedFromPriorQa'] for g in report['groups'] if g['changedFromPriorQa']}},ensure_ascii=False))
