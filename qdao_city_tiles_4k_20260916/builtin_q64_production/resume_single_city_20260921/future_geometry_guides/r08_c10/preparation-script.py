"""Prepare reference-only geometry guides; never creates or counts delivery artwork.

Usage: python prepare_geometry_guides.py r08_c10 --neighbor r09_c10=ABSOLUTE_PNG
The 4096-pixel neighbor core owns only its actual global pixels. Old halos do
not override real cores. Every output directory is write-once.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, re
import numpy as np
from PIL import Image

SESSION=Path(__file__).resolve().parents[1]
ART=SESSION.parents[1]
PROJECT=ART.parent
MASTER=PROJECT/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
PLAZA=ART/'builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png'
EXPECTED_MASTER='aea4c03a216138cd447187279fb62d9f5660da875140a155ca01f88dd1f11428'
EXPECTED_PLAZA='21a40f32316a0d77e411510b71d8dc80a4ace8c4b0e4605291ee060b1aeccf98'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def coord(value):
    match=re.fullmatch(r'r(\d{2})_c(\d{2})',value)
    if not match:
        raise ValueError('Coordinate must be r01_c01 through r16_c16')
    row,col=map(int,match.groups())
    if not 1<=row<=16 or not 1<=col<=16:
        raise ValueError('Coordinate outside 16x16 map')
    return row,col

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('tile')
    ap.add_argument('--out',type=Path)
    ap.add_argument('--neighbor',action='append',default=[],help='Coordinate=absolute 4096 PNG; direct or diagonal neighbor only')
    ap.add_argument('--source',choices=['auto','master','plaza'],default='auto')
    args=ap.parse_args();row,col=coord(args.tile)
    out=args.out or SESSION/'future_geometry_guides'/args.tile
    out=out.resolve()
    if not out.is_relative_to(SESSION.resolve()):
        raise ValueError('Guide output must stay in this session')
    if out.exists():
        raise FileExistsError('Preserve previous guides: '+str(out))
    gx,gy=(col-1)*4096,(row-1)*4096
    global_box=[gx-115,gy-115,gx+4211,gy+4211]
    plaza_box=[v*3/16-4096 for v in global_box]
    inside_plaza=min(plaza_box)>=0 and max(plaza_box)<=4096
    if args.source=='plaza' and not inside_plaza:
        raise ValueError('Plaza has no full source for this extended tile; use original master')
    use_plaza=args.source=='plaza' or (args.source=='auto' and inside_plaza)
    source=PLAZA if use_plaza else MASTER
    assert sha(source)==(EXPECTED_PLAZA if use_plaza else EXPECTED_MASTER)
    box=plaza_box if use_plaza else [v*3/32 for v in global_box]
    with Image.open(source) as image:
        image.load();source_size=list(image.size)
        assert source_size==([4096,4096] if use_plaza else [6144,6144])
        # Replicate only off-map context. Such padded pixels never constitute art.
        padding=16
        padded=np.pad(np.asarray(image.convert('RGB')),((padding,padding),(padding,padding),(0,0)),mode='edge')
        canvas=Image.fromarray(padded).resize((4326,4326),Image.Resampling.BICUBIC,box=[v+padding for v in box])
    neighbors=[];seen=set()
    for value in args.neighbor:
        name,path=value.split('=',1);nr,nc=coord(name);p=Path(path)
        if name in seen or (nr==row and nc==col) or max(abs(nr-row),abs(nc-col))!=1:
            raise ValueError('Duplicate, current, or nonadjacent neighbor: '+name)
        seen.add(name)
        if not p.is_absolute():
            raise ValueError('Neighbor must be an explicit absolute file')
        before=sha(p)
        nx,ny=(nc-1)*4096,(nr-1)*4096
        left,top=max(nx,global_box[0]),max(ny,global_box[1])
        right,bottom=min(nx+4096,global_box[2]),min(ny+4096,global_box[3])
        with Image.open(p) as image:
            image.load();assert image.size==(4096,4096)
            crop=[left-nx,top-ny,right-nx,bottom-ny]
            paste=[left-global_box[0],top-global_box[1]]
            canvas.paste(image.convert('RGB').crop(crop),paste)
        assert sha(p)==before
        neighbors.append({'tile':name,'file':str(p),'sha256':before,'coreOnly':True,'sourceCropLTRB':crop,'pasteXY':paste})
    out.mkdir(parents=True,exist_ok=False)
    (out/'guides').mkdir()
    full=out/'layout-4326-reference-only.png';canvas.save(full)
    patches=[];arrays={}
    for r in range(4):
        for c in range(4):
            name=f'r{r+1:02}_c{c+1:02}';b=[c*1024,r*1024,c*1024+1254,r*1024+1254]
            im=canvas.crop(b);p=out/'guides'/(name+'.layout-only.png');im.save(p)
            arrays[r,c]=np.asarray(im)
            patches.append({'id':name,'file':str(p),'sha256':sha(p),'canvasBoxLTRB':b,'pixels':[1254,1254],'role':'geometry_guide_only_not_native_art'})
    checks=0
    for r in range(4):
        for c in range(4):
            a=arrays[r,c]
            if c<3:
                assert np.array_equal(a[:,-230:],arrays[r,c+1][:,:230]);checks+=1
            if r<3:
                assert np.array_equal(a[-230:],arrays[r+1,c][:230]);checks+=1
    script_copy=out/'preparation-script.py';script_copy.write_bytes(Path(__file__).read_bytes())
    record={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':args.tile,
      'role':'reference_only_not_native_detail_or_production_tile','operation':'mechanical source crop and reference-only resampling plus exact existing-core context',
      'finalPixelRectXYWH':[gx,gy,4096,4096],'extendedGlobalLTRB':global_box,
      'worldRect':{'x':50+(col-1)*18.75,'z':300-row*18.75,'width':18.75,'height':18.75},
      'source':{'file':str(source),'sha256':sha(source),'pixels':source_size,'cropLTRB':box},
      'sourceSelection':'local_plaza_nominal_geometry' if use_plaza else 'original_whole_city_master',
      'plazaSourceCoversWholeExtendedTile':inside_plaza,'offMapContextEdgePadded':min(global_box)<0 or max(global_box)>65536,
      'guideEnlarged':True,'guidePixelsMayBeUsedAsFinalArtwork':False,'neighborCoreOwnership':neighbors,
      'fullCanvas':{'file':str(full),'sha256':sha(full),'pixels':[4326,4326]},'patches':patches,
      'sharedOverlapChecks':checks,'allSharedOverlapPixelsEqual':True,
      'script':{'file':str(script_copy),'sha256':sha(script_copy)},
      'layoutSemanticAcceptancePassed':False,'navigationAlignmentPassed':False,'productionAccepted':False}
    (out/'geometry-record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'directory':str(out),'source':record['sourceSelection'],'sharedOverlapChecks':checks,'deliveryArtworkCreated':False}))

if __name__=='__main__':main()
