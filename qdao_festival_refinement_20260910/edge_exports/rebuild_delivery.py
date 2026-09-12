"""Deterministic assembly/publication for the approved v11 RGB edge-export batch."""
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw,ImageFont,ImageSequence
import numpy as np
import sys,json,hashlib,shutil,importlib.util,argparse
import repair_v11_edges as e
ROOT=e.ROOT;PACK=e.PACK;ROSTER=e.ROSTER;SLUGS=e.SLUGS;DIRS=e.DIRS
STAGE=PACK/'staged';SROSTER=STAGE/'qdao_chibi_roster_v11'

def gif_processor():
    path=Path.home()/'.agents/skills/generate2dsprite/scripts/generate2dsprite.py'
    spec=importlib.util.spec_from_file_location('existing_sprite_exporter',path);m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m,path


def save_gif_exact_binary_alpha(frames,path,sp):
    # Reuse the existing exporter's shared palette, then reserve transparency
    # index0 explicitly. Otherwise a rare opaque pink can quantize to the key.
    sp.save_transparent_gif(frames,path,120)
    with Image.open(path) as g:palette=g.getpalette()
    palette_image=Image.new('P',(1,1));palette_image.putpalette(palette)
    colors=np.asarray(palette,dtype=np.int16).reshape(-1,3);encoded=[]
    for frame in frames:
        rgba=np.asarray(frame);q=frame.convert('RGB').quantize(palette=palette_image,dither=Image.Dither.NONE);a=np.array(q)
        foreground=rgba[:,:,3]>=128;a[~foreground]=0
        for y,x in zip(*np.nonzero(foreground&(a==0))):
            delta=colors[1:].astype(np.int32)-rgba[y,x,:3].astype(np.int32);a[y,x]=1+int(np.argmin(np.sum(delta*delta,axis=1)))
        q=Image.fromarray(a,mode='P');q.putpalette(palette);encoded.append(q)
    encoded[0].save(path,format='GIF',save_all=True,append_images=encoded[1:],duration=120,loop=0,disposal=2,transparency=0,background=0,optimize=False)

