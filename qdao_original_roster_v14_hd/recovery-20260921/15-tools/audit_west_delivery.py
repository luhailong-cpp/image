"""Source-bound W/NW offline inspection assets and machine checks; no runtime edits."""
from pathlib import Path
import hashlib, json
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageSequence

R=Path(__file__).resolve().parents[1]
OUT=R/'15-review/W-NW-final'; OUT.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]; outputs=[]
for d in ('W','NW'):
    views={bg:[] for bg in ('light','dark')}
    for n in [*range(1,17),'idle']:
        name=f'{d}{n:02d}' if isinstance(n,int) else f'{d}-idle'
        p=R/'15-delivery-preview/runtime'/(f'walk/{d}/{n:02d}.png' if isinstance(n,int) else f'idle/{d}.png')
        side=p.with_name(p.name+'.generation.json'); s=json.loads(side.read_text(encoding='utf-8'))
        raw=Path(s['derivedFrom']['path']); g=json.loads(Path(s['derivedFrom']['generationRecord']).read_text(encoding='utf-8'))
        req=raw.parent/'request.json'; receipt=raw.parent/'receipt.json'; prompt=raw.parent/g['prompt']['path']
        im=Image.open(p).convert('RGBA'); ar=np.array(im); yy,xx=np.where(ar[:,:,3]>8)
        top=int(yy.min()); height=int(yy.max())-top; ax=float(np.median(xx[yy<top+max(1,int(height*.42))])); ay=int(yy.max())
        rawim=Image.open(raw); identities=g['archiveIdentity']
        checks={
            'outputSha':sha(p)==s['sha256'], 'rawSha':sha(raw)==s['derivedFrom']['sha256']==g['sha256'],
            'requestSha':sha(req)==identities['requestSha256'], 'receiptSha':sha(receipt)==identities['receiptSha256'],
            'promptSha':sha(prompt)==identities['promptSha256'],
            'promptMatchesRequest':prompt.read_text(encoding='utf-8')==json.loads(req.read_text(encoding='utf-8'))['prompt'],
            'nativeAtLeast1024':min(rawim.size)>=1024, 'output1024Rgba':Image.open(p).mode=='RGBA' and im.size==(1024,1024),
            'anchor942':ay==942, 'anchorXWithinOnePixel':abs(ax-512)<=1,
            'transparentBorder':not np.any(np.concatenate([ar[0,:,3],ar[-1,:,3],ar[:,0,3],ar[:,-1,3]])>0),
            'hasTransparency':ar[:,:,3].min()==0 and ar[:,:,3].max()==255,
            'noUpscale':s['operation']['wholeCellScale']<1 and s['operation']['upscaled']==False,
            'noPoseModification':s['operation']['poseModification']==False,
        }
        checks={k:bool(v) for k,v in checks.items()}
        row={'name':name,'slot':s['slot'],'outputSha256':sha(p),'source':str(raw),'sourceSha256':sha(raw),'nativeSize':list(rawim.size),'anchorMeasured':[ax,ay], 'wholeCellScale':s['operation']['wholeCellScale'],'manualMultiplier':s['operation'].get('manualMultiplier',1), 'checks':checks,'failedChecks':[k for k,v in checks.items() if not v]}
        rows.append(row)
        for bg,color in [('light',(240,234,220,255)),('dark',(24,34,44,255))]:
            c=Image.new('RGBA',im.size,color);c.alpha_composite(im);c=c.convert('RGB')
            dest=OUT/f'{name}-{bg}-1024.png';c.save(dest)
            outputs.append({'path':str(dest),'sha256':sha(dest),'sourceOutputSha256':row['outputSha256']})
            if isinstance(n,int): views[bg].append(c.resize((256,256),Image.Resampling.LANCZOS))
    for bg,images in views.items():
        dest=OUT/f'{d}-{bg}-30ms.gif'
        images[0].save(dest,save_all=True,append_images=images[1:],duration=30,loop=0,optimize=False,disposal=2)
        gif=Image.open(dest);durations=[fr.info.get('duration') for fr in ImageSequence.Iterator(gif)]
        outputs.append({'path':str(dest),'sha256':sha(dest),'frameCount':len(durations),'durationsMs':durations,'cycleMs':sum(durations),'timingPass':durations==[30]*16,'sourceOutputSha256':[r['outputSha256'] for r in rows if r['name'].startswith(d) and not r['name'].endswith('idle')][-16:]})

sources=[r['sourceSha256'] for r in rows]; finals=[r['outputSha256'] for r in rows]
report={'generatedAt':datetime.now(timezone.utc).isoformat(),'character':'15_water_dragon_scholar_boy','scope':['W','NW'],'walkCount':32,'idleCount':2,'sourceUnique':len(set(sources))==34,'outputUnique':len(set(finals))==34,'allMachineChecksPass':all(not r['failedChecks'] for r in rows),'machineChecksDoNotEstablishArtAcceptance':True,'dynamicPlaybackObserved':False,'clientValidation':'not_performed','frames':rows,'reviewArtifacts':outputs}
(R/'15-review/W-NW-source-bound-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ('frames','reviewArtifacts')},ensure_ascii=False))
print([(r['name'],r['failedChecks']) for r in rows if r['failedChecks']])
