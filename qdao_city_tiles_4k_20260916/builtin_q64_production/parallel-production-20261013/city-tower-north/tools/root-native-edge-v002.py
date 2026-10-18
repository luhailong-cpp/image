"""Verified native ROI integration at tile edges; integer pixels and <=16px linear alpha only."""
import argparse
import json
import shutil
from pathlib import Path
from PIL import Image, ImageChops
import native_seam_v003 as base

B = base.B

def local(path):
    p = Path(path).resolve()
    assert p.is_relative_to(B), 'Path outside this production batch'
    return p

def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('prepare','request','prompt','event-id','version','session-log','south-candidate'):
        p.add_argument('--'+name, required=True)
    p.add_argument('--source-rect', nargs=4, type=int, required=True)
    p.add_argument('--feather', type=int, default=16)
    a = p.parse_args()
    assert a.version.startswith('root-')
    base.n.verify_contracts()
    prepare, request, prompt = local(a.prepare), local(a.request), local(a.prompt)
    prep, req = base.read(prepare), base.read(request)
    assert prep['tile']=='r04_c13'
    baseline, inp, southp = local(prep['baseline']['file']), local(prep['input']['file']), Path(a.south_candidate).resolve()
    assert southp == Path(r'D:\work\image\qdao_city_tiles_4k_20260916\builtin_q64_production\main-city-game-20261009\northeast\r05_c13\candidates\r05_c13.candidate.png').resolve(), 'Unexpected read-only south reference'
    assert base.sha(southp)=='a130950d95d08674c325bec88caed4cd68744abf556fe12b9bc7c65d67db7673'
    assert base.sha(baseline)==prep['baseline']['sha256'] and base.sha(inp)==prep['input']['sha256']
    assert prompt.read_text(encoding='utf-8')==req['prompt']
    assert str(inp) in req['referenced_image_paths']
    refs=[base.artifact(local(x)) for x in req['referenced_image_paths']]
    source, receipt, digest = base.rr.completed_event(Path(a.session_log),a.event_id)
    native, before, south = base.rgb(source,(1254,1254)),base.rgb(baseline,(4096,4096)),base.rgb(southp,(4096,4096))
    sx,sy,ex,ey = a.source_rect
    assert 0<=sx<ex<=1254 and 0<=sy<ey<=1254
    cx,cy,_,_ = prep['contextTileXYXY']
    x,y,x1,y1 = cx+sx,cy+sy,cx+ex,cy+ey
    assert 0<=x<x1<=4096 and 0<=y<y1<=4096, 'ROI outside r04_c13'
    f=a.feather
    assert 0<=f<=16 and min(ex-sx,ey-sy)>2*f
    w,h=ex-sx,ey-sy
    released=[k for k,yes in [('west',x==0),('north',y==0),('east',x1==4096),('south',y1==4096)] if yes]
    def alpha(px,py):
        distances=[]
        if x>0: distances.append(px)
        if y>0: distances.append(py)
        if x1<4096: distances.append(w-1-px)
        if y1<4096: distances.append(h-1-py)
        return round(255*min(1,min(distances)/f)) if f and distances else 255
    mask=Image.new('L',(w,h)); mask.putdata([alpha(px,py) for py in range(h) for px in range(w)])
    after=before.copy(); after.paste(native.crop((sx,sy,ex,ey)),(x,y),mask)
    diff=ImageChops.difference(before,after);diff.paste((0,0,0),(x,y,x1,y1))
    assert diff.getbbox() is None
    d=base.outdir(a.version)
    nativep=d/'native-repair.png';shutil.copyfile(source,nativep);assert base.sha(nativep)==digest
    candidate=d/'r04_c13-candidate.png';base.png(candidate,after)
    maskp=d/'linear-alpha-mask.png';base.png(maskp,mask)
    base.js(d/'receipt.json',receipt)
    evidence=[]
    for name,box in [('north',[x-115,y-115,x1+115,y+115]),('south',[x-115,y1-115,x1+115,y1]),
                     ('west',[x-115,y-115,x+115,y1]),('east',[x1-115,y-115,x1+115,y1])]:
        box=[max(0,box[0]),max(0,box[1]),min(4096,box[2]),min(4096,box[3])]
        q=d/(name+'-perimeter-100pct.png');base.png(q,after.crop(box));evidence.append({**base.artifact(q),'crop':box})
    ctx=d/'repaired-context-100pct.png';base.png(ctx,after.crop(prep['contextTileXYXY']))
    qx,qx1=max(0,x-115),min(4096,x1+115)
    joint=Image.new('RGB',(qx1-qx,480));joint.paste(after.crop((qx,3856,qx1,4096)),(0,0));joint.paste(south.crop((qx,0,qx1,240)),(0,240))
    jointp=d/'south-cross-tile-joint-100pct-QA-only.png';base.png(jointp,joint)
    record={**prep,'schemaVersion':2,'createdAtUtc':base.n.now(),'previousCandidate':base.artifact(baseline),
      'candidate':base.artifact(candidate),'nativeRepair':base.artifact(nativep),'inputPrepare':base.artifact(prepare),
      'submittedRequest':base.artifact(request),'exactPrompt':base.artifact(prompt),'references':refs,
      'receipt':base.artifact(d/'receipt.json'),'actualModel':None,'actualModelEvidence':'未返回',
      'sourceNativeROIXYXY':a.source_rect,'sourceCoreXYXY':[115,115,1139,1139],
      'sourceROIIncludesHalo':sx<115 or sy<115 or ex>1139 or ey>1139,
      'editTileXYXY':[x,y,x1,y1],'repairOverlayPixels':[w,h],'candidatePixels':[4096,4096],
      'originalCoreCount':16,'additionalCoreCount':0,'formalAcceptedCount':0,
      'operations':['integer crop from verified actual 1254 native AI source','integer ROI composite with linear alpha up to '+str(f)+' pixels','no feather at physical tile edges: '+str(released)],
      'integrationTool':base.artifact(Path(__file__).resolve()),'baseHelper':base.artifact(Path(base.__file__).resolve()),
      'noResize':True,'noWarp':True,'noImageBlur':True,'alphaPerimeterPixels':f,'unfeatheredPhysicalEdges':released,
      'alphaMask':base.artifact(maskp),'unchangedOutsideEditVerified':True,'nativeEventBytesMatch':True,
      'perimeterEvidence':evidence,'contextEvidence':base.artifact(ctx),
      'southNeighbor':base.artifact(southp),'southCrossTileEvidence':base.artifact(jointp),
      'southJointQa':'pending visual check; no external edge pass inferred','visualQa':'pending; formalAcceptedCount=0'}
    base.js(d/'integration.json',record)
    print(json.dumps({'record':str(d/'integration.json'),'candidate':record['candidate'],'formalAcceptedCount':0},ensure_ascii=False))

if __name__=='__main__':
    main()
