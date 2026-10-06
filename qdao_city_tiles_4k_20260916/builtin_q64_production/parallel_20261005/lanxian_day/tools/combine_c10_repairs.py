"""Compose explicitly selected independent repairs; never infer visual approval."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,json
import numpy as np
from PIL import Image
from workflow import OUTPUT_ROOT,safe_output,sha256,write_json,save_image

BASE_SHA='f4d2059a37599919d6e09aaa25c6e9ffc458bc70738c4ff13514400b324a9de9'

def load(path,size,expected):
    p=Path(path).resolve(strict=True)
    if sha256(p)!=expected:raise ValueError(f'SHA changed: {p}')
    im=Image.open(p)
    if im.size!=size or im.mode!='RGB':raise ValueError(f'Unexpected RGB dimensions: {p}')
    return np.array(im),{'file':str(p),'sha256':expected,'pixels':list(size)}

def run(a):
    tile=OUTPUT_ROOT/'r08_c10'
    original,base_meta=load(tile/'candidate/extended4326.png',(4326,4326),BASE_SHA)
    interior,interior_meta=load(a.internal_core,(4096,4096),a.internal_sha)
    west,west_meta=load(a.west_extended,(4326,4326),a.west_sha)
    internal_ext=original.copy();internal_ext[115:4211,115:4211]=interior
    west_mask=np.any(west!=original,axis=2)
    internal_mask=np.any(internal_ext!=original,axis=2)
    collision=west_mask&internal_mask
    if np.any(collision):raise ValueError(f'Repairs overlap in {collision.sum()} pixels; choose composition explicitly')
    result=internal_ext.copy();result[west_mask]=west[west_mask]
    if not np.array_equal(result[:,311:],internal_ext[:,311:]):
        raise ValueError('West repair extends beyond its agreed corex196 support')
    out=safe_output(tile/a.output_name)
    if out.exists():raise FileExistsError(out)
    out.mkdir(parents=True)
    core=result[115:4211,115:4211]
    outputs={'extended':save_image(out/'extended4326.png',Image.fromarray(result)),
             'core':save_image(out/'core4096.png',Image.fromarray(core)),
             'preview':save_image(out/'preview1024.png',Image.fromarray(core).resize((1024,1024),Image.Resampling.LANCZOS))}
    mask_path=out/'composition-support.npz';np.savez_compressed(mask_path,west=west_mask,internal=internal_mask)
    j={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
       'sources':{'original':base_meta,'westRepair':west_meta,'combinedToneAndGeometry':interior_meta},
       'operation':'Integer placement of already-repaired native-size sources in nonintersecting supports; no additional resampling, scaling, color modification, blur or feather.',
       'selectedSourcesHaveLocalGeometricResamplingAndNativeAIRepairs':True,
       'compositionResampling':'none; preview downsample only',
       'outputs':outputs,'support':{'file':str(mask_path),'sha256':sha256(mask_path),
           'westChangedPixels':int(west_mask.sum()),'internalChangedPixels':int(internal_mask.sum()),'overlapPixels':0},
       'coreIsExactCenterCrop':True,'status':'merged_candidate_pending_visual_review',
       'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False,
       'qualifiedComplete4KCandidate':False}
    write_json(out/'composition.json',j)
    print(json.dumps({'outputs':outputs,'overlapPixels':0}))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--internal-core',required=True);p.add_argument('--internal-sha',required=True)
    p.add_argument('--west-extended',required=True);p.add_argument('--west-sha',required=True);p.add_argument('--output-name',default='combined-final-v1')
    run(p.parse_args())
