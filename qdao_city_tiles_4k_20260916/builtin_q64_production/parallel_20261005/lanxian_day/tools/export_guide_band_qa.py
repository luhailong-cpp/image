"""Export native-scale guide-band boundaries inside generated cores for actual review."""
from pathlib import Path
import argparse,json
from PIL import Image
from workflow import safe_output,sha256,write_json,save_image

def run(tile_path, include_north=False):
    t=safe_output(tile_path);p=t/'candidate/core4096.png';a=Image.open(p).convert('RGB')
    assert a.size==(4096,4096)
    out=safe_output(t/'qa/guide-bands');out.mkdir(exist_ok=True);checks=[]
    for col in range(4):
        x=col*1024+115
        for row in range(4):
            y=row*1024;box=[x-64,y,x+64,y+1024]
            q=save_image(out/f'vertical_c{col+1}_r{row+1}.png',a.crop(box))
            q.update(axis='x',coreCoordinate=x,coreBox=box,reviewed=False);checks.append(q)
    for row in range(0 if include_north else 1,4):
        y=row*1024+115
        for col in range(4):
            x=col*1024;box=[x,y-64,x+1024,y+64]
            q=save_image(out/f'horizontal_r{row+1}_c{col+1}.png',a.crop(box))
            q.update(axis='y',coreCoordinate=y,coreBox=box,reviewed=False);checks.append(q)
    write_json(out/'manifest.json',{'source':{'file':str(p),'sha256':sha256(p)},
        'reason':'Reference native overlap band ends115px inside each core. Any generated guide-edge artifact must be reviewed separately from the1024 assembly boundaries.',
        'operation':'integer crops; no resizing','includesExternalNorthGuideBoundary':include_north,
        'formalAccepted':False,'checks':checks})
    print(json.dumps({'guideBandChecks':len(checks),'directory':str(out)}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('tile');p.add_argument('--include-north',action='store_true')
    a=p.parse_args();run(a.tile,a.include_north)
