from pathlib import Path
import importlib.util, sys
from production import ROOT,read,write,sha,now,deriv
sys.path.insert(0,str(ROOT/'tools/deps'))
import cv2
import numpy as np
from PIL import Image

HELPER=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tools/mechanical_join.py')
spec=importlib.util.spec_from_file_location('join',HELPER);mj=importlib.util.module_from_spec(spec);spec.loader.exec_module(mj)
OUT=ROOT/'assembly-registered';QA=ROOT/'qa/registered';OUT.mkdir(exist_ok=True);QA.mkdir(parents=True,exist_ok=True)
def main():
    canvas=np.zeros((4326,4326,3),np.uint8); sources=[]; reports=[]
    for r in range(4):
        for c in range(4):
            p=ROOT/'rows'/f'row{r+1}'/f'p{r+1}{c+1}.png'; rec=read(str(p)+'.generation.json');assert rec['sha256']==sha(p)
            patch=np.array(Image.open(p).convert('RGB'));assert patch.shape==(1254,1254,3);sources.append(p)
            x,y=c*1024,r*1024;context=patch.copy();edges=[]
            if r:context[:230]=canvas[y:y+230,x:x+1254];edges.append('top')
            if c:context[:,:230]=canvas[y:y+1254,x:x+230];edges.append('left')
            if not edges:canvas[y:y+1254,x:x+1254]=patch;continue
            yy,xx=np.mgrid[:1254,:1254];d=np.full((1254,1254),1254.)
            if r:d=np.minimum(d,yy)
            if c:d=np.minimum(d,xx)
            alpha=np.clip((d-99)/32,0,1);alpha=alpha*alpha*(3-2*alpha);mask=np.uint8(np.rint(alpha*255))
            merged,flow,tone,report=mj.registered_join(context,patch,mask,edges=edges,max_shift=6,flow_inner=230,flow_full=130,tone_inner=330,tone_full=140)
            # Only supports existing near-matching structure. No source is enlarged.
            canvas[y:y+1254,x:x+1254]=merged; label=f'p{r+1}{c+1}';fields={}
            for name,a in [('mask',mask),('flow',flow),('colorCorrection',tone)]:
                dst=OUT/f'{label}.{name}'+('.png' if name=='mask' else '.npy') if False else OUT/(label+'.'+name+('.png' if name=='mask' else '.npy'))
                if name=='mask':Image.fromarray(a).save(dst)
                else:np.save(dst,a)
                fields[name]=dict(file=str(dst),sha256=sha(dst))
            reports.append(dict(id=label,source=str(p),sourceSha256=sha(p),patchXY=[x,y],parameters=report,fields=fields))
    ex=OUT/'r09_c13-extended.png';Image.fromarray(canvas).save(ex)
    final=Image.fromarray(canvas[115:4211,115:4211]);p=OUT/'r09_c13-candidate.png';final.save(p)
    for dst in [ex,p]:
        deriv(dst,sources,dict(kind='limited_registration_and_local_tone_match_existing_structures',sourcePixelScale=1,maxShiftPixels=6,resampling='bicubic subpixel within edge band',blurArtwork=False,sourceUpscaling=False,maskFeatherPixels=32,helper=str(HELPER),helperSha256=sha(HELPER),patches=reports))
        meta=read(str(dst)+'.generation.json');meta.update(productionPixels=True,formalAccepted=False);write(str(dst)+'.generation.json',meta)
    final.resize((1254,1254),Image.Resampling.LANCZOS).save(ROOT/'current-preview.png');deriv(ROOT/'current-preview.png',[p],dict(kind='candidate_preview_downsample',scale='1254/4096'))
    qa=[]
    for axis in ['x','y']:
        for pos in [1024,2048,3072]:
            sheet=Image.new('RGB',(1024,1280));boxes=[]
            for n in range(4):
                box=(pos-160,n*1024,pos+160,(n+1)*1024) if axis=='x' else (n*1024,pos-160,(n+1)*1024,pos+160)
                im=final.crop(box)
                if axis=='x':im=im.transpose(Image.Transpose.ROTATE_90)
                sheet.paste(im,(0,n*320));boxes.append(box)
            dst=QA/f'{axis}{pos}-full.png';sheet.save(dst);qa.append(dict(file=str(dst),sha256=sha(dst),boxes=boxes,scale=1,rotation90=axis=='x',actuallyViewed=False))
    sheet=Image.new('RGB',(960,960))
    for r,y in enumerate([1024,2048,3072]):
        for c,x in enumerate([1024,2048,3072]):sheet.paste(final.crop((x-160,y-160,x+160,y+160)),(320*c,320*r))
    dst=QA/'junctions.png';sheet.save(dst);qa.append(dict(file=str(dst),sha256=sha(dst),scope='all9 internal junctions,320square each',scale=1,actuallyViewed=False))
    write(OUT/'assembly.json',dict(createdAt=now(),tile='r09_c13',file=str(p),sha256=sha(p),pixels=[4096,4096],globalPixelRectXYWH=[49152,32768,4096,4096],sourceCount=16,sourcePixelScale=1,sourceResampling='limited native edge registration',patches=reports,qa=qa,completePixelCoverage=True,formalAccepted=False,clientVerified=False,status='internal_registered_candidate_pending_visual_QA'))
    print(str(p))
if __name__=='__main__':main()
