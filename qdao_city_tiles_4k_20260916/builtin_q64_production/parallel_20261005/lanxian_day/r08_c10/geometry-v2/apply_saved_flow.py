"""Apply the exact saved geometry-v2 field to a chosen RGB input, e.g. tone-v1."""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib, json, sys
import numpy as np
from PIL import Image

BASE=Path(__file__).resolve().parent
TILE=BASE.parent.resolve()
sys.path.insert(0,'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor')
import cv2

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def apply_saved_flow(input_array, flow_file=BASE/'flow-correction.npz'):
    """Return a new image; one local INTER_LINEAR remap, identical saved dx/dy."""
    assert input_array.shape==(4096,4096,3) and input_array.dtype==np.uint8
    output=input_array.copy()
    with np.load(flow_file) as fields:
        for name in ('HG01a','HG01b','HG02','H2c3'):
            x0,y0,x1,y1=map(int,fields[name+'_support_box'])
            dx=fields[name+'_applied_flow_x'];dy=fields[name+'_applied_flow_y']
            active=(np.abs(dx)+np.abs(dy))>1e-7
            yy,xx=np.mgrid[y0:y1,x0:x1].astype(np.float32)
            warped=cv2.remap(input_array,xx+dx,yy+dy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT_101)
            output[y0:y1,x0:x1][active]=warped[active]
    return output

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',required=True,type=Path)
    p.add_argument('--input-sha',required=True)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--flow',type=Path,default=BASE/'flow-correction.npz')
    a=p.parse_args();src=a.input.resolve(strict=True);out=a.output.resolve()
    if not out.is_relative_to(TILE) or out==src or 'candidate' in out.relative_to(TILE).parts:
        raise ValueError('Output must be a new derivative inside r08_c10, never the input or candidate directory')
    if out.exists():raise FileExistsError(out)
    if sha(src)!=a.input_sha:raise ValueError('Input checksum mismatch')
    im=Image.open(src)
    if im.size!=(4096,4096) or im.mode!='RGB':raise ValueError('Expected 4096x4096 RGB input')
    before=np.array(im);after=apply_saved_flow(before,a.flow)
    with np.load(a.flow) as f:
        active=(np.abs(f['flow_x'])+np.abs(f['flow_y']))>1e-7
    assert np.array_equal(before[~active],after[~active])
    out.parent.mkdir(parents=True,exist_ok=True);Image.fromarray(after).save(out)
    report=dict(createdAt=datetime.now(timezone.utc).isoformat(),input=dict(file=str(src),sha256=a.input_sha),
        flow=dict(file=str(a.flow.resolve()),sha256=sha(a.flow)),output=dict(file=str(out),sha256=sha(out)),
        operation='same geometry-v2 displacement field applied to supplied RGB pixels; no source-PNG overwrite composition',
        resampling='single local OpenCV INTER_LINEAR subpixel remap',outsideSupportUnchanged=True,
        actualToneGeometryComposition='Input tone changes are retained and moved by the exact same saved geometric field',
        formalAccepted=False,visualInspectionPerformed=False)
    rp=Path(str(out)+'.registration.json');rp.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':main()
