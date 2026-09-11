"""Complete reviewed contiguous v9 edge cleanup; staging only."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from stage_local_edges import EXPECTED,REGIONS as ORIGINAL_REGIONS

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
REGIONS={4:[[430,1000,1390,3900]],
         14:[[1100,190,2780,1100],[2720,500,3060,1180],
             [2700,1050,3190,1650],[790,1000,1580,1620]]}
PROTECTED={4:[],14:[[1450,1140,2530,1480],[2590,1090,2800,1450]]}
POINTS={4:[(1303,2558),(1170,2650),(960,2850),(830,3050),(734,3230),
           (900,1680),(830,1120),(616,2550),(815,3810)],
        14:[(2335,348),(2804,938),(3015,1234),(1065,1252),
            (1900,315),(1370,680),(1250,939),(2810,1010),
            (3100,1280),(2850,1500),(1150,1500),(1400,1530)]}

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rectangular_mask(shape,regions):
    m=np.zeros(shape,dtype=bool)
    for x0,y0,x1,y1 in regions:m[y0:y1,x0:x1]=True
    return m

def evidence(source,output,number,mask):
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
    pages=[]
    for start in range(0,len(POINTS[number]),3):
        page=Image.new('RGB',(1300,1020),'#e8e3d8');draw=ImageDraw.Draw(page)
        for j,(x,y) in enumerate(POINTS[number][start:start+3]):
            draw.text((12,j*340+5),f'{number:02d} ({x},{y}) - native crop at 2x - before light/dark | after light/dark',font=font,fill='#193b30')
            for col,im in enumerate((source,output)):
                crop=im.crop((x-75,y-75,x+75,y+75)).resize((300,300),Image.Resampling.NEAREST)
                for k,bg in enumerate(('#f9f1de','#182a25')):
                    tile=Image.new('RGBA',crop.size,bg);tile.alpha_composite(crop)
                    page.paste(tile.convert('RGB'),(12+col*640+k*310,j*340+30))
        name=f'expanded-review-{number:02d}-{start//3+1:02d}.png';page.save(HERE/name);pages.append(name)
    mask_path=HERE/f'expanded-mask-{number:02d}.png'
    Image.fromarray((mask*255).astype(np.uint8)).save(mask_path)
    # Whole affected extent, with protected artwork visible for review.
    box=(430,1000,1390,3900) if number==4 else (790,190,3170,1650)
    for tag,im in [('before',source),('after',output)]:
        crop=im.crop(box);tile=Image.new('RGBA',crop.size,'#182a25');tile.alpha_composite(crop)
        tile.convert('RGB').save(HERE/f'expanded-{number:02d}-{tag}.jpg',quality=96)
    return pages

def main(only=None):
    records=[]
    previous=json.loads((HERE/"review.json").read_text(encoding="utf-8")) if (HERE/"review.json").exists() else {"records":[]}
    for number,regions in REGIONS.items():
        if only is not None and number not in only:
            prior=next(r for r in previous["records"] if Path(r["path"]).name.startswith(f"{number:02d}_"))
            assert sha(ROOT/prior["staged_path"])==prior["output_sha256"]
            assert sha(ROOT/prior["path"])==prior["source_sha256"]
            records.append(prior)
            continue
        source=next((ROOT/'q_daoist_character_pack_4096').glob(f'{number:02d}_*.png'))
        assert sha(source)==EXPECTED[number],'Source changed; review again'
        im=Image.open(source).convert('RGBA');a=np.asarray(im).copy();out=a.copy()
        rgb=a[:,:,:3].astype(np.float32);alpha=a[:,:,3];r,g,b=rgb.transpose(2,0,1);dom=np.minimum(r,b)-g
        in_regions=rectangular_mask(alpha.shape,regions)
        protected=rectangular_mask(alpha.shape,PROTECTED[number])
        # 20 px transparent-boundary band includes antialiased key bleed.
        near=np.asarray(Image.fromarray(((alpha<16)*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(41)))>0
        original=rectangular_mask(alpha.shape,ORIGINAL_REGIONS[number])
        if number==4:
            selected=in_regions&(near|original)&(r>g+6)&(b>g+3)&(alpha>0)
            clean=(b<=g)&(alpha>=230)
        else:
            selected=in_regions&(near|original)&(dom>10)&(alpha>0)
            clean=(dom<4)&(alpha>=230)
        selected &= ~protected
        weights=np.array([.2126,.7152,.0722],dtype=np.float32)
        changed=[];donors=[];unresolved=[]
        for y,x in zip(*np.nonzero(selected)):
            donor=None
            for radius in (5,10,20,36,60):
                x0,x1=max(0,x-radius),min(alpha.shape[1],x+radius+1)
                y0,y1=max(0,y-radius),min(alpha.shape[0],y+radius+1)
                yy,xx=np.nonzero(clean[y0:y1,x0:x1]);yy+=y0;xx+=x0
                if len(xx):
                    k=int(np.argmin((xx-x)**2+(yy-y)**2));donor=rgb[yy[k],xx[k]];dxy=[int(xx[k]),int(yy[k])];break
            if donor is None:unresolved.append([int(x),int(y)]);continue
            value=donor+float(rgb[y,x]@weights-donor@weights)
            out[y,x,:3]=np.clip(np.rint(value),0,255).astype(np.uint8)
            if not np.array_equal(out[y,x,:3],a[y,x,:3]):changed.append([int(x),int(y)]);donors.append(dxy)
        assert not unresolved
        assert np.array_equal(a[:,:,3],out[:,:,3])
        assert np.array_equal(a[~selected],out[~selected])
        assert np.array_equal(a[protected],out[protected])
        assert len(changed)<alpha.size*.005
        relative=source.relative_to(ROOT).as_posix();dest=HERE/'staged'/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        result=Image.fromarray(out);result.save(dest,optimize=True)
        assert sha(source)==EXPECTED[number]
        pages=evidence(im,result,number,selected)
        luma_delta=np.abs((out[:,:,:3].astype(float)-a[:,:,:3])@weights)
        records.append({'path':relative,'staged_path':dest.relative_to(ROOT).as_posix(),
            'source_sha256':EXPECTED[number],'output_sha256':sha(dest),'size':list(im.size),
            'alpha_bbox':list(im.getchannel('A').getbbox()),'original_regions':ORIGINAL_REGIONS[number],
            'regions':regions,'protected_regions':PROTECTED[number],'edge_band_radius_px':20,
            'changed_rgb_pixels':len(changed),'changed_coordinates':changed,'donor_coordinates':donors,
            'alpha_changed_pixels':0,'unselected_pixels_changed':0,'outside_regions_changed':0,
            'protected_pixels_changed':0,'max_changed_pixel_luma_delta':float(luma_delta[selected].max()),
            'unresolved_pixels':unresolved,'evidence':pages})
        print(number,len(changed),flush=True)
    dump(HERE/'review.json',{'status':'staged_needs_expanded_visual_review',
        'created_utc':datetime.now(timezone.utc).isoformat(),'processor':Path(__file__).relative_to(ROOT).as_posix(),
        'processor_sha256':sha(Path(__file__)),'method':'Region-limited transparent-edge chroma transfer from nearest clean same-image foreground; retain per-pixel luminance, alpha, and protected purple artwork.',
        'expansion_evidence':['context-04-extended.png','context-14.png','expanded-source-04.png','expanded-source-14.png'],
        'records':records})

if __name__=='__main__':main([int(v) for v in sys.argv[1:]] or None)
