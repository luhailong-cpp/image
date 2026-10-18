"""Isolated native production ledger. No image-model API and no writes outside this batch."""
import sys
sys.dont_write_bytecode = True
from pathlib import Path
import json, hashlib, shutil, argparse
from datetime import datetime, timezone
from PIL import Image, ImageDraw

ROOT = Path('D:/work/image')
OUT = Path(__file__).resolve().parent
BASE = ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production'
OLD = BASE/'main-city-game-20261009/southeast'
TILES = ['r12_c15', 'r12_c16']
N, C, H = 1254, 1024, 115

def now(): return datetime.now(timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,j,exclusive=False):
    p=Path(p); assert p.resolve().is_relative_to(OUT)
    p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x' if exclusive else 'w',encoding='utf-8') as f: json.dump(j,f,ensure_ascii=False,indent=2)
def png(p,im):
    assert Path(p).resolve().is_relative_to(OUT)
    with Path(p).open('xb') as f: im.save(f,format='PNG')
def info(p):
    with Image.open(p) as im: size=list(im.size)
    return {'path':str(Path(p).resolve()),'sha256':sha(p),'size':size}
def co(t,p):
    assert t in TILES
    r,c=int(t[1:3]),int(t[5:7]); pr,pc=int(p[1:3]),int(p[4:6]); assert 1<=pr<=4 and 1<=pc<=4
    x,y=(c-1)*4096+(pc-1)*C,(r-1)*4096+(pr-1)*C
    return {'tile':t,'patch':p,'coreBox':[x,y,x+C,y+C],'contextBox':[x-H,y-H,x+C+H,y+C+H],'coreCrop':[H,H,H+C,H+C]}
