"""Bounded local registration of generated existing structures; no generated holes filled by guides."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,hashlib,sys
import numpy as np
from PIL import Image
TASK=Path(__file__).resolve().parent
ROOT=next(p for p in TASK.parents if (p/'config/image-generation.json').is_file())
sys.path.insert(0,str(ROOT/'qdao_city_tiles_4k_20260916/builtin_q64_production/resume_single_city_20260921/continuation_20261004/c07-recovery/vendor'))
import cv2
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
info=lambda p:{'file':str(p),'sha256':sha(p)}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('directory',type=Path);args=ap.parse_args()
    d=args.directory.resolve();d.relative_to(TASK)
    req=json.loads((d/'request.json').read_text(encoding='utf-8-sig'))
    raw=np.array(Image.open(d/'native.png').convert('RGB'));ctx=np.array(Image.open(d/'context.png').convert('RGBA'))
    assert raw.shape==ctx[:,:,:3].shape==(1254,1254,3)
    known=ctx[:,:,3]==255
    # Raw pixels on missing side provide no registration target. Only known side estimates flow.
    target=raw.copy();target[known]=ctx[:,:,:3][known]
    inside=cv2.distanceTransform(known.astype(np.uint8),cv2.DIST_L2,5)
    outside=cv2.distanceTransform((~known).astype(np.uint8),cv2.DIST_L2,5)
    smooth=lambda x:x*x*(3-2*x)
    weight=np.where(known,smooth(np.clip((100-inside)/100,0,1)),smooth(np.clip((64-outside)/64,0,1))).astype(np.float32)
    flow=cv2.calcOpticalFlowFarneback(cv2.cvtColor(target,cv2.COLOR_RGB2GRAY),cv2.cvtColor(raw,cv2.COLOR_RGB2GRAY),None,0.5,4,41,5,7,1.5,0)
    measured=np.abs(flow[known]).max(axis=0).tolist()
    flow=np.clip(cv2.GaussianBlur(flow,(0,0),4),-4,4)*weight[:,:,None]
    yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
    aligned=cv2.remap(raw,xx+flow[:,:,0],yy+flow[:,:,1],cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
    delta=ctx[:,:,:3].astype(np.float32)-aligned.astype(np.float32);delta[~known]=0
    norm=cv2.GaussianBlur(known.astype(np.float32),(0,0),20)
    tone=cv2.GaussianBlur(delta,(0,0),20)/np.maximum(norm[:,:,None],.001)
    tone=np.clip(tone,-12,12)*weight[:,:,None]
    corrected=np.clip(np.rint(aligned.astype(np.float32)+tone),0,255).astype(np.uint8)
    alpha=np.where(known,smooth(np.clip((96-inside)/64,0,1)),1).astype(np.float32)
    joined=np.clip(np.rint(target*(1-alpha[:,:,None])+corrected*alpha[:,:,None]),0,255).astype(np.uint8)
    assert np.array_equal(joined[known & (inside>=100)],ctx[:,:,:3][known & (inside>=100)])
    assert np.array_equal(joined[(~known)&(outside>=65)],raw[(~known)&(outside>=65)])
    Image.fromarray(joined).save(d/'joined.png');Image.fromarray(np.rint(alpha*255).astype(np.uint8)).save(d/'mask.png')
    np.save(d/'flow.npy',flow);np.save(d/'tone.npy',tone)
    record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'operation':'Bounded local subpixel registration and local tone matching on already generated structures, then source-preserving overlap blend. No enlargement; no guide pixels used.','derivedFrom':[info(d/'native.png'),info(d/'context.png')],'request':info(d/'request.json'),'output':info(d/'joined.png'),'nativePixels':[1254,1254],'measuredRawFlowMaxXYKnownRegion':measured,'allowedMaxShiftPx':4,'actualMaxShiftXY':np.abs(flow).max(axis=(0,1)).tolist(),'allowedToneMaxRGB':12,'actualToneMaxRGB':np.abs(tone).max(axis=(0,1)).tolist(),'resampling':'OpenCV INTER_CUBIC only within blend neighborhood; native image dimensions retained','knownUnchangedBeyond100Px':True,'newUnchangedBeyond65Px':True,'fields':[info(d/x) for x in ['mask.png','flow.npy','tone.npy']],'script':info(Path(__file__)),'requiresVisualReview':True,'accepted':False,'formalAccepted':False}
    (d/'assembly.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    (d/'joined.png.generation.json').write_text(json.dumps({'file':str(d/'joined.png'),'sha256':sha(d/'joined.png'),'derivedFrom':record['derivedFrom'],'assembly':info(d/'assembly.json'),'operation':record['operation'],'newModelCalls':0},indent=2)+'\n',encoding='utf-8')
    qa=d/'qa';qa.mkdir(exist_ok=True)
    j=Image.fromarray(joined);c=Image.fromarray(ctx)
    j.crop((64,0,390,1254)).save(qa/'left-return-326x1254.png')
    j.crop((0,1010,1254,1254)).save(qa/'bottom-return-1254x244.png')
    j.crop((0,1010,390,1254)).save(qa/'corner-390x244.png')
    j.crop((0,900,1254,1254)).save(qa/'lower-return-1254x354.png')
    j.crop((900,0,1254,1254)).save(qa/'right-return-354x1254.png')
    board=Image.new('RGB',(978,1254),(20,20,20))
    for i,im in enumerate([c.convert('RGB'),Image.fromarray(raw),j]):board.paste(im.crop((0,0,326,1254)),(i*326,0))
    board.save(qa/'left-context-native-joined-comparison.png')
    board=Image.new('RGB',(1254,345))
    for i,im in enumerate([c.convert('RGB'),Image.fromarray(raw),j]):board.paste(im.crop((0,1139,1254,1254)),(0,i*115))
    board.save(qa/'bottom-context-native-joined-comparison.png')
    print(json.dumps({'directory':str(d),'measuredFlowMax':measured,'actualMaxShift':record['actualMaxShiftXY'],'joined':record['output']}))
if __name__=='__main__':main()
