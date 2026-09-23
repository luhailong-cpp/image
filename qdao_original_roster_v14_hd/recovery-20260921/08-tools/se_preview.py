"""Pin the selected SE-only sources and generate review composites, never other directions."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, json, shutil
from PIL import Image, ImageDraw
from process import read, write, sha, RECOVERY, OUT

HERE = Path(__file__).resolve().parent
DELIVERY = RECOVERY / '08-delivery-preview'
selection = read(DELIVERY / 'SE-selection.json')
parser = argparse.ArgumentParser(); parser.add_argument('--revision', default='SE-review-v1'); args = parser.parse_args()
assert args.revision.startswith('SE-review-') and '/' not in args.revision and '\\' not in args.revision
dest = DELIVERY / args.revision
if dest.exists():
    raise ValueError('Preserve existing snapshot')
dest.mkdir()
files, images = [], []
for i in range(1, 17):
    slot = f'walk/SE/{i:02d}'; attempt = selection[slot]; source = OUT / attempt
    row = read(source / 'source.json'); p = dest / f'{i:02d}.png'
    assert row['slot'] == slot and sha(source / 'frame.png') == row['output_sha256']
    shutil.copy2(source / 'frame.png', p); im = Image.open(p).convert('RGBA'); images.append(im)
    files.append({'slot': slot, 'path': p.name, 'sha256': sha(p), 'attempt': attempt, 'raw': row['raw'], 'anchor': row['anchor_px'], 'bbox': row['bbox_px'], 'source_record': str(source / 'source.json'), 'source_record_sha256': sha(source / 'source.json')})
assert len(set(r['raw']['sha256'] for r in files)) == 16
previews = []
for theme, color in [('light', (240,238,228)), ('dark', (30,38,46))]:
    sheet = Image.new('RGB', (2048,2176), color); draw = ImageDraw.Draw(sheet); frames = []
    seam = Image.new('RGB', (2048,544), color); sd = ImageDraw.Draw(seam)
    feet = Image.new('RGB', (2048,1200), color); fd = ImageDraw.Draw(feet)
    for i, im in enumerate(images):
        small = im.resize((512,512), Image.Resampling.LANCZOS); view = Image.new('RGB', (512,512), color);view.paste(small,(0,0),small);frames.append(view)
        x,y=(i%4)*512,(i//4)*544;sheet.paste(view,(x,y+32));draw.text((x+12,y+8),f'SE {i+1:02d}',fill='white' if theme=='dark' else 'black')
        crop=im.crop((256,724,768,1024));base=Image.new('RGB',(512,300),color);base.paste(crop,(0,0),crop);feet.paste(base,((i%4)*512,(i//4)*300));fd.text(((i%4)*512+8,(i//4)*300+8),f'{i+1:02d}',fill='white' if theme=='dark' else 'black')
    for j,i in enumerate([14,15,0,1]):seam.paste(frames[i],(j*512,32));sd.text((j*512+12,8),f'SE {i+1:02d}',fill='white' if theme=='dark' else 'black')
    for name,im in [('contact',sheet),('seam',seam),('feet',feet)]:
        p=dest/f'{name}-{theme}.png';im.save(p);previews.append({'path':p.name,'sha256':sha(p),'operation':'review_composite_only'})
    p=dest/f'SE-30ms-{theme}.gif';frames[0].save(p,save_all=True,append_images=frames[1:],duration=[30]*16,loop=0,optimize=False,disposal=2)
    with Image.open(p) as gif:
        durations=[]
        for i in range(gif.n_frames):gif.seek(i);durations.append(gif.info['duration'])
    assert durations==[30]*16
    previews.append({'path':p.name,'sha256':sha(p),'frames':16,'duration_ms':durations,'cycle_ms':480})
manifest={'character_id':'08_alchemy_prodigy_boy','revision':args.revision,'createdAt':datetime.now(timezone.utc).isoformat(),'directions':['SE'],'files':files,'actual_walk':16,'actual_idle':0,'missing':[],'scope':'SE walk only; not full-character inventory','visual_approval':False,'browser_review_performed':False,'previews':previews,'selection_sha256':sha(DELIVERY/'SE-selection.json'),'script_sha256':sha(__file__)}
write(dest/'manifest.json',manifest)
html=(HERE/'preview.html').read_text(encoding='utf-8').replace('__MANIFEST__',json.dumps(manifest,ensure_ascii=False).replace('</','<\\/'))
html=html.replace("direction='S'","direction='SE'").replace('${M.actual_walk}/128 行走，${M.actual_idle}/8 独立站立。','${M.actual_walk}/16 东南方向行走；本页只检查SE。').replace('无缺槽','SE行走无缺槽；不代表全角色齐套')
(dest/'index.html').write_text(html,encoding='utf-8')
print(json.dumps({'path':str(dest),'selected_frames':len(files),'GIFs':2,'duration_ms':30,'cycle_ms':480},ensure_ascii=False))
