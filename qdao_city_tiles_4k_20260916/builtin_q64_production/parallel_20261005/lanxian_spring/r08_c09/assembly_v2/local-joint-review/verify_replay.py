"""Read-only pixel replay of assembly_v2, writing only its mechanical check report."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
import numpy as np
from PIL import Image
OUT=Path(__file__).resolve().parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
arr=lambda p:np.array(Image.open(p).convert('RGB'))
data=json.loads((OUT/'assembly.json').read_text(encoding='utf-8'))
sources={s['patchId']:s for s in data['sources']}
west=data['westFixedSource'];assert sha(west['file'])==west['sha256']
old=arr(west['file']);canvas=np.zeros((4326,4326,3),np.uint8);canvas[115:4211,:115]=old[:,-115:]
owner=np.zeros((4326,4326),np.uint8);owner[115:4211,:115]=255
checks=[]
for index,step in enumerate(data['steps'],1):
    source=sources[step['patchId']]
    assert sha(source['file'])==source['sha256']
    record=source['generationRecord'];assert sha(record['file'])==record['sha256']
    raw=arr(source['file']);l,t,r,b=step['sourceCrop'];raw=raw[t:b,l:r]
    x0,y0,x1,y1=step['canvasBox'];height,width=raw.shape[:2]
    for key in ('incomingAlpha','actualRGBField','seamPaths'):
        assert sha(step[key]['file'])==step[key]['sha256']
    alpha=np.array(Image.open(step['incomingAlpha']['file']))
    with np.load(step['actualRGBField']['file']) as fields:field=fields['rgbDelta'].astype(np.int16)
    assert int(np.abs(field).max())<=16
    near=np.zeros((height,width),bool);transition=np.zeros((height,width),bool)
    with np.load(step['seamPaths']['file']) as paths:
        for direction in paths.files:
            path=paths[direction]
            distance=np.abs(np.arange(height)[:,None]-path[None,:]) if direction=='top' else np.abs(np.arange(width)[None,:]-path[:,None])
            near|=distance<160
            if direction!='west_fixed':transition|=distance<=3
    assert not np.any(field[~near])
    assert not np.any(((alpha>0)&(alpha<255))&~transition)
    assert max(abs(v) for v in step['registration']['actualShiftXY'])<=4
    corrected=np.clip(raw.astype(np.int16)+field,0,255).astype(np.uint32)
    a=alpha.astype(np.uint32)[:,:,None];before=canvas[y0:y1,x0:x1].astype(np.uint32)
    canvas[y0:y1,x0:x1]=((before*(255-a)+corrected*a+127)//255).astype(np.uint8)
    ownership=owner[y0:y1,x0:x1];ownership[alpha>=128]=index
    checks.append({'patch':step['patchId'],'sourceAndArtifactHashesMatch':True,'fieldWithin16':True,'fieldOutside160Zero':True,'blendWithin6':True})
assert np.array_equal(canvas[115:4211,:115],old[:,-115:])
for output in data['outputs']:
    assert sha(output['file'])==output['sha256']
    expected=canvas if output['pixels']==[4326,4326] else canvas[115:4211,115:4211]
    assert np.array_equal(arr(output['file']),expected)
assert np.array_equal(owner,np.array(Image.open(data['dominantSourceMask']['file'])))
report={'checkedAtUtc':datetime.now(timezone.utc).isoformat(),'assemblySha256':sha(OUT/'assembly.json'),
    'scriptSha256':sha(__file__),'sourceChecks':checks,'exactReplayMatchesBothOutputs':True,'dominantOwnershipMatches':True,
    'fixedWestHaloExact':True,'westernSourceUnchanged':sha(west['file'])==west['sha256'],'visualAccepted':False}
(OUT/'local-joint-review'/'replay-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('Exact replay passed for 4326 and 4096 outputs; fields, masks, shifts, sources and fixed west halo verified.')
