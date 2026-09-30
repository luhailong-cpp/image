"""Read-only checks of selected character 20 files and their generation evidence."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json
import numpy as np
from PIL import Image

R = Path(__file__).resolve().parent.parent
CHAR = '20_star_formation_master_girl'
P = R/'20-final' if (R/'20-final/walk').exists() else R/'20-work/export-v1'/CHAR
O = P/'preview' if P.name == '20-final' else R/'20-delivery-preview'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))

def audit(directions, require_raw=True):
    rows, gifs = [], []
    processing = read(P/'processing/frame-sources.json')
    for d in directions:
        for slot in [f'walk/{d}/{n:02d}.png' for n in range(1,17)] + [f'idle/{d}.png']:
            p = P/slot
            m = read(Path(str(p)+'.generation.json'))
            source = Path(m['derivedFrom']['path'])
            gen_path = Path(m['derivedFrom']['generationRecord'])
            gen = read(gen_path)
            receipt = read(gen_path.parent/'generation-receipt.json')
            assert sha(p) == m['sha256'] == processing[slot]['output_sha256'], slot
            assert m['derivedFrom']['sha256'] == gen['sha256'] == receipt['raw_sha256'], slot
            if require_raw:
                assert source.exists() and sha(source) == gen['sha256'], slot
                with Image.open(source) as raw:
                    assert list(raw.size) == [gen['width'],gen['height']], slot
            assert min(gen['width'],gen['height']) >= 1024, slot
            assert processing[slot]['source']['grid'] == [1,1], slot
            assert sha(gen_path.parent/'prompt.txt') == gen['prompt']['sha256'], slot
            assert receipt['paid_api_calls'] == 0, slot
            with Image.open(p) as im:
                assert im.size == (1024,1024) and im.mode == 'RGBA', slot
                a = np.asarray(im.getchannel('A')); yy,xx = np.where(a>8)
                assert yy.max() == 942 and a.min() == 0, slot
                assert not any(np.any(e>8) for e in [a[0,:],a[-1,:],a[:,0],a[:,-1]]), slot
                rows.append({'slot':slot,'sha256':sha(p),'size':[1024,1024],'mode':'RGBA',
                    'alphaLowestY':int(yy.max()),'alphaBoundingBox':[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
                    'nativeSourceSha256':gen['sha256'],'nativeSize':[gen['width'],gen['height']],
                    'sourceAttempt':source.parent.name,'generationRecord':str(gen_path.relative_to(R)).replace('\\','/'),
                    'sourceSingleFrameFlagAsRecorded':gen.get('nativeSingleFrameConfirmed'),
                    'actualModel':gen.get('actualModel'),'actualQuality':gen.get('actualQuality')})
        for mode in ['dark','light']:
            p = O/f'{d}-30ms-{mode}.gif'
            with Image.open(p) as im:
                durations=[]
                for n in range(im.n_frames):
                    im.seek(n);durations.append(im.info['duration'])
                assert im.n_frames == 16 and durations == [30]*16, p.name
            gifs.append({'file':p.name,'sha256':sha(p),'frames':16,'frameMs':30,'cycleMs':480})
    assert len({r['sha256'] for r in rows}) == len(rows)
    assert len({r['nativeSourceSha256'] for r in rows}) == len(rows)
    return {'at':datetime.now(timezone.utc).isoformat(),'rows':rows,'gifs':gifs,'count':len(rows),
        'uniqueFiles':len(rows),'uniqueNativeSources':len(rows),'allPass':True,'rawFilesChecked':require_raw,
        'manifestSha256':sha(O/'manifest.json')}

if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--directions',default='N,NE,E,SE,S,SW,W,NW')
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--after-retention',action='store_true')
    args=ap.parse_args();result=audit(args.directions.split(','),not args.after_retention)
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:result[k] for k in ['count','uniqueFiles','uniqueNativeSources','allPass','rawFilesChecked']}))
