"""Local native repair crops and exact limited composition; no image model API."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
from PIL import Image
import numpy as np
import json,shutil
from datetime import datetime,timezone
import produce as p

SPECS={
 'round-ribs':{'window':[2842,420,4096,1674],'paste':[3240,820,4096,1230], 'instruction':'Repair ONLY the broken GOLD RIBS and horizontal cut across the SAME giant round RED LANTERN in the center band. Multiple upper rib ends are stepped/disconnected from their lower ends. Join each corresponding pair into ONE smooth continuous gently curved narrow gold rib with consistent width, and continue the same red paper curvature, light and fine paper texture through the band. Remove duplicate loose rib stubs; do not add or remove ribs. Keep exact lantern silhouette, crop, size, position, all upper/lower endpoints, background and wood pillar. No cap, new lantern, extra ornaments, lettering or blur.'},
 'square-frame':{'window':[1670,2500,2924,3754],'paste':[2070,2980,2520,3340], 'instruction':'Repair ONLY the broken slim vertical RED FRAME and its narrow gold edge on the RIGHT FACE of the existing SQUARE PAPER LANTERN near image center. The upper long frame and lower short segment are horizontally displaced, and a redundant thin gold stub hangs into the cream paper. Reconnect the corresponding endpoints as ONE continuous straight frame in the same perspective, remove the duplicate detached stub, and continue cream paper texture naturally. Also remove the adjacent jagged light/color seam on the existing red vertical post only inside the same band. Preserve the whole lantern outer silhouette, paper-face angle, existing lower rim and original wood-post positions. No new frame, new object, decoration, lettering, zoom or blur.'},
 'gold-window-tone':{'window':[0,1450,1254,2704],'paste':[0,1870,680,2250], 'instruction':'Repair ONLY the jagged abrupt change of brightness/material across the existing golden wooden lattice and adjoining dark wooden wall around the horizontal center band. Continue the same individual existing wood grain and gentle natural light consistently through the band while keeping every real wooden bar, joint, edge and shadow. No blur, gradient cover, color wash, new lattice, ornament, window or object. Do not remove real structural joins or change geometry.'},
 'rear-wood-tone':{'window':[2200,1500,3454,2754],'paste':[2660,1950,3210,2310], 'instruction':'Repair ONLY the abrupt jagged light/material boundary on the existing plain vertical brown wooden panel behind the lantern plaque in the middle-right. Continue the same original boards, wood grain and daylight naturally through the boundary. Preserve every real edge of the red plaque, its supporting bracket and adjoining red post. No blur, uniform paint overlay, extra board, new ornament or geometry change.'},
}

def prepare(key):
    authority=p.authority();s=SPECS[key];tile='r12_c15';latest=p.read(p.OUT/tile/'candidate/latest.json');base=Path(latest['candidate']['path']);assert p.sha(base)==latest['candidate']['sha256']
    version=key+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');d=p.OUT/tile/'repairs'/version;d.mkdir(parents=True)
    im=Image.open(base).convert('RGB');assert im.size==(4096,4096);target=d/'target-native-1254.png';p.png(target,im.crop(s['window']))
    refs=p.read(p.OUT/'batch.json')['references'];w=s['window'];r=s['paste'];local=[r[0]-w[0],r[1]-w[1],r[2]-w[0],r[3]-w[1]]
    prompt=f'''Use case: precise-object-edit. Produce ONE native opaque EXACT1254x1254 repair image.
Inputs1/2/3 are REFERENCES ONLY: approved whole-city layout, material close-up, Taoist chibi illustration style. Input4 LAST IMAGE is the ONLY EDIT TARGET, an EXACT NATIVE1254 crop from the current4096 artwork, not a full object. Preserve its framing and all detail outside the repair rectangle. Do not pan, resize, zoom, rotate, recenter or fit a whole object.
Repair rectangle in this target: {local} (right/bottom exclusive). Outside this rectangle, keep the original pixels, geometry, illumination and brush detail. The surrounding upper/lower/left/right areas are fixed anchors. Every gold/red/wood/paper endpoint crossing the rectangle must continue exactly at its original position, width and slope.
{s['instruction']}
Keep the existing refined clean rounded Taoist chibi hand painting, teal roof, warm timber, vermilion and pale paper, soft daylight. Paint new native detail only where necessary to repair continuity. Do not add people, UI, new objects, texture noise, text, watermark, frame, extra structure or artificial highlights. Do not blur or hide the seam with a color overlay. Return same1254x1254 partial-object native crop.'''
    req={'prompt':prompt,'referenced_image_paths':[refs[0]['path'],refs[1]['path'],refs[2]['path'],str(target)],'transparent_background':False}
    record={'createdAt':p.now(),'key':key,'version':version,'tile':tile,'sourceCandidate':p.info(base),'sourceWindow':w,'pasteBoxIn4096':r,'nativePasteCrop':local,'target':p.info(target),'authority':authority,'request':req,'status':'prepared_only_not_inflight','formalAccepted':False,'actualModel':None,'entry':'image_gen.imagegen'}
    p.write(d/'preparation.json',record,True);p.write(d/'request.json',req,True)
    print(json.dumps({'key':key,'directory':str(d),'version':version,'target':str(target),'requestArguments':req}))

def save(directory,source):
    d=Path(directory).resolve();assert d.is_relative_to(p.OUT);j=p.read(d/'preparation.json');dst=d/'native-1254.png';assert not dst.exists()
    with Image.open(source) as im:assert im.size==(1254,1254);assert im.mode!='RGBA' or im.getextrema()[-1]==(255,255)
    shutil.copyfile(source,dst);p.write(d/'receipt.json',{'savedAt':p.now(),'native':p.info(dst),'originalOutput':source,'entry':'image_gen.imagegen','actualModel':None,'actualQuality':None,'modelEvidence':'No actual model/quality metadata returned','resized':False,'uniqueCoreContribution':0,'purpose':'local seam repair, not a new coverage core'},True)
    print(json.dumps({'directory':str(d),'native':p.info(dst)}))

def compose(*directories):
    ds=[Path(x).resolve() for x in directories];js=[p.read(d/'preparation.json') for d in ds];base=Path(js[0]['sourceCandidate']['path']);assert p.sha(base)==js[0]['sourceCandidate']['sha256'];assert all(j['sourceCandidate']['sha256']==js[0]['sourceCandidate']['sha256'] for j in js)
    before=Image.open(base).convert('RGB');after=before.copy();allowed=np.zeros((4096,4096),bool);repairs=[]
    for d,j in zip(ds,js):
        rec=p.read(d/'receipt.json');src=Path(rec['native']['path']);assert p.sha(src)==rec['native']['sha256'];native=Image.open(src).convert('RGB');r=j['pasteBoxIn4096'];crop=j['nativePasteCrop'];after.paste(native.crop(crop),r[:2]);allowed[r[1]:r[3],r[0]:r[2]]=True;repairs.append({'preparation':{'path':str(d/'preparation.json'),'sha256':p.sha(d/'preparation.json')},'native':p.info(src),'pasteBoxIn4096':r,'sourceCrop':crop})
    aa=np.asarray(before);bb=np.asarray(after);assert np.array_equal(aa[~allowed],bb[~allowed]);tile=js[0]['tile'];v=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');dest=p.OUT/tile/'candidate'/f'{tile}-4k-local-repairs-{v}.png';p.png(dest,after);qa=p.OUT/tile/'qa'/('local-repairs-'+v);qa.mkdir(parents=True)
    for i,j in enumerate(js):
        w=j['sourceWindow'];r=j['pasteBoxIn4096'];p.png(qa/f"{i+1}-{j['key']}-native-context.png",after.crop(w))
        for k,box in {'north':[max(0,r[0]-64),max(0,r[1]-64),min(4096,r[2]+64),min(4096,r[1]+64)],'south':[max(0,r[0]-64),max(0,r[3]-64),min(4096,r[2]+64),min(4096,r[3]+64)],'west':[max(0,r[0]-64),max(0,r[1]-64),min(4096,r[0]+64),min(4096,r[3]+64)],'east':[max(0,r[2]-64),max(0,r[1]-64),min(4096,r[2]+64),min(4096,r[3]+64)]}.items():p.png(qa/f"{i+1}-{j['key']}-{k}-perimeter.png",after.crop(box))
    m={'createdAt':p.now(),'tile':tile,'candidate':p.info(dest),'baseCandidate':p.info(base),'repairs':repairs,'uniqueCoreCount':16,'sources':p.read(p.OUT/tile/'selected.json'),'outsideRepairRectanglesExactlyUnchanged':True,'changedPixelCount':int(np.any(aa!=bb,axis=2).sum()),'resized':False,'blur':False,'composition':'Exact1254 native crops, integer paste only; outside rectangles byte-identical','qaDirectory':str(qa),'internalQA':'pending_local_visual_review_full_tile_not_passed','externalQA':'pending','formalAccepted':False}
    manifest=dest.with_suffix('.manifest.json');p.write(manifest,m,True)
    print(json.dumps({'candidate':str(dest),'manifest':str(manifest),'qa':str(qa),'outsideExactlyUnchanged':True}))

if __name__=='__main__':{'prepare':prepare,'save':save,'compose':compose}[sys.argv[1]](*sys.argv[2:])
