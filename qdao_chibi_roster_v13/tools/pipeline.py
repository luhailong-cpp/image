"""Deterministic V13 assembly; generation of source art is deliberately external."""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, shutil, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT.parent / 'qdao_chibi_roster_v12/candidate-stable-body/24_lu_dongbin'
OUT = ROOT / 'candidate/24_lu_dongbin'
BASE_SHA = '3dbc699023fd7fe6f45304fd91ecea2f088e107d4c727d375dc1b23c31e68c68'
DIRS = ('N','NE','E','SE','S','SW','W','NW')
SPRITE_PROCESSOR = Path('C:/Users/luyua/.agents/skills/generate2dsprite/scripts/generate2dsprite.py')

def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def rgba_sha(im): return hashlib.sha256(im.tobytes()).hexdigest()
def now(): return datetime.now(timezone.utc).isoformat()
def read(path): return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def write(path, data):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def relative(path): return Path(path).resolve().relative_to(OUT.resolve()).as_posix()
def root_relative(path): return Path(path).resolve().relative_to(ROOT.resolve()).as_posix()
def module(path, name):
    spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
def image(path):
    with Image.open(path) as im: return im.convert('RGBA')
def save(im,path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); im.save(path)
def bbox(im,threshold=8):
    yy,xx=np.nonzero(np.asarray(im)[:,:,3]>threshold)
    return None if not len(xx) else [int(xx.min()),int(yy.min()),int(xx.max())+1,int(yy.max())+1]
def head(im,roi):
    yy,xx=np.nonzero(np.asarray(im)[:,:,3]>8)
    if not len(xx): raise ValueError('Empty source cell')
    top=int(yy.min()); return [float(np.median(xx[yy<top+roi])),top]
def body_scale(im):
    # Same V12 proxy: sqrt(nonzero alpha in central 50% / full cell area).
    a=np.asarray(im)[:,:,3]; half=max(1,round(im.width*.5/2)); mid=im.width//2
    return math.sqrt(float(np.count_nonzero(a[:,max(0,mid-half):min(im.width,mid+half)]))/(im.width*im.height))
def frozen():
    if sha(BASE/'manifest.json')!=BASE_SHA: raise ValueError('Approved V12 manifest changed')
    return read(BASE/'manifest.json')
def copy_exact(src,dst):
    dst=Path(dst); dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists() and sha(dst)!=sha(src): raise ValueError(f'Refusing to overwrite frozen copy: {dst}')
    if not dst.exists(): shutil.copy2(src,dst)
    if sha(dst)!=sha(src): raise ValueError(f'Copy failed: {dst}')
def export_paths():
    return ['portrait.png',*[f'idle/{d}.png' for d in DIRS],*[f'walk/{d}/{i:02d}.png' for d in DIRS for i in range(1,17)],*[f'walk/{d}/strip.png' for d in DIRS]]

