"""Prepare reviewed repairs and exact dependent copies without publishing."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import hashlib,json,shutil
from datetime import datetime,timezone
import numpy as np
import repair_edges as b

DEST=b.PACK/'delivery'
def stage(rel,im=None,src=None):
    old=b.ROOT/rel;out=DEST/rel;out.parent.mkdir(parents=True,exist_ok=True)
    before=b.sha(old)
    if src:shutil.copy2(src,out)
    else:im.save(out,optimize=True)
    assert b.sha(old)==before
    return {'path':rel,'before_sha256':before,'sha256':b.sha(out),'stage':out.relative_to(b.ROOT).as_posix()}

def main():
    rows=[];support=b.load(b.PACK/'support-v2.json')['records'];source={r['path']:r for r in support}
    for r in support:
        s=b.PACK/'support-v2'/r['path'];assert b.sha(s)==r['output_sha256'];assert b.sha(b.ROOT/r['path'])==r['source_sha256']
        a=np.array(Image.open(b.ROOT/r['path']).convert('RGBA'));o=np.array(Image.open(s).convert('RGBA'))
        assert a.shape==o.shape and np.array_equal(a[:,:,3],o[:,:,3])
        rows.append(stage(r['path'],src=s))
    pre=b.load(b.ROOT/'docs/style-repair-20260911/publish-preflight.json')['edge_repair']
    for c in pre['copies']:
        assert b.sha(b.ROOT/c['path'])==c['copy_sha256']
        s=DEST/c['source']
        if c['pixels_identical_to_source']:rows.append(stage(c['path'],src=s))
        else:rows.append(stage(c['path'],Image.open(s).convert('RGBA').resize(tuple(c['size']),Image.Resampling.LANCZOS)))
    # Preserve the approved 124 original atlas coordinates and untouched padding.
    atlas=pre['atlas'];ap=b.ROOT/atlas['file']['path'];assert b.sha(ap)==atlas['file']['sha256']
    sheet=Image.open(ap).convert('RGBA');dependencies=[]
    for f in atlas['frames']:
        s=DEST/f['source'] if f['source'] in source else b.ROOT/f['source']
        if f['source'] not in source:assert b.sha(s)==f['source_sha256']
        im=Image.open(s).convert('RGBA');x,y,x2,y2=f['rect_xyxy'];assert im.size==(x2-x,y2-y)
        sheet.paste(im,(x,y));dependencies.append({'path':f['source'],'sha256':b.sha(s)})
    for f in atlas['frames']:
        s=DEST/f['source'] if f['source'] in source else b.ROOT/f['source']
        assert sheet.crop(f['rect_xyxy']).tobytes()==Image.open(s).convert('RGBA').tobytes()
    rows.append(stage(atlas['file']['path'],sheet))
    # Rebuild only four heads. All frozen rectangles and canvas dimensions stay.
    contract=b.load(b.ROOT/'qdao_ui_style_recut_v10/contracts/attributes.json')
    portrait_rows=[]
    for e in contract['sprites']:
        if not e['name'].startswith('portrait_') or e['name']=='portrait_frame':continue
        rel='designs/attribute-panels/assets/'+e['name'].removeprefix('portrait_')+'.png'
        im=Image.open(DEST/rel).convert('RGBA');x,y,w,h=e['sourceRectNativeTopLeft']
        out=im.resize((e['width'],e['height']),Image.Resampling.LANCZOS,box=(x,y,x+w,y+h))
        target='designs/attribute-panels/v2-painted/unity-slices/png/'+e['name']+'.png'
        for dest in [target,'qdao_ui_style_recut_v10/staged/'+target]:
            r=stage(dest,out);r['source']=rel;r['source_sha256']=b.sha(DEST/rel);rows.append(r);portrait_rows.append(r)
    result={'status':'prepared_needs_final_visual_review','created_utc':datetime.now(timezone.utc).isoformat(),'records':rows,'atlas_dependencies':dependencies,'portraits':portrait_rows}
    b.dump(b.PACK/'delivery-plan.json',result)
    # All four head crops at 3x on light/dark for before/after review.
    board=Image.new('RGB',(1320,760),'#e9e3d5');d=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    for k,r in enumerate(portrait_rows[1::2]):
        x0=(k%2)*660;y0=(k//2)*380;d.text((x0+4,y0+4),Path(r['path']).name+' OLD / NEW',fill='#17372b',font=font)
        for j,p in enumerate([b.ROOT/r['path'],DEST/r['path']]):
            im=Image.open(p).convert('RGBA').resize((300,300),Image.Resampling.NEAREST)
            for z,bg in enumerate(['#eee9d9','#182e29']):
                tile=Image.new('RGBA',(150,300),bg);tile.alpha_composite(im,(-75,0));board.paste(tile.convert('RGB'),(x0+j*326+z*150,y0+34))
    board.save(b.PACK/'portraits-final.jpg',quality=95)
    print(json.dumps({'staged_files':len(rows),'atlas_cells_verified':124,'portrait_files':len(portrait_rows)}))
if __name__=='__main__':main()
