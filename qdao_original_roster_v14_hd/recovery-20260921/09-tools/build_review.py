"""Build an immutable, offline-only review snapshot from actual selected 09 PNGs."""
import argparse, hashlib, json, shutil, statistics
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
from PIL import Image, ImageDraw, ImageOps
from common import DELIVERY, DIRS, CHARACTER, sha

def digest(im):
    return hashlib.sha256(im.tobytes()).hexdigest()

def selected_root(d):
    base=DELIVERY/'work'/d
    return base/'variants/native' if d=='S' else base

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--name', required=True); a=ap.parse_args()
    assert a.name.replace('-','').isalnum()
    out=DELIVERY/'revisions'/a.name; assert not out.exists(), 'Snapshot exists; choose a new name'
    records=[]; missing=[]; images={}; pixel_keys={}; mirror_keys={}; reconstruction=[]
    for d in DIRS:
        base=selected_root(d)
        for kind,frame in [('idle',None)]+[('walk',i) for i in range(1,17)]:
            key=f'idle/{d}.png' if kind=='idle' else f'walk/{d}/{frame:02d}.png'
            path=base/'runtime'/key; recpath=base/'sources'/(key+'.json')
            if not path.is_file() or not recpath.is_file(): missing.append(key); continue
            rec=json.loads(recpath.read_text(encoding='utf-8'))
            assert sha(path)==rec['outputSha256']
            raw=Path(rec['source']['path']); assert sha(raw)==rec['source']['sha256']
            image=Image.open(path).convert('RGBA'); assert image.size==(1024,1024)
            pixels=np.asarray(image); assert pixels[:,:,3].min()==0
            assert max(pixels[0,:,3].max(),pixels[-1,:,3].max(),pixels[:,0,3].max(),pixels[:,-1,3].max())==0
            op=rec['operation']; rebuilt=None
            if not op.get('chromaKey') and not op.get('despill'):
                native=Image.open(raw).convert('RGBA'); assert min(native.size)>=1024
                size=tuple(round(v*1024/max(native.size)*.88) for v in native.size)
                normalized=native.resize(size,Image.Resampling.LANCZOS)
                aa=np.asarray(normalized)[:,:,3]; yy,xx=np.where(aa>8)
                top=int(yy.min()); height=int(yy.max())-top
                axis=float(np.median(xx[yy<top+max(1,int(height*.42))]))
                offset=(round(512-axis),942-int(yy.max()))
                rebuilt=Image.new('RGBA',(1024,1024)); rebuilt.paste(normalized,offset)
                assert rebuilt.tobytes()==image.tobytes(), 'Independent reconstruction differs: '+key
            reconstruction.append({'key':key,'status':'passed' if rebuilt else 'unsupported_processing','sourceSha256':sha(raw),'outputSha256':sha(path)})
            target=out/'runtime'/key; target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,target)
            sidecar=path.with_name(path.name+'.generation.json'); shutil.copy2(sidecar,target.with_name(target.name+'.generation.json'))
            destrec=out/'sources'/(key+'.json'); destrec.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(recpath,destrec)
            records.append({'key':key,'path':'runtime/'+key,'sha256':sha(path),'sourcePath':str(raw),'sourceSha256':sha(raw),'sourceRecord':'sources/'+key+'.json','nativeSize':rec['nativeSize'],'originalSelectedPath':str(path)})
            images[key]=image; pixel_keys[key]=digest(image); mirror_keys[key]=digest(ImageOps.mirror(image))
    assert records, 'No selected frames'
    exact=[(a,b) for i,a in enumerate(pixel_keys) for b in list(pixel_keys)[i+1:] if pixel_keys[a]==pixel_keys[b]]
    mirrored=[(a,b) for i,a in enumerate(pixel_keys) for b in list(pixel_keys)[i+1:] if pixel_keys[a]==mirror_keys[b]]
    raw_sha=[r['sourceSha256'] for r in records]
    assert not exact and not mirrored and len(raw_sha)==len(set(raw_sha)), 'Duplicate or mirror/source reuse found'
    colors={'dark':(26,36,40,255),'light':(239,236,224,255)}
    preview=out/'preview'; preview.mkdir(exist_ok=True)
    gif_records=[]; stats={}
    for d in DIRS:
        keys=[f'walk/{d}/{i:02d}.png' for i in range(1,17)]
        complete=all(k in images for k in keys)
        heights=[]
        for key in keys:
            if key in images:
                aa=np.asarray(images[key])[:,:,3]; yy,xx=np.where(aa>8); heights.append(int(yy.max()-yy.min()+1))
        stats[d]={'walk':len(heights),'idle':f'idle/{d}.png' in images,'heightMin':min(heights) if heights else None,'heightMax':max(heights) if heights else None,'heightMean':statistics.mean(heights) if heights else None}
        for name,color in colors.items():
            sheet=Image.new('RGB',(1024,1120),color[:3]); draw=ImageDraw.Draw(sheet)
            frames=[]
            for idx,key in enumerate(keys):
                x=(idx%4)*256; y=(idx//4)*280
                if key in images:
                    tile=Image.new('RGBA',(1024,1024),color); tile.alpha_composite(images[key]); tile=tile.convert('RGB')
                    sheet.paste(tile.resize((256,256),Image.Resampling.LANCZOS),(x,y))
                    frames.append(tile.resize((512,512),Image.Resampling.LANCZOS))
                draw.text((x+8,y+260),f'{d} {idx+1:02d}'+(' MISSING' if key not in images else ''),fill='white' if name=='dark' else 'black')
            sheet.save(preview/f'{d}-{name}-contact.png')
            if complete:
                gif=preview/f'{d}-{name}-30ms.gif'
                frames[0].save(gif,save_all=True,append_images=frames[1:],duration=[30]*16,loop=0,disposal=2,optimize=False)
                check=Image.open(gif); durations=[]
                for i in range(check.n_frames): check.seek(i); durations.append(check.info['duration'])
                assert len(durations)==16 and durations==[30]*16
                gif_records.append({'path':gif.relative_to(out).as_posix(),'sha256':sha(gif),'frames':16,'durationsMs':durations,'cycleMs':sum(durations)})
                seam=Image.new('RGB',(2048,544),color[:3]); sd=ImageDraw.Draw(seam)
                for x,idx in enumerate([15,16,1,2]):
                    im=Image.new('RGBA',(1024,1024),color); im.alpha_composite(images[f'walk/{d}/{idx:02d}.png'])
                    seam.paste(im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(x*512,0)); sd.text((x*512+20,518),f'{d} {idx:02d}',fill='white' if name=='dark' else 'black')
                seam.save(preview/f'{d}-{name}-seam.png')
    for name,color in colors.items():
        sheet=Image.new('RGB',(2048,1088),color[:3]); draw=ImageDraw.Draw(sheet)
        for i,d in enumerate(DIRS):
            key=f'idle/{d}.png'; x=(i%4)*512; y=(i//4)*544
            if key in images:
                b=Image.new('RGBA',(1024,1024),color);b.alpha_composite(images[key]);sheet.paste(b.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(x,y))
            draw.text((x+16,y+518),d+(' MISSING' if key not in images else ''),fill='white' if name=='dark' else 'black')
        sheet.save(preview/f'idle-{name}.png')
    manifest={'character':CHARACTER,'createdAt':datetime.now(timezone.utc).isoformat(),'walkCount':sum('/' in k and k.startswith('walk/') for k in images),'idleCount':sum(k.startswith('idle/') for k in images),'frameSize':[1024,1024],'frameDurationMs':30,'cycleMs':480,'files':records,'missing':missing,'directions':stats,'gifs':gif_records,'numericChecks':{'exactDuplicatePairs':exact,'horizontalMirrorPairs':mirrored,'uniqueSourceCount':len(set(raw_sha)),'independentReconstruction':reconstruction},'visualReview':'pending','formalApproval':False,'unityValidation':'not_performed','clientValidation':'not_performed'}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    template=(Path(__file__).parent/'review_template.html').read_text(encoding='utf-8')
    (out/'index.html').write_text(template.replace('__MANIFEST__',json.dumps(manifest,ensure_ascii=False)),encoding='utf-8')
    print(json.dumps({'snapshot':str(out),'walk':manifest['walkCount'],'idle':manifest['idleCount'],'missing':len(missing),'manifestSha256':sha(out/'manifest.json'),'visualReview':'pending'},ensure_ascii=False))

if __name__=='__main__': main()
