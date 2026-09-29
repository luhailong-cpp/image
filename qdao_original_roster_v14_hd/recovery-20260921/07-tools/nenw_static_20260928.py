from pathlib import Path
from PIL import Image,ImageSequence
import json,hashlib,numpy as np
from datetime import datetime,timezone
here=Path(__file__).resolve().parent
src=here/'candidate/07_moon_shadow_assassin_girl'
preview=here.parent/'07-delivery-preview/all-review-20260928-3'
out=here/'nenw-static-20260928';out.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((preview/'manifest.json').read_text(encoding='utf-8-sig'));lookup={r['path']:r for r in manifest['files']}
rows=[]
for d in ['NE','NW']:
 for slot in [f'idle/{d}.png']+[f'walk/{d}/{i:02}.png' for i in range(1,17)]:
  p=src/slot;m=json.loads(Path(str(p)+'.generation.json').read_text(encoding='utf-8-sig'));im=Image.open(p).convert('RGBA');a=np.asarray(im.getchannel('A'))
  pair=Image.new('RGB',(2048,1024))
  for k,bg in enumerate([(30,38,46),(240,238,228)]):
   canvas=Image.new('RGB',(1024,1024),bg);canvas.paste(im,(0,0),im);pair.paste(canvas,(1024*k,0))
  pair.save(out/f'{d}-{p.stem}-pair.png')
  native=m.get('derivedFrom',{});raw=Path(native.get('path',''))
  rows.append({'slot':slot,'attempt':m['attempt'],'sha256':sha(p),'previewMatchesCurrent':sha(p)==lookup[slot]['sha256'],'outputMatchesRecord':sha(p)==m['outputSha256'],'sourceSha256':native.get('sha256'),'nativeSize':m.get('nativeMetrics',{}).get('size') or lookup[slot]['nativeSize'],'sourceCurrentlyPresent':raw.is_file(),'sourceCurrentHashMatches':sha(raw)==native.get('sha256') if raw.is_file() else None,'alphaRange':[int(a.min()),int(a.max())],'bottomAlphaGt8':int(np.where(a>8)[0].max()),'edgeAlphaMax':max(int(x.max()) for x in [a[0],a[-1],a[:,0],a[:,-1]]),'outputMetrics':m.get('outputMetrics',lookup[slot]['metrics'])})
gifs=[]
for d in ['NE','NW']:
 for mode in ['light','dark']:
  p=preview/'preview'/f'{d}-30ms-{mode}.gif';im=Image.open(p);dur=[f.info.get('duration') for f in ImageSequence.Iterator(im)]
  gifs.append({'path':str(p),'sha256':sha(p),'frames':len(dur),'durationMs':dur,'cycleMs':sum(dur),'pass':dur==[30]*16})
report={'scope':'07 NE and NW static review only','observedAt':datetime.now(timezone.utc).isoformat(),'previewRevision':manifest['revision'],'previewManifestSha256':sha(preview/'manifest.json'),'files':rows,'gifs':gifs,'browserPlaybackPerformed':False,'fullOfflineAcceptance':False,'clientIntegration':False,'reviewState':'in_progress','sourceRetentionNote':'Missing historical raw is not current pixel proof; do not infer native validation from absence.'}
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'out':str(out),'count':len(rows),'manifestMatch':all(r['previewMatchesCurrent'] for r in rows),'recordMatch':all(r['outputMatchesRecord'] for r in rows),'nativeCurrentlyPresent':sum(r['sourceCurrentlyPresent'] for r in rows)}))