def authority():
    rule=ROOT/'AGENTS.md'; text=rule.read_text(encoding='utf-8-sig')
    split=read(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')
    b=next(b for b in split['batches'] if b['key']=='city_more_20261016')
    assert b['worker']=='01a14368-65c7-7691-bdea-f18c23911119' and b['tiles']==TILES and b['status']=='allocated_root_reserved'
    assert (ROOT/b['outputDirectory']).resolve()==OUT
    for tile in TILES:
        assert not (OLD/tile).exists(), 'CONFLICT: original owner has target work'
        for other in split['batches']:
            if other is not b and other['map']==b['map']: assert tile not in other['tiles'], 'CONFLICT: reservation duplicate'
    return {'rootRule':{'path':str(rule),'sha256':sha(rule)},'split':{'path':str(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json'),'sha256':sha(ROOT/'docs/MAP_PARALLEL_SPLIT_20261013.json')},'reservation':b}
def init():
    a=authority(); contract=read(BASE/'main-city-game-20261009/production-contract.json')
    refs=[Path(contract[k]) for k in ['layoutReference','detailStyleReference']]+[ROOT/'designs/mail-ui-v1/01-mail-event.png',ROOT/'designs/team-ui-v2/team-ui-v2.png']
    assert all(p.is_file() for p in refs)
    if not (OUT/'batch.json').exists(): write(OUT/'batch.json',{'createdAt':now(),'authority':a,'contract':contract,'references':[info(p) for p in refs],'model':None,'modelEvidence':'Builtin image_gen exposes no model selector; record returned metadata, never infer 2.5','builtinOnly':True,'paidApiAllowed':False,'formalAccepted':False},True)
    layout=Image.open(refs[0]).convert('RGB')
    for t in TILES:
        d=OUT/t
        if (d/'coordinates.json').exists(): continue
        for f in ['guides','native','records','qa','candidate']: (d/f).mkdir(parents=True,exist_ok=True)
        coords=[co(t,f'p{r:02d}_{c:02d}') for r in range(1,5) for c in range(1,5)]
        for q in coords:
            box=[v*layout.width/65536 for v in q['contextBox']]
            im=layout.transform((N,N),Image.Transform.EXTENT,box,Image.Resampling.NEAREST)
            png(d/'guides'/f"{q['patch']}-layout-only.png",im)
        x,y=coords[0]['coreBox'][:2]
        tileguide=layout.transform((1024,1024),Image.Transform.EXTENT,[x*layout.width/65536,y*layout.height/65536,(x+4096)*layout.width/65536,(y+4096)*layout.height/65536],Image.Resampling.NEAREST)
        png(d/'guides'/'tile-layout-only.png',tileguide)
        board=Image.new('RGB',(1024,1088),'white');board.paste(tileguide,(0,64));draw=ImageDraw.Draw(board);draw.text((20,20),t+' GEOMETRY GUIDE ONLY, NOT ART',fill='black')
        for rr in range(4):
            for cc in range(4): draw.rectangle([cc*256,64+rr*256,cc*256+255,64+rr*256+255],outline='red',width=2);draw.text((cc*256+5,64+rr*256+5),f'p{rr+1:02d}_{cc+1:02d}',fill='red')
        png(d/'guides'/'tile-grid-layout-only.png',board)
        write(d/'coordinates.json',{'patches':coords,'guideRole':'Enlarged geometry only; never deliverable pixels','sourceLayout':info(refs[0])},True)
        write(d/'selected.json',{},True)
        write(d/'progress.json',{'tile':t,'uniqueCoreCount':0,'status':'initialized_no_native','formalAccepted':False},True)
    return {'status':'initialized','output':str(OUT)}

def intersect(box,other):
    b=[max(box[0],other[0]),max(box[1],other[1]),min(box[2],other[2]),min(box[3],other[3])]
    return b if b[0]<b[2] and b[1]<b[3] else None

def prepare(t,p,content):
    core_only_bottom=content.startswith('CORE_ONLY_BOTTOM ')
    content=content.removeprefix('CORE_ONLY_BOTTOM ')
    a=authority();d=OUT/t;q=co(t,p);cb=q['contextBox'];selected=read(d/'selected.json');im=Image.open(d/'guides'/f'{p}-layout-only.png').convert('RGB');anchors=[]
    pr,pc=int(p[1:3]),int(p[4:6])
    def add(path,origin,reliable,direction):
        ib=intersect(cb,reliable)
        if not ib:return
        src=[ib[0]-origin[0],ib[1]-origin[1],ib[2]-origin[0],ib[3]-origin[1]];dst=[ib[0]-cb[0],ib[1]-cb[1],ib[2]-cb[0],ib[3]-cb[1]]
        with Image.open(path) as aimg: im.paste(aimg.convert('RGB').crop(src),dst[:2])
        anchors.append({'direction':direction,'source':info(path),'sourceCrop':src,'target':dst,'resampled':False})
    if pc>1:
        np=f'p{pr:02d}_{pc-1:02d}'
        assert np in selected,'Left core not ready'
        n=selected[np];path=Path(n['source']['path']);assert sha(path)==n['source']['sha256'];origin=co(t,np)['contextBox'][:2]
        add(path,origin,[cb[0],cb[1],cb[0]+230,cb[3]],'left')
    elif t=='r12_c16' and (OUT/'r12_c15/candidate/latest.json').exists():
        n=read(OUT/'r12_c15/candidate/latest.json');path=Path(n['candidate']['path']);assert sha(path)==n['candidate']['sha256']
        add(path,[57344,45056],[57344,45056,61440,49152],'left_external_core_only')
    elif t=='r12_c16' and (OUT/'r12_c15/selected.json').exists():
        west=read(OUT/'r12_c15/selected.json');wp=f'p{pr:02d}_04'
        if wp in west:
            n=west[wp];path=Path(n['source']['path']);assert sha(path)==n['source']['sha256'];wq=co('r12_c15',wp)
            add(path,wq['contextBox'][:2],wq['coreBox'],'left_external_core_only')
    if pr<4:
        np=f'p{pr+1:02d}_{pc:02d}'
        assert np in selected,'South core not ready'
        n=selected[np];path=Path(n['source']['path']);assert sha(path)==n['source']['sha256'];origin=co(t,np)['contextBox'][:2]
        add(path,origin,[cb[0],cb[3]-(H if core_only_bottom else 230),cb[2],cb[3]],'bottom_core_only' if core_only_bottom else 'bottom')
    else:
        nt='r13_c'+t[5:7];n=read(OLD/nt/'candidate/latest-assembly.json');path=Path(n['candidate']['path']);assert sha(path)==n['candidate']['sha256']
        x=(int(t[5:7])-1)*4096
        add(path,[x,49152],[x,49152,x+4096,53248],'bottom_external_core_only')
    v=p+'-v'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');guide=d/'guides'/f'{v}-anchored.png';png(guide,im)
    refs=read(OUT/'batch.json')['references'];anchor_text='\n'.join(f"{n['direction']} fixed rectangle {n['target']} (right/bottom exclusive), native pixels without resizing." for n in anchors)
    prompt=f'''Use case: precise-object-edit / stylized game environment. Create one native opaque EXACT 1254x1254 map context patch {t}/{p}.
Inputs 1 and 2: approved whole-city geometry and close material style REFERENCE ONLY. Input 3: Taoist chibi illustration style REFERENCE ONLY (do not copy UI, people, writing, night scene). Input 4 LAST IMAGE: the ONLY EDIT TARGET, an enlarged local geometry guide with real native anchor strips. Repaint the blocky guide area with genuinely new crisp native detail. Keep exactly the framing, perspective, scale, silhouettes and material boundaries of the last image; this is a giant partial-object DETAIL CROP, not a whole-building composition. Do not pan, zoom out, recenter, rotate or fit whole objects.
Artwork canvas65536 square; context {cb}, unique1024 core {q['coreBox']}, native core crop[115,115,1139,1139]. No resizing of generated artwork.
LOCKED ANCHORS (keep their pixels/geometry/lighting and match every endpoint into new paint):
{anchor_text}
Continue all stone seams, wood beams, eave/rib curves, walls, shadows, foliage edges exactly across each anchor boundary; do not restart textures at x230/y1024 or the115-pixel core border. At overlapping anchor corner the LAST target already defines precedence. Lower/right black region, if present, is outside overview; continue the existing local material, never paint black or a border.
Style: refined bright clean rounded Taoist chibi hand painting; natural pale grey/blue-grey stone, warm wood, teal roof, restrained gold trim, gentle daylight. Same native detail density and brushwork as anchor. No photorealistic grit, dense noise, blur, plastic glare, tiny repeated bricks, red paving, frame, text, people, UI or watermark. No new building, roof tier, finial, furniture or objects. Existing objects continue beyond crop. Do not turn a fragment into a complete object.
LOCAL CONTENT BINDING FOR THIS CROP: {content}
Output a single1254x1254 fully painted native image with the same local framing.'''
    req={'prompt':prompt,'referenced_image_paths':[refs[0]['path'],refs[1]['path'],refs[2]['path'],str(guide)],'transparent_background':False}
    write(d/'records'/f'{v}.request.json',req,True);write(d/'records'/f'{v}.preparation.json',{'createdAt':now(),'coordinate':q,'anchors':anchors,'target':info(guide),'authority':a,'status':'prepared_only_not_inflight','layoutGuideNeverDeliverable':True},True)
    return {'tile':t,'patch':p,'version':v,'request':str(d/'records'/f'{v}.request.json'),'target':str(guide),'requestArguments':req}

def ingest(t,v,source):
    d=OUT/t;req=read(d/'records'/f'{v}.request.json');prep=read(d/'records'/f'{v}.preparation.json');p=prep['coordinate']['patch'];dst=d/'native'/f'{v}.png';assert not dst.exists()
    with Image.open(source) as im: assert im.size==(N,N),f'Native dimensions differ: {im.size}';assert im.mode in ['RGB','RGBA'];assert im.mode!='RGBA' or im.getextrema()[-1]==(255,255),'Nonopaque image'
    shutil.copyfile(source,dst)
    rec={'savedAt':now(),'coordinate':prep['coordinate'],'source':info(dst),'originalOutput':str(source),'request':{'path':str(d/'records'/f'{v}.request.json'),'sha256':sha(d/'records'/f'{v}.request.json')},'entry':'image_gen.imagegen','actualModel':None,'actualQuality':None,'modelEvidence':'No actual model/quality metadata returned','resizedAfterGeneration':False,'finalArtUpscaled':False,'layoutPixelsComposited':False,'quickVisualQA':'pending'}
    write(d/'records'/f'{v}.receipt.json',rec,True);sel=read(d/'selected.json');sel[p]=rec;write(d/'selected.json',sel)
    write(d/'progress.json',{'tile':t,'updatedAt':now(),'uniqueCoreCount':len(sel),'nativeSourceVersionCount':len(list((d/'native').glob('*.png'))),'status':'native_coverage_in_progress' if len(sel)<16 else 'coverage_complete_assembly_QA_pending','internalQA':'pending','externalQA':'pending','formalAccepted':False})
    return {'tile':t,'patch':p,'uniqueCoreCount':len(sel),'source':info(dst)}

def assemble(t):
    d=OUT/t;sel=read(d/'selected.json');assert len(sel)==16
    canvas=Image.new('RGB',(4096,4096));sources=[]
    for p,n in sel.items():
        path=Path(n['source']['path']);assert sha(path)==n['source']['sha256'];q=co(t,p);pr,pc=int(p[1:3]),int(p[4:6])
        with Image.open(path) as im: assert im.size==(N,N);canvas.paste(im.convert('RGB').crop((H,H,H+C,H+C)),((pc-1)*C,(pr-1)*C))
        sources.append(n)
    ver=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ');dest=d/'candidate'/f'{t}-4k-native-{ver}.png';png(dest,canvas)
    qa=d/'qa'/ver;qa.mkdir(parents=True,exist_ok=True)
    png(qa/'overview-preview-only.png',canvas.resize((1024,1024),Image.Resampling.LANCZOS))
    for axis in ['x','y']:
        for pos in [1024,2048,3072]:
            for k in range(4):
                box=[pos-192,k*1024,pos+192,(k+1)*1024] if axis=='x' else [k*1024,pos-192,(k+1)*1024,pos+192]
                png(qa/f'{axis}{pos}-segment{k+1}-100pct.png',canvas.crop(box))
    n=read(OLD/('r13_c'+t[5:7])/'candidate/latest-assembly.json');south=Image.open(n['candidate']['path']).convert('RGB')
    joint=Image.new('RGB',(4096,512));joint.paste(canvas.crop((0,3840,4096,4096)),(0,0));joint.paste(south.crop((0,0,4096,256)),(0,256));png(qa/'south-external-joint-100pct.png',joint)
    m={'createdAt':now(),'tile':t,'candidate':info(dest),'sources':sources,'uniqueCoreCount':16,'nativeSize':[N,N],'coreSize':C,'halo':H,'composition':'Exact source1024 core crops in global positions; no resizing, blending, blur or layout pixels','qaDirectory':str(qa),'internalQA':'pending','externalQA':'pending','formalAccepted':False}
    write(d/'candidate'/f'{t}-{ver}.manifest.json',m,True);write(d/'candidate/latest.json',m)
    return {'candidate':str(dest),'qa':str(qa),'status':'coverage_complete_visual_QA_pending'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['init','prepare','ingest','assemble']);parser.add_argument('args',nargs='*');a=parser.parse_args()
    result={'init':init,'prepare':prepare,'ingest':ingest,'assemble':assemble}[a.action](*a.args)
    print(json.dumps(result,ensure_ascii=False))
