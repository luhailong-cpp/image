from pathlib import Path
import numpy as np
from PIL import Image
from production import ROOT,read,write,sha,now,deriv

OUT=ROOT/'assembly'; QA=ROOT/'qa/full'; OUT.mkdir(exist_ok=True); QA.mkdir(parents=True,exist_ok=True)
def minimum_cut(a,b,axis,label):
    if axis==0: a,b=a.transpose(1,0,2),b.transpose(1,0,2)
    cost=np.mean(np.abs(a.astype(float)-b.astype(float)),axis=2)
    # Spatially central mild prior avoids selecting the very edge of a halo.
    h,w=cost.shape; cost+=np.abs(np.arange(w)-w/2)[None,:]*0.005
    acc=cost[0].copy(); parent=np.zeros((h,w),np.int8)
    for y in range(1,h):
        options=np.stack([np.r_[1e12,acc[:-1]],acc,np.r_[acc[1:],1e12]])
        choice=np.argmin(options,axis=0); parent[y]=choice-1; acc=cost[y]+options[choice,np.arange(w)]
    xs=np.empty(h,np.int32); xs[-1]=np.argmin(acc)
    for y in range(h-1,0,-1): xs[y-1]=xs[y]+parent[y,xs[y]]
    m=np.arange(w)[None,:]>=xs[:,None]; result=np.where(m[:,:,None],b,a)
    if axis==0: result=result.transpose(1,0,2); m=m.T
    path=OUT/f'{label}.mask.png'; Image.fromarray(m.astype(np.uint8)*255).save(path)
    return result,dict(id=label,axis=axis,overlap=230,mask=str(path),maskSha256=sha(path),resampling=False,feather=0,meanOverlapDifference=float(cost.mean()),maxSeamStep=int(np.abs(np.diff(xs)).max()))

def main():
    sources=[]; joins=[]; row_arrays=[]
    for r in range(1,5):
        row=np.zeros((1254,4326,3),np.uint8)
        for c in range(1,5):
            p=ROOT/'rows'/f'row{r}'/f'p{r}{c}.png'; im=Image.open(p).convert('RGB'); assert im.size==(1254,1254),str(p)
            rec=read(str(p)+'.generation.json'); assert sha(p)==rec['sha256'],str(p)
            sources.append(p); a=np.asarray(im); x=(c-1)*1024
            if c==1: row[:,:1254]=a
            else:
                overlap,j=minimum_cut(row[:,x:x+230],a[:,:230],1,f'h-r{r}-c{c-1}-c{c}')
                joins.append(j); row[:,x:x+230]=overlap; row[:,x+230:x+1254]=a[:,230:]
        row_arrays.append(row)
    master=np.zeros((4326,4326,3),np.uint8)
    for r,row in enumerate(row_arrays):
        y=r*1024
        if r==0: master[:1254]=row
        else:
            overlap,j=minimum_cut(master[y:y+230],row[:230],0,f'v-r{r}-r{r+1}');joins.append(j)
            master[y:y+230]=overlap;master[y+230:y+1254]=row[230:]
    ext=Image.fromarray(master); ex=OUT/'r09_c13-extended.png';ext.save(ex)
    final=ext.crop((115,115,4211,4211)); target=OUT/'r09_c13-candidate.png';final.save(target)
    for p in [ex,target]:
        deriv(p,sources,dict(kind='native_patch_minimum_cut_assembly',sourcePixelScale=1,sourceResampling=False,sourceUpscaling=False,geometryWarp=False,blur=False,core=1024,halo=115,joins=joins,finalCropLTRB=[115,115,4211,4211]))
        meta=read(str(p)+'.generation.json');meta['productionPixels']=True;meta['formalAccepted']=False;write(str(p)+'.generation.json',meta)
    final.resize((1254,1254),Image.Resampling.LANCZOS).save(ROOT/'current-preview.png')
    deriv(ROOT/'current-preview.png',[target],dict(kind='candidate_preview_downsample',scale='1254/4096'))
    qa=[]
    for axis in ['x','y']:
        for pos in [1024,2048,3072]:
            sheet=Image.new('RGB',(1024,1280))
            boxes=[]
            for n in range(4):
                box=(pos-160,n*1024,pos+160,(n+1)*1024) if axis=='x' else (n*1024,pos-160,(n+1)*1024,pos+160)
                crop=final.crop(box)
                if axis=='x':crop=crop.transpose(Image.Transpose.ROTATE_90)
                sheet.paste(crop,(0,n*320));boxes.append(box)
            p=QA/f'{axis}{pos}-full.png';sheet.save(p);qa.append(dict(file=str(p),sha256=sha(p),boxes=boxes,scale=1,rotation90=axis=='x',actuallyViewed=False))
    sheet=Image.new('RGB',(960,960));centers=[]
    for r,y in enumerate([1024,2048,3072]):
        for c,x in enumerate([1024,2048,3072]):sheet.paste(final.crop((x-160,y-160,x+160,y+160)),(320*c,320*r));centers.append([x,y])
    p=QA/'junctions.png';sheet.save(p);qa.append(dict(file=str(p),sha256=sha(p),centers=centers,scale=1,actuallyViewed=False))
    h=read(ROOT/'handoff.json');west=Image.open(h['baselineCandidates'][2]['file']).convert('RGB');edge=Image.new('RGB',(320,4096));edge.paste(west.crop((3936,0,4096,4096)),(0,0));edge.paste(final.crop((0,0,160,4096)),(160,0));sheet=Image.new('RGB',(1024,1280))
    for n in range(4):sheet.paste(edge.crop((0,n*1024,320,(n+1)*1024)).transpose(Image.Transpose.ROTATE_90),(0,320*n))
    p=QA/'west-c12-c13-full.png';sheet.save(p);qa.append(dict(file=str(p),sha256=sha(p),scale=1,rotation90=True,scope='Full4096px c12-c13 shared boundary320px width',actuallyViewed=False))
    corners=Image.new('RGB',(640,640))
    for i,(x,y) in enumerate([(0,0),(3776,0),(0,3776),(3776,3776)]):corners.paste(final.crop((x,y,x+320,y+320)),((i%2)*320,(i//2)*320))
    p=QA/'outer-corners.png';corners.save(p);qa.append(dict(file=str(p),sha256=sha(p),scale=1,scope='four tile corners; missing outside neighbours not accepted',actuallyViewed=False))
    write(OUT/'assembly.json',dict(createdAt=now(),tile='r09_c13',file=str(target),sha256=sha(target),pixels=[4096,4096],globalPixelRectXYWH=[49152,32768,4096,4096],sourceCount=16,sourcePixelScale=1,sourceResampling=False,joins=joins,qa=qa,completePixelCoverage=True,formalAccepted=False,clientVerified=False,status='complete_pixels_pending_visual_QA'))
    p=read(ROOT/'progress.json');p.update(updatedAt=now(),newAIGenerations=18,nativeFragments=17,newNativeDetailPatches=16,newFullPixelCandidates=0,totalFullPixelCandidates=3,completePixelCoveragePendingQA=['r09_c13'],currentPreview=str(ROOT/'current-preview.png'));write(ROOT/'progress.json',p)
    w=read(ROOT/'current-work.json');w.update(updatedAt=now(),stage='full_native_seam_QA',next='Inspect six full internal lines, nine junctions, full western edge and all corners; repair evidenced defects.');write(ROOT/'current-work.json',w)
    print(str(target))
if __name__=='__main__':main()
