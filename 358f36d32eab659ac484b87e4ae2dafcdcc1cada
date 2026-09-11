"""Read-only production comparison evidence for the staged hero repair."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json, hashlib

ROOT=Path(__file__).resolve().parent.parent
PACK=Path(__file__).resolve().parent

def main():
    data=json.loads((PACK/'review-v2.json').read_text(encoding='utf-8'))
    old_review=json.loads((ROOT/'docs/style-audit-20260910/continuation/edges/review.json').read_text(encoding='utf-8'))
    rois={r['path']:next(e['crop_xyxy'] for e in r['evidence'] if e.get('crop_xyxy')) for r in old_review['records']}
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',16)
    evidence=[]
    for start in range(0,len(data['records']),4):
        records=data['records'][start:start+4]
        page=Image.new('RGB',(1536,480*len(records)),'#eee7da');draw=ImageDraw.Draw(page)
        for row,record in enumerate(records):
            src=ROOT/record['path']; dest=ROOT/record['output']
            assert hashlib.sha256(src.read_bytes()).hexdigest()==record['source_sha256'],'Production changed since staging'
            assert hashlib.sha256(dest.read_bytes()).hexdigest()==record['output_sha256'],'Staged output changed'
            roi=rois[record['path']]
            for col,path in enumerate((src,dest)):
                im=Image.open(path).convert('RGBA')
                for bgidx,bg in enumerate(('#f1eedf','#172a25')):
                    x=col*768+bgidx*384;y=row*480
                    draw.text((x+8,y+5),src.name+(' OLD' if col==0 else ' V2'),fill='#17372f',font=font)
                    full=im.copy();full.thumbnail((330,330))
                    tile=Image.new('RGBA',(384,430),bg);tile.alpha_composite(full,(27,0))
                    crop=im.crop(roi);crop.thumbnail((100,100));crop=crop.resize((crop.width,crop.height),Image.Resampling.NEAREST)
                    tile.alpha_composite(crop,(140,326));page.paste(tile.convert('RGB'),(x,y+35))
        output=PACK/f'review-v2-exact-{start//4+1:02}.jpg';page.save(output,quality=98);evidence.append(output.name)
    data['evidence_exact_rois']=evidence
    (PACK/'review-v2.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'files':len(data['records']),'evidence':evidence,'source_hashes_current':True,'staged_hashes_current':True}))

if __name__=='__main__':main()