def compose(frames,cols):
    out=Image.new('RGBA',(cols*512,((len(frames)+cols-1)//cols)*512),(0,0,0,0))
    for i,f in enumerate(frames):out.paste(f,((i%cols)*512,(i//cols)*512))
    return out

def checks(base,before):
    rows=[];allframes=[];frames={};gifs=[]
    m=e.load(before/'manifest.json')
    for f in m['files']:
        p=base/f['path'];old=before/f['path'];im=Image.open(p)
        row={'path':f['path'],'sha256':e.sha(p),'bytes':p.stat().st_size,'before_sha256':e.sha(old),'size':list(im.size),'mode':im.mode,'changed':e.sha(p)!=e.sha(old)}
        if p.suffix=='.png':
            o=Image.open(old);assert im.mode==o.mode=='RGBA' and im.size==o.size
            a=np.array(im);oa=np.array(o);assert np.array_equal(a[:,:,3],oa[:,:,3]),str(p)
            row['alpha_sha256']=e.ah(a[:,:,3]);row['alpha_unchanged']=True;row['rgb_changed_pixels']=int(np.any(a[:,:,:3]!=oa[:,:,:3],axis=2).sum())
            if p.parent.name in DIRS and p.stem.isdigit():
                assert im.size==(512,512);yy,xx=np.where(a[:,:,3]>8);assert yy.max()==471
                ax=float(np.median(xx[yy>=np.percentile(yy,90)]));assert abs(ax-256)<=.5
                row['foot_xy']=[ax,471];allframes.append(row['sha256'])
            elif p.name=='portrait.png':assert im.size==(1024,1024)
        else:
            assert im.n_frames==4 and im.size==(512,512) and im.info.get('loop')==0
            times=[];oldim=Image.open(old)
            for n,g in enumerate(ImageSequence.Iterator(im)):
                times.append(g.info.get('duration'));rgba=np.array(g.convert('RGBA'));oldim.seek(n)
                assert np.array_equal(rgba[:,:,3],np.array(oldim.convert('RGBA'))[:,:,3]),str(p)+' GIF alpha changed'
                png=np.array(Image.open(base/'walk'/p.parent.name/f'{n+1:02d}.png'))
                assert not np.any((rgba[:,:,3]>0)&(png[:,:,3]<128)),'GIF reveals pixels outside accepted PNG threshold'
                row.setdefault('preserved_legacy_gif_threshold_exceptions',[]).append(int(np.count_nonzero((rgba[:,:,3]>0)!=(png[:,:,3]>=128))))
            assert times==[120]*4;row['duration_ms_each']=times;row['binary_alpha_unchanged']=True
        rows.append(row)
    assert len(allframes)==32 and len(set(allframes))==32
    for d in DIRS:
        ff=[Image.open(base/'walk'/d/f'{n:02d}.png').convert('RGBA') for n in range(1,5)];frames[d]=ff
        assert Image.open(base/'walk'/d/'strip.png').tobytes()==compose(ff,4).tobytes()
    for kind,ds in [('cardinal',['S','W','E','N']),('diagonal',['SW','NW','NE','SE'])]:
        assert Image.open(base/f'walk-{kind}.png').tobytes()==compose([im for d in ds for im in frames[d]],4).tobytes()
    assert len(rows)==51
    return rows

def build():
    stage=e.load(PACK/'stage.json');assert stage['summary']['base_images']==198
    sp,script=gif_processor();characters=[]
    for slug in SLUGS:
        base=SROSTER/slug;frames={}
        for d in DIRS:
            ff=[Image.open(base/'walk'/d/f'{n:02d}.png').convert('RGBA') for n in range(1,5)];frames[d]=ff
            compose(ff,4).save(base/'walk'/d/'strip.png',optimize=True)
            # Preserve the old GIF binary Alpha as well. The original palette
            # occasionally hid a few magenta fringe pixels above PNG alpha128.
            # Current RGB comes exclusively from the same clean PNG frame.
            oldgif=Image.open(PACK/'before'/'qdao_chibi_roster_v11'/slug/'walk'/d/'walk.gif');gifframes=[]
            for n,frame in enumerate(ff):
                oldgif.seek(n);preview=frame.copy();preview.putalpha(oldgif.convert('RGBA').getchannel('A'));gifframes.append(preview)
            save_gif_exact_binary_alpha(gifframes,base/'walk'/d/'walk.gif',sp)
        evidence=[]
        for kind,ds in [('cardinal',['S','W','E','N']),('diagonal',['SW','NW','NE','SE'])]:
            sheet=compose([im for d in ds for im in frames[d]],4);sheet.save(base/f'walk-{kind}.png',optimize=True)
            for label,bg in [('light','#f2eddf'),('dark','#172c26')]:
                page=Image.new('RGB',(1024,1112),'#e9e3d6');draw=ImageDraw.Draw(page)
                font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
                for y,d in enumerate(ds):
                    for x,im in enumerate(frames[d]):
                        tile=Image.new('RGBA',(256,256),bg);tile.alpha_composite(im.resize((256,256),Image.Resampling.LANCZOS))
                        page.paste(tile.convert('RGB'),(x*256,y*278+22));draw.text((x*256+8,y*278+2),slug[:2]+' '+d+' '+str(x+1)+' '+label,fill='#17382d',font=font)
                ep=base/'processing'/f'festival-edge-{kind}-{label}.jpg';ep.parent.mkdir(parents=True,exist_ok=True);page.save(ep,quality=95)
                evidence.append({'path':ep.relative_to(base).as_posix(),'sha256':e.sha(ep)})
        rows=checks(base,PACK/'before'/'qdao_chibi_roster_v11'/slug)
        characters.append({'slug':slug,'files':rows,'evidence':evidence,'status':'numeric_passed_pending_visual_approval'})
        print(slug,'assembled and exact Alpha/geometry/GIF checks passed',flush=True)
    data={'schema':'qdao.festival.edge-derived.v1','status':'numeric_passed_pending_visual_approval','created_utc':e.now(),'base_stage_sha256':e.sha(PACK/'stage.json'),'processor_sha256':e.sha(PACK/'repair_v11_edges.py'),'gif_exporter':str(script),'gif_exporter_sha256':e.sha(script),'characters':characters,'summary':{'roles':6,'formal_media':306,'changed_media':sum(f['changed'] for c in characters for f in c['files']),'changed_png':sum(f['changed'] and f['path'].endswith('.png') for c in characters for f in c['files']),'gifs_rebuilt':48,'png_alpha_changes':0,'gif_binary_alpha_changes':0,'frame_order_and_anchor':'unchanged; 192 unique poses, x256 +/-0.5, y471'}}
    e.dump(PACK/'derived.json',data);print(json.dumps(data['summary']),flush=True)

def publish():
    approval=e.load(PACK/'visual-approval.json');data=e.load(PACK/'derived.json')
    assert approval['status']=='approved' and approval['derived_sha256']==e.sha(PACK/'derived.json')
    assert data['base_stage_sha256']==e.sha(PACK/'stage.json')
    before=e.load(PACK/'before.json');index={f['path']:f for f in before['files']}
    # Entire write set is verified before the first publication; stale upstream
    # changes make this fail safely instead of silently rolling them back.
    for c in data['characters']:
        for f in c['files']:
            src=SROSTER/c['slug']/f['path'];dst=ROSTER/c['slug']/f['path']
            assert e.sha(src)==f['sha256'];assert e.sha(dst)==f['before_sha256']
        for name in ['manifest.json','qc.json']:
            p=ROSTER/c['slug']/name;assert e.sha(p)==index[e.local(p)]['sha256']
        for ev in c['evidence']:assert e.sha(SROSTER/c['slug']/ev['path'])==ev['sha256']
    published=[]
    for c in data['characters']:
        slug=c['slug'];base=ROSTER/slug;old=PACK/'before'/'qdao_chibi_roster_v11'/slug
        record={'schema':'qdao.visual-approval.v1','status':'approved','approved_utc':e.now(),'reviewer':approval['reviewer'],'scope':'RGB-only chroma matte export correction; no redesigned source, pose, alpha or layout','prior_geometry_and_design_qc':{'record':e.local(old/'qc.json'),'sha256':e.sha(old/'qc.json'),'attribution':'Original producer pose/design acceptance, frozen before this export correction; alpha geometry is byte-identical.'},'files':[{'path':f['path'],'sha256':f['sha256']} for f in c['files']],'review_evidence':c['evidence'],'checks':approval['checks'],'batch_review_record':e.local(PACK/'visual-approval.json'),'batch_review_sha256':e.sha(PACK/'visual-approval.json')}
        rp=base/'processing/festival-edge-approval.json';e.dump(SROSTER/slug/'processing/festival-edge-approval.json',record)
        manifest=e.load(old/'manifest.json')
        for f in manifest['files']:
            r=next(x for x in c['files'] if x['path']==f['path']);f.update(sha256=r['sha256'],bytes=r['bytes'])
        manifest['festival_edge_export']={'record':'processing/festival-edge-approval.json','sha256':e.sha(SROSTER/slug/'processing/festival-edge-approval.json'),'batch_record':e.local(PACK/'derived.json'),'batch_record_sha256':e.sha(PACK/'derived.json'),'rebuild_entry':e.local(PACK/'repair_v11_edges.py'),'alpha_geometry_and_identity':'unchanged','previous_manifest':e.local(old/'manifest.json'),'previous_manifest_sha256':e.sha(old/'manifest.json'),'previous_processing_records':'Historical generation/scale transforms remain original; current RGB/file hashes are in this manifest and the new approval.'}
        qc=e.load(old/'qc.json');qc['historical_visual_review']={'record':e.local(old/'qc.json'),'sha256':e.sha(old/'qc.json'),'attribution':'Producer acceptance of the original generated design and poses; not current export approval'}
        qc['visual_review']={'status':'approved','record':'processing/festival-edge-approval.json','sha256':e.sha(SROSTER/slug/'processing/festival-edge-approval.json'),'reviewed_at_utc':record['approved_utc'],'review_scope':'Current final media hash-bound RGB-edge correction; source pose acceptance retained separately.'}
        qc['festival_edge_validation']={'formal_media':51,'png_alpha_changes':0,'gif_binary_alpha_changes':0,'frames':32,'frame_size':[512,512],'feet_y':471,'feet_x_tolerance':.5,'strips_sheets_equal_frames':True,'gif_duration_ms':120,'gif_frames':4,'record':e.local(PACK/'derived.json'),'sha256':e.sha(PACK/'derived.json')}
        qc['status']='passed_visual_and_numeric_qc'
        e.dump(SROSTER/slug/'manifest.json',manifest);e.dump(SROSTER/slug/'qc.json',qc)
        for f in c['files']:
            src=SROSTER/slug/f['path'];dst=base/f['path']
            if f['changed']:shutil.copy2(src,dst);published.append({'path':e.local(dst),'sha256':e.sha(dst),'previous_sha256':f['before_sha256'],'kind':'media'})
        for name in ['manifest.json','qc.json','processing/festival-edge-approval.json']+[x['path'] for x in c['evidence']]:
            src=SROSTER/slug/name;dst=base/name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert e.sha(src)==e.sha(dst)
            published.append({'path':e.local(dst),'sha256':e.sha(dst),'kind':'metadata_or_visual_evidence'})
        checks(base,old)
        print(slug,'published and reverified',flush=True)
    e.dump(PACK/'publication.json',{'status':'published_and_reverified','created_utc':e.now(),'approval':e.local(PACK/'visual-approval.json'),'approval_sha256':e.sha(PACK/'visual-approval.json'),'files':published,'media_changed':sum(x['kind']=='media' for x in published),'next':'Rebuild roster overview/index, run full existing delivery verification, refresh current ZIP; unchanged27/30 remain byte-identical.'})

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','publish']);a=p.parse_args();build() if a.action=='build' else publish()
