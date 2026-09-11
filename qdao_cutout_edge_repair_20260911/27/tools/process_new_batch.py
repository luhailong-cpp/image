"""Deterministic staging of newly generated 27 art. Never writes production.

Uses the existing project anchor/compose contract and installed sprite GIF
encoder. Raw art must already have been generated and visually accepted.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

PACK=Path(__file__).resolve().parents[1]
ROOT=PACK.parents[1]
CELL=512
FOOT=(256,471)
DIRS=['S','SW','W','NW','N','NE','E','SE']
ROWS={'cardinal':['S','W','E','N'],'diagonal':['SW','NW','NE','SE']}

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def load_module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

rp=load_module('roster_contract',ROOT/'qdao_chibi_roster_v11/process_roster.py')
sp=load_module('sprite_encoder',Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py')
edge=load_module('ink_kite_rgb_edges',PACK/'repair.py')

def tool_hashes():
    return {'batch_processor':sha(Path(__file__)), 'rgb_cleanup':sha(PACK/'repair.py'), 'anchor_contract':sha(ROOT/'qdao_chibi_roster_v11/process_roster.py'), 'gif_encoder':sha(Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py')}

def source_record(p):
    im=Image.open(p)
    return {'path':str(p.resolve()),'sha256':sha(p),'native_size':list(im.size),'native_mode':im.mode,'source':'built-in image_gen','output_size_is_not_native_resolution':True,'processing_tool_sha256':tool_hashes()}

def key_matte(image):
    """Estimate the actual key and solve edge pixels against nearby foreground.

    Alpha is created here from opaque magenta-backed raw art. The later narrow
    RGB repair preserves this derived alpha. No component erasure is used.
    """
    a=np.asarray(image.convert('RGBA')).copy();rgb=a[:,:,:3].astype('float32');h,w=a.shape[:2]
    r,g,b=rgb.transpose(2,0,1);dom=np.minimum(r,b)-g
    border=np.zeros((h,w),bool);border[:8]=True;border[-8:]=True;border[:,:8]=True;border[:,-8:]=True
    samples=rgb[border&(dom>170)&(g<80)]
    if len(samples)<max(20,int(border.sum()*.5)):
        raise ValueError('Expected flat magenta source padding; inspect source before matting')
    key=np.median(samples,axis=0)
    keydistance=np.sqrt(np.sum((rgb-key)**2,axis=2))
    field=(keydistance<=8)&(dom>170)
    strong=(dom>65)&(g<140)&(b>r*.62)
    # Enclosed key pockets between hair/kite strings can differ from the
    # outer field after generation; include their neighboring antialiasing.
    near=np.asarray(Image.fromarray(((field|strong)*255).astype('uint8')).filter(ImageFilter.MaxFilter(21)))>0
    interior=np.asarray(Image.fromarray((field*255).astype('uint8')).filter(ImageFilter.MaxFilter(5)))==0
    candidate=(dom>6)&(~field)&near&(a[:,:,3]>0)
    donors=(dom<5)&(~field)&interior&(a[:,:,3]>=240)
    coverage=np.ones((h,w),dtype='float32');coverage[field]=0
    out_rgb=rgb.copy();unresolved=[];solved=0
    for y,x in zip(*np.nonzero(candidate)):
        found=None
        for radius in (6,12,24,40):
            x0=max(0,x-radius);x1=min(w,x+radius+1);y0=max(0,y-radius);y1=min(h,y+radius+1)
            yy,xx=np.nonzero(donors[y0:y1,x0:x1]);yy+=y0;xx+=x0
            if not len(xx):continue
            colors=rgb[yy,xx];v=key-colors
            frac=np.clip(np.sum((rgb[y,x]-colors)*v,axis=1)/np.maximum(np.sum(v*v,axis=1),1),0,1)
            predicted=colors+v*frac[:,None];err=np.sum((predicted-rgb[y,x])**2,axis=1)
            dist=(xx-x)**2+(yy-y)**2;k=int(np.argmin(err+dist*3.0))
            found=(float(frac[k]),colors[k],float(np.sqrt(dist[k])));break
        if found is None and keydistance[y,x] < 60 and dom[y,x] > 170:
            # Key field compression/noise far from every opaque foreground.
            # Never apply this to a strand with an available local donor.
            coverage[y,x]=0
            continue
        if found is None:
            # Record this for review; only a neutral-edge analytic estimate is
            # possible when an isolated strand has no local opaque foreground.
            t=float(np.clip(dom[y,x]/max(1,min(key[0],key[2])-key[1]),0,1))
            unresolved.append([int(x),int(y)])
        else:t=found[0];solved+=1
        cov=1-t
        if found is not None and cov<.07 and found[2]>6 and keydistance[y,x]<45:
            # Near-key compression flecks remote from true foreground can
            # borrow a distant boot/hair donor; they are field, not an edge.
            cov=0
        if cov<.015:cov=0
        if cov>.985:cov=1
        coverage[y,x]=cov
        if cov>0:out_rgb[y,x]=np.clip((rgb[y,x]-t*key)/max(1-t,1e-5),0,255)
    out=np.dstack([np.round(out_rgb),np.round(coverage*a[:,:,3])]).clip(0,255).astype('uint8');out[out[:,:,3]==0,:3]=0
    matte=Image.fromarray(out,'RGBA')
    fixed,stats=edge.clean(matte, extra_mask=candidate)
    assert np.array_equal(np.asarray(matte)[:,:,3],np.asarray(fixed)[:,:,3])
    return fixed, {'key_rgb':key.tolist(),'exact_field_pixels':int(field.sum()),'mixture_solved_pixels':solved,'mixture_unresolved':len(unresolved),'mixture_unresolved_coordinates':unresolved,'post_matte_rgb_cleanup':stats,'note':'Alpha derives from new opaque key-backed raw art. Subsequent edge correction preserves this alpha exactly.'}

def save_png(im,p):
    p.parent.mkdir(parents=True,exist_ok=True);im.save(p,optimize=True)

def preview(images,labels,out):
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    page=Image.new('RGB',(1280,350*len(images)),'#ebe5d7');draw=ImageDraw.Draw(page)
    for row,(im,label) in enumerate(zip(images,labels)):
        for col,bg in enumerate(['#f0ecdf','#162c26']):
            tile=Image.new('RGBA',(640,320),bg);thumb=im.copy();thumb.thumbnail((630,310),Image.Resampling.LANCZOS);tile.alpha_composite(thumb,((640-thumb.width)//2,(320-thumb.height)//2));page.paste(tile.convert('RGB'),(col*640,row*350+30))
            draw.text((col*640+8,row*350+6),label,fill='#183b30',font=font)
    out.parent.mkdir(parents=True,exist_ok=True);page.save(out,quality=96,subsampling=0)

def process_portrait(sources,out):
    p=sources/'portrait_raw.png';rec=source_record(p);im=Image.open(p).convert('RGBA')
    clean,stats=key_matte(im);save_png(clean,out/'processing/portrait-keyed-native.png')
    # Keep the source canvas and body proportions. Uniform letterboxing only.
    clean.thumbnail((1024,1024),Image.Resampling.LANCZOS)
    result=Image.new('RGBA',(1024,1024),(0,0,0,0));result.paste(clean,((1024-clean.width)//2,(1024-clean.height)//2))
    bbox=result.getchannel('A').getbbox()
    if not bbox or min(bbox)<1 or bbox[2]>=1024 or bbox[3]>=1024:raise ValueError('Portrait missing safe canvas padding')
    save_png(result,out/'portrait.png');assert sha(p)==rec['sha256']
    rec.update(matte=stats,output_sha256=sha(out/'portrait.png'),source_canvas_preserved_by_isotropic_fit=True,visual_review='required')
    write(out/'processing/portrait.json',rec);preview([result],['portrait: new raw, keyed only'],out/'processing/portrait-review.jpg')
    return rec

def process_direction(direction,sources,out):
    p=sources/f'walk_{direction}_2x2.png';rec=source_record(p);raw=Image.open(p).convert('RGBA')
    if raw.width<500 or raw.height<500:raise ValueError(f'{direction}: source resolution unexpectedly small')
    clean,stats=key_matte(raw);save_png(clean,out/'processing'/f'{direction}-keyed-native.png')
    xs=[0,raw.width//2,raw.width];ys=[0,raw.height//2,raw.height];frames=[];boxes=[];heights=[]
    for row in range(2):
        for col in range(2):
            box=(xs[col],ys[row],xs[col+1],ys[row+1]);cell=clean.crop(box);bbox=cell.getchannel('A').getbbox();visible=rp.bounds(cell)
            if not bbox or not visible:raise ValueError(f'{direction}: missing body in cell {row*2+col+1}')
            if bbox[0]<2 or bbox[1]<2 or bbox[2]>cell.width-2 or bbox[3]>cell.height-2:raise ValueError(f'{direction}: cell {row*2+col+1} touches a cut line; regenerate or manually review layout')
            comps=sp.connected_components(cell,min_area=500)
            if len(comps)!=1:raise ValueError(f'{direction}: cell {row*2+col+1} has {len(comps)} large components; review whole silhouette')
            frames.append(cell);boxes.append(list(box));heights.append(visible[3]-visible[1])
    cv=float(np.std(heights)/np.mean(heights))
    if cv>.08:raise ValueError(f'{direction}: raw height CV {cv:.4f}>.08; regenerate inconsistent scale')
    scale=420/max(heights);pairs=[rp.normalized_frame(f,scale) for f in frames];final=[p[0] for p in pairs];transforms=[p[1] for p in pairs]
    hashes=[hashlib.sha256(im.tobytes()).hexdigest() for im in final]
    if len(set(hashes))!=4:raise ValueError(f'{direction}: exact duplicate poses; cannot synthesize missing phases')
    d=out/'walk'/direction
    for i,im in enumerate(final,1):save_png(im,d/f'{i:02}.png')
    save_png(rp.compose(final,4),d/'strip.png');sp.save_transparent_gif(final,d/'walk.gif',120)
    gif=Image.open(d/'walk.gif')
    if gif.n_frames!=4:raise ValueError(f'{direction}: GIF merged poses unexpectedly')
    for i in range(4):
        gif.seek(i)
        if gif.info.get('duration')!=120:raise ValueError('GIF frame duration mismatch')
    assert sha(p)==rec['sha256']
    rec.update(matte=stats,layout='2x2 TL,TR,BL,BR',source_boxes=boxes,native_subject_heights=heights,same_scale_all_four_frames=scale,body_scale_cv=cv,frames=transforms,visual_review='required: side/contact/pass/opposite-contact/opposite-pass, identity and direction; unique hashes are not motion evidence')
    rec['outputs']=[{'path':q.relative_to(out).as_posix(),'sha256':sha(q)} for q in sorted(d.iterdir()) if q.suffix in ['.png','.gif']]
    write(out/'processing'/f'{direction}.json',rec)
    preview(final,[f'{direction} {i}' for i in range(1,5)],out/'processing'/f'{direction}-review.jpg')
    return rec

def assemble(sources,out):
    records={};all_images={};errors=[]
    for d in DIRS:
        rec=json.loads((out/'processing'/f'{d}.json').read_text(encoding='utf-8'));records[d]=rec
        if rec.get('processing_tool_sha256')!=tool_hashes():raise ValueError(f'{d}: processing tool version changed; rebuild this direction')
        if sha(sources/f'walk_{d}_2x2.png')!=rec['sha256']:raise ValueError(f'{d}: new source changed after processing')
        for artifact in rec['outputs']:
            if sha(out/artifact['path'])!=artifact['sha256']:raise ValueError(f'{d}: processed output changed; rebuild direction')
        all_images[d]=[Image.open(out/'walk'/d/f'{i:02}.png').convert('RGBA') for i in range(1,5)]
    prec=json.loads((out/'processing/portrait.json').read_text(encoding='utf-8'))
    if prec.get('processing_tool_sha256')!=tool_hashes():raise ValueError('Portrait processing tool version changed; rebuild portrait')
    if sha(sources/'portrait_raw.png')!=prec['sha256'] or sha(out/'portrait.png')!=prec['output_sha256']:raise ValueError('Portrait source/output changed after processing')
    for kind,dirs in ROWS.items():save_png(rp.compose([im for d in dirs for im in all_images[d]],4),out/f'walk-{kind}.png')
    meanheights=[float(np.mean([r['bbox_alpha_gt_8'][3]-r['bbox_alpha_gt_8'][1] for r in records[d]['frames']])) for d in DIRS]
    ratio=max(meanheights)/min(meanheights)
    if ratio>1.10:errors.append(f'Cross-direction mean-height ratio {ratio:.4f}>1.10')
    framehashes=[hashlib.sha256(im.tobytes()).hexdigest() for d in DIRS for im in all_images[d]]
    if len(set(framehashes))!=32:errors.append('Exact duplicates across directions')
    qc={'status':'failed' if errors else 'passed_numeric_qc_pending_visual_review','errors':errors,'visual_review':{'status':'required','checks':['portrait proportions and mature identity','eight viewing directions','four semantically distinct ordered gait phases per direction','no purple edge, lost hair/string or matte hole','light/dark composites at native scale']},'artifact_validation':{'portrait':'1024x1024 RGBA','independent_walk_frames':32,'unique_frame_hashes':len(set(framehashes)),'frame_size':[512,512],'directions':8,'strips':'2048x512 RGBA','gifs':8,'gif_frames_each':4,'duration_ms':120,'all_feet_y':471},'directions':{d:{'body_scale_cv':records[d]['body_scale_cv'],'shared_scale':records[d]['same_scale_all_four_frames'],'frames':records[d]['frames']} for d in DIRS},'cross_direction_mean_height_ratio':ratio}
    write(out/'qc.json',qc)
    profile={'strategy':'one isotropic scale shared by four original poses per direction; translation to common feet only','target_max_subject_height':420,'cell_size':[512,512],'output_foot_px':list(FOOT),'mirrored_frames':False,'synthetic_or_repeated_frames':False,'scale_by_direction':{d:records[d]['same_scale_all_four_frames'] for d in DIRS},'source_sha_by_direction':{d:records[d]['sha256'] for d in DIRS}}
    write(out/'processing/scale-profile.json',profile);write(out/'processing/frame-transforms.json',{d:records[d]['frames'] for d in DIRS});write(out/'processing/sources.json',{'portrait':prec,**records})
    artifacts=[out/'portrait.png',out/'walk-cardinal.png',out/'walk-diagonal.png']+[p for d in DIRS for p in sorted((out/'walk'/d).iterdir()) if p.suffix in ['.png','.gif']]
    assert len(artifacts)==51
    manifest={'version':3,'character_id':'27_ink_kite_ranger','generated_at_utc':datetime.now(timezone.utc).isoformat(),'status':qc['status'],'art_source':'built-in image_gen','portrait':'portrait.png','portrait_size':[1024,1024],'walk':{'directions':DIRS,'frames_per_direction':4,'cell':[512,512],'strip_size':[2048,512],'frame_duration_ms':120,'fps':1000/120,'feet_px_from_top_left':list(FOOT),'row_order_cardinal':ROWS['cardinal'],'row_order_diagonal':ROWS['diagonal'],'frame_pattern':'walk/{direction}/{01,02,03,04}.png','strip_pattern':'walk/{direction}/strip.png','gif_pattern':'walk/{direction}/walk.gif'},'qc':'qc.json','client_integration':'not performed','sources':{'portrait':prec,**records},'processing':'processing/scale-profile.json','source_resolution_note':'Native generated source sizes are recorded per input. Output dimensions describe deterministic resampled exports, not native art detail.','files':[{'path':p.relative_to(out).as_posix(),'sha256':sha(p),'bytes':p.stat().st_size} for p in artifacts]}
    write(out/'manifest.json',manifest)
    if errors:raise ValueError('; '.join(errors))
    return {'files':51,'status':qc['status'],'output_dir':str(out)}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('command',choices=['portrait','direction','build','assemble']);p.add_argument('direction',nargs='?',choices=DIRS);p.add_argument('--source-dir',type=Path,default=PACK/'sources');p.add_argument('--output-dir',type=Path,default=PACK/'production-staged')
    args=p.parse_args();sources=args.source_dir.resolve();out=args.output_dir.resolve()
    # This helper is deliberately unable to overwrite any formal roster path.
    if not out.is_relative_to(PACK) or out==PACK or out.is_relative_to(sources):p.error('Output must be a dedicated folder inside this repair batch and outside its sources')
    out.mkdir(parents=True,exist_ok=True)
    try:
        if args.command=='portrait':result=process_portrait(sources,out)
        elif args.command=='direction':
            if args.direction is None:p.error('direction command requires S/SW/W/NW/N/NE/E/SE')
            result=process_direction(args.direction,sources,out)
        elif args.command=='assemble':result=assemble(sources,out)
        else:
            required=[sources/'portrait_raw.png']+[sources/f'walk_{d}_2x2.png' for d in DIRS]
            missing=[str(q) for q in required if not q.is_file()]
            if missing:raise FileNotFoundError('Missing final sources: '+', '.join(missing))
            process_portrait(sources,out)
            for d in DIRS:process_direction(d,sources,out)
            result=assemble(sources,out)
        print(json.dumps({'status':'staged_needs_visual_review','command':args.command,'direction':args.direction,'output':str(out)},ensure_ascii=False));return 0
    except (ValueError,OSError) as e:
        write(out/'processing/last-failure.json',{'command':args.command,'direction':args.direction,'error':str(e),'utc':datetime.now(timezone.utc).isoformat()});print(str(e),file=sys.stderr);return 2

if __name__=='__main__':raise SystemExit(main())
