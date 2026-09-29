"""Build source-bound E/SE offline review assets and file-contract evidence only."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image, ImageDraw
import numpy as np

R=Path(__file__).resolve().parents[1]
O=R/'15-review/east-previews';O.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[];gifs=[]
for d in ('E','SE'):
    paths=[R/'15-delivery-preview/runtime/walk'/d/f'{n:02d}.png' for n in range(1,17)]
    idle=R/'15-delivery-preview/runtime/idle'/f'{d}.png'
    for p in [*paths,idle]:
        s=json.loads(p.with_name(p.name+'.generation.json').read_text(encoding='utf8'))
        raw=Path(s['derivedFrom']['path']);record=json.loads(Path(s['derivedFrom']['generationRecord']).read_text(encoding='utf8'))
        im=Image.open(p);a=np.asarray(im)[:,:,3]
        assert im.size==(1024,1024) and im.mode=='RGBA'
        assert sha(p)==s['sha256'] and sha(raw)==s['derivedFrom']['sha256']==record['sha256']
        assert min(Image.open(raw).size)>=1024
        assert not max(a[0].max(),a[-1].max(),a[:,0].max(),a[:,-1].max())
        y,x=np.where(a>8);assert int(y.max())==942
        rows.append({'slot':s['slot'],'file':str(p),'sha256':sha(p),'source':str(raw),'sourceSha256':sha(raw),'nativeSize':list(Image.open(raw).size),'finalSize':list(im.size),'mode':im.mode,'borderVisiblePixels':int(np.count_nonzero(a[0])+np.count_nonzero(a[-1])+np.count_nonzero(a[:,0])+np.count_nonzero(a[:,-1])),'effectiveFootY':int(y.max()),'recordedAnchor':s['operation']['anchorAfterPx'],'nativeScale':s['operation']['wholeCellScale'],'poseModification':s['operation']['poseModification'],'upscaled':s['operation']['upscaled'],'actualModel':s['actualModel'],'actualQuality':s['actualQuality']})
    for name,bg in [('light',(242,235,214)),('dark',(26,40,48))]:
        sheet=Image.new('RGB',(1024,1128),bg);feet=Image.new('RGB',(1920,1120),bg);seam=Image.new('RGB',(1024,282),bg)
        seq=[];full=[]
        for n,p in enumerate(paths,1):
            im=Image.open(p).convert('RGBA');canvas=Image.new('RGBA',(1024,1024),(*bg,255));canvas.alpha_composite(im)
            canvas=canvas.convert('RGB');full.append(canvas);small=canvas.resize((256,256),Image.Resampling.LANCZOS)
            x=((n-1)%4)*256;y=((n-1)//4)*282;sheet.paste(small,(x,y));ImageDraw.Draw(sheet).text((x+6,y+260),f'{d}{n:02}',fill=(80,150,180))
            x=((n-1)%4)*480;y=((n-1)//4)*280;feet.paste(canvas.crop((300,690,780,970)),(x,y));ImageDraw.Draw(feet).text((x+6,y+5),f'{d}{n:02}',fill=(80,150,180))
            seq.append(canvas.resize((512,512),Image.Resampling.LANCZOS))
        for col,n in enumerate([15,16,1,2]):
            seam.paste(full[n-1].resize((256,256),Image.Resampling.LANCZOS),(col*256,0));ImageDraw.Draw(seam).text((col*256+6,260),f'{d}{n:02}',fill=(80,150,180))
        sheet.save(O/f'{d}-current-{name}.png');feet.save(O/f'{d}-feet-{name}.png');seam.save(O/f'{d}-seam-{name}.png')
        # A 1:1 inspection sheet retains original pixels over entire character bounds.
        for start in range(1,17,4):
            page=Image.new('RGB',(2048,2048),bg)
            for k in range(4):
                page.paste(full[start+k-1],((k%2)*1024,(k//2)*1024))
                ImageDraw.Draw(page).text(((k%2)*1024+8,(k//2)*1024+8),f'{d}{start+k:02} 1:1',fill=(80,150,180))
            page.save(O/f'{d}-{start:02}-{start+3:02}-{name}-large.png')
        gif=O/f'{d}-{name}-30ms.gif';seq[0].save(gif,save_all=True,append_images=seq[1:],duration=30,loop=0,disposal=2)
        test=Image.open(gif);dur=[]
        for i in range(test.n_frames):test.seek(i);dur.append(test.info['duration'])
        assert dur==[30]*16 and test.info['loop']==0
        gifs.append({'file':str(gif),'sha256':sha(gif),'direction':d,'background':name,'frameDurationsMs':dur,'cycleMs':sum(dur),'loop':0,'sourceSha256':[sha(p) for p in paths],'visualPlayback':'not_verified_by_script'})
        im=Image.open(idle).convert('RGBA');canvas=Image.new('RGBA',(1024,1024),(*bg,255));canvas.alpha_composite(im);canvas.convert('RGB').save(O/f'{d}-idle-{name}.png')
assert len({r['sha256'] for r in rows})==34 and len({r['sourceSha256'] for r in rows})==34
(O/'file-contract.json').write_text(json.dumps({'checkedAt':datetime.now(timezone.utc).isoformat(),'frames':rows,'gifTiming':gifs,'artPass':'requires_actual_viewing_and_separate_record'},indent=2),encoding='utf8')
print('E/SE 34 file contracts and four 16x30ms GIFs passed; visual acceptance separate')