def init():
    m=frozen(); records=[]
    for name in ('manifest.json','qc.json','validation.json','processing/frame-transforms.json'):
        copy_exact(BASE/name,OUT/'source/v12-frozen'/name)
    for name in ['portrait.png',*[f'idle/{d}.png' for d in DIRS]]:
        copy_exact(BASE/name,OUT/name)
        records.append({'output':name,'source':str(BASE/name),'sha256':sha(BASE/name),'kind':'frozen_v12'})
    for d in DIRS:
        idle_source=m['alignment']['direction_references'][d]['idle_input_path']
        copy_exact(BASE/idle_source,OUT/idle_source)
        for i in range(1,9):
            name=f'walk/{d}/{2*i-1:02d}.png'; src=BASE/f'walk/{d}/{i:02d}.png'
            copy_exact(src,OUT/name)
            records.append({'output':name,'source':str(src),'sha256':sha(src),'kind':'frozen_v12','v12_frame':i,'v13_frame':2*i-1})
        for half,start in [('first-half',1),('second-half',5)]:
            dest=ROOT/'references'/d/half; dest.mkdir(parents=True,exist_ok=True)
            for role in ('A','B','idle'):
                sheet=Image.new('RGBA',(1024,1024),(255,0,255,255))
                cells=[]
                for n in range(4):
                    i=start+n
                    source=BASE/f'idle/{d}.png' if role=='idle' else BASE/f'walk/{d}/{(i if role=="A" else i%8+1):02d}.png'
                    im=image(source); sheet.alpha_composite(im,((n%2)*512,(n//2)*512))
                    cells.append({'row':n//2,'col':n%2,'v13_even_frame':i*2,'source':str(source),'source_sha256':sha(source)})
                save(sheet,dest/f'{role}.png'); write(dest/f'{role}.json',{'role':role,'no_subject_resize':True,'cells':cells,'sha256':sha(dest/f'{role}.png')})
    vendor=ROOT/'tools/vendor'; vendor.mkdir(parents=True,exist_ok=True)
    copy_exact(SPRITE_PROCESSOR,vendor/'generate2dsprite.py')
    copy_exact(ROOT.parent/'qdao_chibi_roster_v12/edge_despill.py',vendor/'edge_despill.py')
    write(OUT/'source/v12-frozen/preservation.json',{'manifest_sha256':BASE_SHA,'baseline':str(BASE),'records':records,'count':len(records)})
    write(ROOT/'tools/vendor/implementations.json',{'generate2dsprite.py':sha(vendor/'generate2dsprite.py'),'edge_despill.py':sha(vendor/'edge_despill.py')})
    print(json.dumps({'frozen_files':len(records),'reference_sheets':48,'root':str(ROOT)}))

def import_batch(batch_path):
    m=frozen(); config=read(batch_path); bid=config['batch_id']
    if not bid or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_' for c in bid): raise ValueError('Invalid batch_id')
    generation=config['generation']
    if generation.get('tool')!='built-in image_gen': raise ValueError('New poses must have built-in image_gen provenance')
    if 'model_verified' not in generation or not generation.get('model_evidence'): raise ValueError('Record actual model evidence')
    src=Path(config['source']); prompt=Path(config['prompt'])
    if not prompt.is_file() or not prompt.read_text(encoding='utf-8-sig').strip(): raise ValueError('Exact source prompt required')
    work=OUT/'processing/batches'/bid; work.mkdir(parents=True,exist_ok=True)
    saved_src=OUT/'source/generated'/bid/'raw.png'; saved_prompt=saved_src.with_name('prompt.txt')
    copy_exact(src,saved_src); copy_exact(prompt,saved_prompt)
    copy_exact(batch_path,work/'batch-input.json')
    raw=image(saved_src); rows=int(config['grid']['rows']); cols=int(config['grid']['cols'])
    if min(rows,cols)<1 or rows==1 and cols>1: raise ValueError('Use a multi-row source grid')
    cw=raw.width/cols; ch=raw.height/rows; factor=512/max(cw,ch)
    keyer=module(ROOT/'tools/vendor/generate2dsprite.py','frozen_chroma')
    cleaner=module(ROOT/'tools/vendor/edge_despill.py','frozen_despill')
    records=read(OUT/'processing/even-frame-sources.json') if (OUT/'processing/even-frame-sources.json').exists() else {}
    targets=[(c['direction'],int(c['frame'])) for c in config['cells']]
    source_slots=[(int(c['row']),int(c['col'])) for c in config['cells']]
    if len(set(targets))!=len(targets) or len(set(source_slots))!=len(source_slots):
        raise ValueError('Each selected transition must have a distinct destination and a distinct source cell')
    selected=[]
    for item in config['cells']:
        d=item['direction']; frame=int(item['frame']); r=int(item['row']); c=int(item['col'])
        if d not in DIRS or frame not in range(2,17,2) or not 0<=r<rows or not 0<=c<cols: raise ValueError('Invalid direction/frame/cell')
        if not item.get('selection_reason'): raise ValueError('Visual selection reason required')
        box=[round(c*cw),round(r*ch),round((c+1)*cw),round((r+1)*ch)]
        cell=raw.crop(box); key=keyer.remove_bg_magenta(cell.copy(),100,150)
        if bbox(key,0) is None: raise ValueError(f'Empty keyed source: {d}/{frame}')
        source_alpha=np.asarray(key)[:,:,3]
        if any(np.any(e) for e in (source_alpha[0],source_alpha[-1],source_alpha[:,0],source_alpha[:,-1])):
            raise ValueError(f'Original source cell touches its border: {d}/{frame}; regenerate art, never hide a clipped source through translation')
        size=[round(cell.width*factor),round(cell.height*factor)]
        normalized=key.resize(size,Image.Resampling.LANCZOS) if key.size!=tuple(size) else key.copy()
        radius=int(config.get('despill_radius',4)); clean,stats=cleaner.despill(normalized,radius=radius,reference_radius=radius*3)
        ref=m['alignment']['direction_references'][d]; ax,ay=head(clean,ref['roi_height_px'])
        tx,ty=ref['target_head_px']; dx=round(tx-ax); dy=int(ty-ay)
        bb=bbox(clean,0); moved=[bb[0]+dx,bb[1]+dy,bb[2]+dx,bb[3]+dy]
        if min(moved[:2])<1 or max(moved[2:])>511: raise ValueError(f'Frame would touch/crop output edge: {d}/{frame} {moved}; regenerate art')
        final=Image.new('RGBA',(512,512)); final.paste(clean,(dx,dy))
        paths={}
        for stage,im in [('cell',cell),('keyed',key),('normalized',normalized),('cleaned',clean),('final',final)]:
            p=work/d/f'{frame:02d}-{stage}.png'; save(im,p); paths[stage]={'path':relative(p),'sha256':sha(p),'rgba_sha256':rgba_sha(im)}
        output=OUT/f'walk/{d}/{frame:02d}.png'
        record={'kind':'generated_transition','direction':d,'frame':frame,'between_v12_frames':[frame//2,frame//2%8+1],
            'batch_id':bid,'source':{'path':relative(saved_src),'sha256':sha(saved_src),'native_size':list(raw.size),'cell_xyxy':box,'grid':{'rows':rows,'cols':cols,'row':r,'col':c}},
            'prompt':{'path':relative(saved_prompt),'sha256':sha(saved_prompt)},'generation':generation,'selection_reason':item['selection_reason'],
            'whole_cell_normalization':{'scale':factor,'source_cell_size':list(cell.size),'normalized_size':size,'resample':'LANCZOS','bbox_fit':False,'common_scale':1.0},
            'chroma_key':{'threshold':100,'edge_threshold':150,'implementation_sha256':sha(ROOT/'tools/vendor/generate2dsprite.py')},
            'source_cell_qc':{'edge_touch_alpha_gt_0':False,'body_scale':body_scale(key),'body_scale_definition':'sqrt(nonzero_alpha_in_central_50_percent_width / full_cell_area)'},
            'edge_despill':{'radius_px':radius,'reference_radius_px':radius*3,'implementation_sha256':sha(ROOT/'tools/vendor/edge_despill.py'),'stats':stats},
            'alignment_version':3,'reference':ref,'head_anchor_before_px':[ax,ay],'head_anchor_after_px':head(final,ref['roi_height_px']),
            'translation_px':[dx,dy],'stages':paths,'output':relative(output),'output_sha256':paths['final']['sha256'],'output_rgba_sha256':rgba_sha(final),'recorded_at_utc':now()}
        records[f'{d}/{frame:02d}']=record; selected.append(record)
    # Commit only after every selected cell passes; a failed batch keeps evidence without replacing candidate frames.
    for rec in selected:
        destination=OUT/rec['output']; destination.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(OUT/rec['stages']['final']['path'],destination)
    write(work/'selected.json',selected); write(OUT/'processing/even-frame-sources.json',records)
    print(json.dumps({'imported':len(selected),'batch':bid,'selected_even_count':len(records)}))

def numeric_qc():
    m=frozen(); result={'version':13,'checked_at_utc':now(),'status':'pending','visual_review':'pending','errors':[],'directions':{},
      'gates':{'body_scale_cv_max':.08,'cross_direction_mean_height_ratio_max':1.10,'idle_walk_height_drift_max':.08,'head_axis_deviation_max_px':.5,'head_top_deviation_max_px':0,'unique_frames_per_direction':16}}
    means=[]
    for d in DIRS:
        paths=[OUT/f'walk/{d}/{i:02d}.png' for i in range(1,17)]; missing=[str(p.relative_to(OUT)) for p in paths if not p.exists()]
        if missing: result['directions'][d]={'status':'incomplete','missing':missing}; continue
        frames=[image(p) for p in paths]; idle=image(OUT/f'idle/{d}.png'); ref=m['alignment']['direction_references'][d]
        heights=[bbox(im)[3]-bbox(im)[1] for im in frames]; mean=float(np.mean(heights)); means.append(mean)
        scales=[body_scale(im) for im in frames]; scale_mean=float(np.mean(scales)); cv=float(np.std(scales)/scale_mean)
        height_cv=float(np.std(heights)/mean); ih=bbox(idle)[3]-bbox(idle)[1]; drift=abs(ih/mean-1)
        anchors=[head(im,ref['roi_height_px']) for im in [idle,*frames]]; axis=max(abs(a[0]-256) for a in anchors); top=max(abs(a[1]-ref['target_head_px'][1]) for a in anchors)
        unique=len(set(rgba_sha(im) for im in frames)); errors=[]
        if cv>.08: errors.append('body_scale_cv')
        if drift>.08: errors.append('idle_walk_height_drift')
        if axis>.5 or top!=0: errors.append('head_anchor')
        if unique!=16: errors.append('duplicate_frame')
        if rgba_sha(idle) in [rgba_sha(im) for im in frames]: errors.append('idle_duplicate')
        for i,im in enumerate(frames,1):
            a=np.asarray(im)[:,:,3]
            if any(np.any(e) for e in (a[0],a[-1],a[:,0],a[:,-1])): errors.append(f'edge_touch_{i}')
        result['directions'][d]={'status':'failed' if errors else 'passed_numeric','frame_count':16,'unique_frames':unique,'output_subject_heights':heights,'output_subject_height_mean':mean,'body_height_cv_record_only':height_cv,'body_scale_samples':scales,'body_scale_mean':scale_mean,'body_scale_cv':cv,'body_scale_definition':'sqrt(nonzero_alpha_in_central_50_percent_width / full_cell_area), measured on uniformly aligned output cells','idle_walk_height_drift':drift,'head_anchors':anchors,'head_axis_deviation_max_px':axis,'head_top_deviation_max_px':top,'errors':errors}
        result['errors'].extend(f'{d}: {e}' for e in errors)
    ratio=max(means)/min(means) if means else None; result['cross_direction_mean_height_ratio']=ratio
    if ratio and ratio>1.1: result['errors'].append('cross_direction_height_ratio')
    result['status']='failed' if result['errors'] else ('passed_numeric_qc_pending_visual_review' if len(means)==8 else 'incomplete')
    return result

def assemble():
    m=frozen(); frozen_records=read(OUT/'source/v12-frozen/preservation.json'); records=read(OUT/'processing/even-frame-sources.json') if (OUT/'processing/even-frame-sources.json').exists() else {}
    for d in DIRS:
        paths=[OUT/f'walk/{d}/{i:02d}.png' for i in range(1,17)]
        if not all(p.exists() for p in paths): continue
        frames=[image(p) for p in paths]; strip=Image.new('RGBA',(8192,512))
        for i,im in enumerate(frames): strip.paste(im,(i*512,0))
        save(strip,OUT/f'walk/{d}/strip.png')
        # Review-only layout: 1 idle plus 16 genuine exported poses.
        sheet=Image.new('RGB',(5*512,4*552),(38,44,45)); draw=ImageDraw.Draw(sheet)
        for i,im in enumerate([image(OUT/f'idle/{d}.png'),*frames]):
            x=(i%5)*512; y=(i//5)*552; sheet.paste(im,(x,y),im); draw.text((x+12,y+516),f'{d} / '+('idle' if i==0 else f'{i:02d} '+('V12' if i%2 else 'new')),fill='white')
        save(sheet,OUT/f'review/{d}-idle-and-16.png')
    qc=numeric_qc(); write(OUT/'qc.json',qc)
    files=[{'path':p,'sha256':sha(OUT/p),'bytes':(OUT/p).stat().st_size} for p in export_paths() if (OUT/p).exists()]
    manifest={'version':13,'character_id':'24_lu_dongbin','generated_at_utc':now(),'status':qc['status'],'art_source':'built-in image_gen for even frames; frozen approved V12 for odd frames',
      'baseline':{'path':str(BASE),'manifest_sha256':BASE_SHA,'preservation_path':'source/v12-frozen/preservation.json'},
      'alignment':{**m['alignment'],'common_scale':1.0,'transforms_path':'processing/even-frame-sources.json','transforms_sha256':sha(OUT/'processing/even-frame-sources.json') if records else None},
      'portrait':'portrait.png','portrait_size':[1024,1024],'portrait_mode':'frozen_v12','idle':{'dedicated_neutral_pose':True,'directions':list(DIRS)},
      'walk':{'directions':list(DIRS),'frames_per_direction':16,'frame_duration_ms':30,'cycle_duration_ms':480,'cell_size':[512,512],'strip_size':[8192,512],'contact_frame':0,'expected_new_generated_frames':64},
      'source_records':{'frozen_count':len(frozen_records['records']),'selected_generated_count':len(records)},'files':files}
    write(OUT/'manifest.json',manifest)
    print(json.dumps({'status':qc['status'],'delivery_pngs':len(files),'generated_frames':len(records),'errors':qc['errors']},ensure_ascii=False))

def preview():
    template=ROOT/'tools/preview-template.html'; target=ROOT/'index.html'; shutil.copy2(template,target)
    write(ROOT/'preview-status.json',{'updated_at_utc':now(),'directions':{d:all((OUT/f'walk/{d}/{i:02d}.png').exists() for i in range(1,17)) for d in DIRS}})
    print(str(target))

def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['init','import','assemble','preview']); p.add_argument('--batch'); a=p.parse_args()
    if a.command=='init': init()
    elif a.command=='import':
        if not a.batch: p.error('--batch is required')
        import_batch(a.batch)
    elif a.command=='assemble': assemble()
    else: preview()
if __name__=='__main__': main()
