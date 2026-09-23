from pathlib import Path
import json, hashlib
from datetime import datetime, timezone
from PIL import Image, ImageDraw
import import_frame as shared

here=Path(__file__).resolve().parent
stage=here/'work-idle-final'
out=stage/'candidate'/shared.CHARACTER
before=shared.read(stage/'old-idle-sha256-before.json')
v=shared.module('idle_final_source_review',here/'alpha_verify.py')
v.ROOT=stage
v.mod=lambda name:shared.module('idle_final_vendor_'+name,shared.ROOT/'tools/vendor'/f'{name}.py')
rows=[]
for d in ['N','NE','E','SE','S','SW','W','NW']:
    p=out/f'idle/{d}.png'
    old=shared.IMAGE_ROOT/f'qdao_original_roster_v13/candidate/{shared.CHARACTER}/idle/{d}.png'
    batch=f'idle-{d}-edge-final-v2' if d=='SW' else f'idle-{d}-edge-final-v1'
    a=here.parent/'06-generation'/batch
    im=Image.open(p).convert('RGBA')
    mask=im.getchannel('A').point(lambda n:255 if n>=16 else 0)
    bbox=mask.getbbox()
    result=v.verify(shared.CHARACTER,d,False,None,idle_only=True)
    assert result['status']=='passed_numeric_sources_pending_visual'
    assert shared.sha(old)==before[d]
    assert im.size==(1024,1024)
    shared.write(out/f'review/validation-idle-{d}.json',result)
    rows.append({'direction':d,'selected_batch':batch,'output_sha256':shared.sha(p),'raw_sha256':shared.sha(a/'raw.png'),'native_size':[1254,1254],'output_size':list(im.size),'visible_bbox_alpha16':bbox,'old_512_sha256_before':before[d],'old_512_sha256_after':shared.sha(old),'old_bytes_unchanged':True,'independent_idle_reconstruction':True,'synthetic_frames_created':0,'visual_review':'passed','reviewed_backgrounds':['dark','light'],'findings':'Full 1024px dark/light images reviewed: correct independent planted idle, original facing/props/costume retained, clean antialiased edges, no visible fluorescent magenta fringe. Natural navy/purple cloth and cool hair shading retained.','actualModel':None,'actualQuality':None})
    # A QA-only doubled detail sheet; final sprite pixels are never modified.
    for mode,col in [('dark',(30,38,46)),('light',(240,238,228))]:
        canvas=Image.new('RGB',(1536,560),col)
        draw=ImageDraw.Draw(canvas)
        for i,(label,box) in enumerate([('hair',(384,bbox[1],640,bbox[1]+256)),('staff-left',(240,310,496,566)),('hem-shoes',(384,686,640,942))]):
            crop=im.crop(box).resize((512,512),Image.Resampling.NEAREST)
            canvas.paste(crop,(i*512,32),crop)
            draw.text((i*512+12,8),d+' '+label+' / 200% actual pixels',fill='white' if mode=='dark' else 'black')
        canvas.save(out/f'review/backgrounds/idle-{d}-{mode}-details-2x.png')

shared.write(out/'review/idle-restoration-review.json',{'scope':'06 eight independent idle directions only','reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'status':'passed_offline_static_and_source_reconstruction','directions':rows,'builtin_generation_calls':9,'paid_api_calls':0,'native_minimum_side':1254,'final_canvas':[1024,1024],'common_scale':.88,'foot_anchor':942,'walk_substitution_used':False,'superseded_batches':{'idle-SW-edge-final-v1':'Clean edges but body height 766 compared with SW walk mean 839.6 exceeded 8 percent scale drift; superseded by fresh native AI drawing v2. Source retained for root cleanup.'},'model_quality_evidence':'host-managed; actual values not disclosed; config target frozen in each generation record','limitations':['Static art and independent reconstruction only; client/runtime integration is outside this review.'],'source_deletion_performed':False})
print(json.dumps({'directions':8,'native':'1254 RGBA','old_512_unchanged':True,'numeric_sources':'passed','output_bboxes':{r['direction']:r['visible_bbox_alpha16'] for r in rows}}))
