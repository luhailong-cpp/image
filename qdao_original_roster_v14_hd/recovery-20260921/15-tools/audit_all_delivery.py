"""Read all 136 selected assets and their true source chains. No runtime writes."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageSequence

R = Path(__file__).resolve().parents[1]
P = R/'15-delivery-preview'
O = R/'15-review/global-final'; O.mkdir(exist_ok=True)
DIRECTIONS = ['N','NE','E','SE','S','SW','W','NW']
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
rows = []; gifs = []; panels = []
for d in DIRECTIONS:
    walk = [P/'runtime/walk'/d/f'{n:02d}.png' for n in range(1,17)]
    idle = P/'runtime/idle'/f'{d}.png'
    for p in [*walk,idle]:
        s = json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf8'))
        raw = Path(s['derivedFrom']['path'])
        record_path = Path(s['derivedFrom']['generationRecord'])
        g = json.loads(record_path.read_text(encoding='utf8'))
        req, receipt, prompt = raw.parent/'request.json', raw.parent/'receipt.json', raw.parent/g['prompt']['path']
        im = Image.open(p); native = Image.open(raw); ar = np.array(im)
        yy,xx = np.where(ar[:,:,3]>8); top = int(yy.min()); height = int(yy.max())-top
        ax = float(np.median(xx[yy<top+max(1,int(height*.42))])); ay = int(yy.max())
        ident = g['archiveIdentity']; request = json.loads(req.read_text(encoding='utf8'))
        submitted_prompt = request.get('prompt',request.get('arguments',{}).get('prompt'))
        checks = {
            'selectedSha':sha(p)==s['sha256'], 'sourceSha':sha(raw)==s['derivedFrom']['sha256']==g['sha256'],
            'requestSha':sha(req)==ident['requestSha256'], 'receiptSha':sha(receipt)==ident['receiptSha256'],
            'promptSha':sha(prompt)==ident['promptSha256'], 'precisePromptMatchesRequest':prompt.read_text(encoding='utf8')==submitted_prompt,
            'nativeAtLeast1024':min(native.size)>=1024, 'final1024RGBA':im.size==(1024,1024) and im.mode=='RGBA',
            'footY942':ay==942, 'anchorX512Within1':abs(ax-512)<=1,
            'transparentBorder':not np.any(np.concatenate([ar[0,:,3],ar[-1,:,3],ar[:,0,3],ar[:,-1,3]])),
            'realAlpha':ar[:,:,3].min()==0 and ar[:,:,3].max()==255,
            'nativeDownsample':s['operation']['wholeCellScale']<1 and s['operation']['upscaled']==False,
            'noPoseModification':s['operation']['poseModification']==False,
            'modelUnknownHonest':s['actualModel'] is None and s['actualQuality'] is None,
        }
        checks = {k:bool(v) for k,v in checks.items()}
        rows.append({'slot':s['slot'],'direction':d,'kind':'idle' if p==idle else 'walk','path':str(p),'sha256':sha(p),
                     'source':str(raw),'sourceSha256':sha(raw),'sourceRecord':str(record_path),'sourceRecordSha256':sha(record_path),
                     'requestSha256':sha(req),'receiptSha256':sha(receipt),'promptSha256':sha(prompt),
                     'nativeSize':list(native.size),'finalSize':list(im.size),'anchor':[ax,ay],'selectedBatch':raw.parent.name,
                     'actualModel':s['actualModel'],'actualQuality':s['actualQuality'],'checks':checks,'failedChecks':[k for k,v in checks.items() if not v]})
    for bg,color in [('light',(242,235,214)),('dark',(26,40,48))]:
        path = P/'derived'/f'{d}-walk-30ms-{bg}.gif'
        with Image.open(path) as gif:
            durations = [fr.info.get('duration') for fr in ImageSequence.Iterator(gif)]
            loop = gif.info.get('loop')
        gifs.append({'path':str(path),'sha256':sha(path),'direction':d,'background':bg,'durations':durations,'cycleMs':sum(durations),'loop':loop,'pass':durations==[30]*16 and loop==0})
        if d in ['N','NE']:
            full = []
            for p in [*walk,idle]:
                im = Image.open(p).convert('RGBA'); canvas = Image.new('RGBA',im.size,(*color,255)); canvas.alpha_composite(im)
                full.append(canvas.convert('RGB'))
            for start in range(0,16,4):
                page = Image.new('RGB',(2048,2048),color)
                for k in range(4): page.paste(full[start+k],(k%2*1024,k//2*1024))
                dest = O/f'{d}-{start+1:02d}-{start+4:02d}-{bg}-1024.png'; page.save(dest)
                panels.append({'path':str(dest),'sha256':sha(dest),'sourceHashes':[sha(p) for p in walk[start:start+4]],'scale':1})
            full[-1].save(O/f'{d}-idle-{bg}-1024.png')
sources = [r['sourceSha256'] for r in rows]; outputs = [r['sha256'] for r in rows]
report = {'generatedAt':datetime.now(timezone.utc).isoformat(),'character':'15_water_dragon_scholar_boy','walkCount':sum(r['kind']=='walk' for r in rows),
          'idleCount':sum(r['kind']=='idle' for r in rows),'sourceUniqueCount':len(set(sources)),'outputUniqueCount':len(set(outputs)),
          'allMachineChecksPass':len(rows)==136 and len(set(sources))==136 and len(set(outputs))==136 and all(not r['failedChecks'] for r in rows),
          'allGifTimingPass':all(g['pass'] for g in gifs),'machineChecksAreNotArtAcceptance':True,'dynamicPlaybackObserved':False,'clientValidation':'not_performed',
          'frames':rows,'gifs':gifs,'panels':panels}
(R/'15-review/role15-source-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in report.items() if k not in ['frames','gifs','panels']},ensure_ascii=False))
print([(r['slot'],r['failedChecks']) for r in rows if r['failedChecks']])
