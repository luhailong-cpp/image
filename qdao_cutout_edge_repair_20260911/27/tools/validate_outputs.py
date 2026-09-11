"""Independent validation of staged PNG, strip, GIF, hashes and source lineage.

Does not call the processing pipeline and never marks gait/style as passed.
"""
from pathlib import Path
import argparse, hashlib, json
from datetime import datetime,timezone
import numpy as np
from PIL import Image

PACK=Path(__file__).resolve().parents[1]
DIRS=['S','SW','W','NW','N','NE','E','SE']
ROWS={'cardinal':['S','W','E','N'],'diagonal':['SW','NW','NE','SE']}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rg_sha(im):return hashlib.sha256(im.tobytes()).hexdigest()
def foot(im):
    y,x=np.nonzero(np.asarray(im.getchannel('A'))>8)
    return float(np.median(x[y>=np.percentile(y,90)])),int(y.max())

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=PACK/'staged-v2');p.add_argument('--directions',nargs='+',choices=DIRS,default=DIRS);args=p.parse_args();base=args.output_dir.resolve();dirs=args.directions;full=set(dirs)==set(DIRS)
    errors=[];files=[];frame_hashes=[];records={};process_hashes=[]
    def check(ok,message):
        if not ok:errors.append(message)
    try:
        portrait=Image.open(base/'portrait.png');check(portrait.mode=='RGBA' and portrait.size==(1024,1024),'Portrait format mismatch');files.append(base/'portrait.png')
        pr=json.loads((base/'processing/portrait.json').read_text());check(sha(Path(pr['path']))==pr['sha256'],'Portrait source changed');check(sha(base/'portrait.png')==pr['output_sha256'],'Portrait output changed');process_hashes.append(pr['processing_tool_sha256'])
        for d in dirs:
            rec=json.loads((base/'processing'/f'{d}.json').read_text());check(sha(Path(rec['path']))==rec['sha256'],f'{d}: source changed');process_hashes.append(rec['processing_tool_sha256']);images=[];details=[]
            for item in rec['outputs']:check(sha(base/item['path'])==item['sha256'],f'{d}: staged output SHA mismatch: {item["path"]}')
            for i in range(1,5):
                path=base/'walk'/d/f'{i:02}.png';im=Image.open(path);check(im.mode=='RGBA' and im.size==(512,512),f'{d}/{i}: format mismatch');im=im.convert('RGBA');images.append(im);a=np.asarray(im);box=im.getchannel('A').getbbox();anchor=foot(im)
                check(box and box[0]>0 and box[1]>0 and box[2]<512 and box[3]<512,f'{d}/{i}: alpha touches canvas')
                check(anchor[1]==471 and abs(anchor[0]-256)<=.5,f'{d}/{i}: foot anchor {anchor}')
                check(a[:,:,3].min()==0 and a[:,:,3].max()==255,f'{d}/{i}: alpha missing clear/opaque range')
                h=rg_sha(im);frame_hashes.append(h);check(h==rec['frames'][i-1]['rgba_sha256'],f'{d}/{i}: frame transform content mismatch')
                details.append({'file':path.relative_to(base).as_posix(),'sha256':sha(path),'rgba_sha256':h,'alpha_bbox':list(box),'foot_anchor':anchor});files.append(path)
            strip_path=base/'walk'/d/'strip.png';strip=Image.open(strip_path);check(strip.mode=='RGBA' and strip.size==(2048,512),f'{d}: strip format mismatch')
            for i,im in enumerate(images):check(strip.crop((i*512,0,(i+1)*512,512)).tobytes()==im.tobytes(),f'{d}: strip frame {i+1} differs from PNG')
            files.append(strip_path);gif_path=base/'walk'/d/'walk.gif';gif=Image.open(gif_path);check(gif.size==(512,512) and gif.n_frames==4,f'{d}: GIF format/frame count mismatch');dur=[]
            for i in range(gif.n_frames):gif.seek(i);dur.append(gif.info.get('duration'))
            check(dur==[120]*4,f'{d}: GIF timing {dur}');files.append(gif_path);records[d]={'frames':details,'gif_durations_ms':dur,'source_sha256':rec['sha256'],'shared_scale':rec['same_scale_all_four_frames'],'body_scale_cv':rec['body_scale_cv'],'visual_review':rec.get('visual_review','required')}
        check(len(set(frame_hashes))==len(frame_hashes),'Exact RGBA duplicate frame present')
        check(all(v==process_hashes[0] for v in process_hashes),'Mixed processing tool versions')
        toolfiles={'batch_processor':PACK/'tools/process_new_batch.py','rgb_cleanup':PACK/'repair.py','anchor_contract':PACK.parents[1]/'qdao_chibi_roster_v11/process_roster.py','gif_encoder':Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py'}
        for name,path in toolfiles.items():check(sha(path)==process_hashes[0][name],f'{name}: tool changed after processing')
        if full:
            for kind,rowdirs in ROWS.items():
                path=base/f'walk-{kind}.png';sheet=Image.open(path);check(sheet.mode=='RGBA' and sheet.size==(2048,2048),f'{kind}: table format mismatch')
                for row,d in enumerate(rowdirs):
                    for col in range(4):check(sheet.crop((col*512,row*512,(col+1)*512,(row+1)*512)).tobytes()==Image.open(base/'walk'/d/f'{col+1:02}.png').tobytes(),f'{kind}: table {d}/{col+1} differs')
                files.append(path)
            manifest=json.loads((base/'manifest.json').read_text());check(len(manifest['files'])==51,'Manifest does not contain 51 media files')
            expected={q.relative_to(base).as_posix() for q in files};listed={item['path'] for item in manifest['files']};check(expected==listed,'Manifest set differs from expected delivery')
            for item in manifest['files']:check(sha(base/item['path'])==item['sha256'],f'Manifest SHA mismatch: {item["path"]}')
    except (OSError,ValueError,KeyError,IndexError) as e:errors.append(str(e))
    report={'status':'passed_numeric_independent_validation' if not errors else 'failed','scope':'full_51_media' if full else 'partial_directions','directions_checked':dirs,'verified_media_files':len(files),'unique_rgba_frames':len(set(frame_hashes)),'errors':errors,'visual_approval':'not inferred; use explicit per-direction visual records','checked_at_utc':datetime.now(timezone.utc).isoformat(),'records':records}
    path=base/'processing'/('artifact-validation.json' if full else 'artifact-validation-partial.json');path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k!='records'}));return 0 if not errors else 2

if __name__=='__main__':raise SystemExit(main())
