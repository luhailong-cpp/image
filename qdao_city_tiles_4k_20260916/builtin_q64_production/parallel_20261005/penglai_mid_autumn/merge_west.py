from pathlib import Path
import sys,importlib.util
from production import ROOT,read,write,sha,now,deriv
sys.path.insert(0,str(ROOT/'tools/deps'))
import numpy as np
from PIL import Image
HELPER=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/tools/mechanical_join.py')
spec=importlib.util.spec_from_file_location('join',HELPER);mj=importlib.util.module_from_spec(spec);spec.loader.exec_module(mj)
OUT=ROOT/'output/r09_c13';QA=ROOT/'qa/west-merged';OUT.mkdir(parents=True,exist_ok=True);QA.mkdir(parents=True,exist_ok=True)

def main():
    h=read(ROOT/'handoff.json');left=Path(h['baselineCandidates'][2]['file']);base=ROOT/'assembly-registered/r09_c13-candidate.png'
    leftarr=np.array(Image.open(left).convert('RGB'));old=np.array(Image.open(base).convert('RGB'));right=old.copy(); records=[];ys=[0,947,1894,2842]
    bounds=[(0,1100),(1100,2050),(2050,3000),(3000,4096)]
    for i,y in enumerate(ys):
        src=ROOT/'repairs/west'/f'west{i+1}.png';rec=read(str(src)+'.generation.json');assert rec['sha256']==sha(src)
        # Crop native patch only, keeping115px of western support; never enlarge.
        patch=np.array(Image.open(src).convert('RGB'))[:,512:1254].copy()
        context=np.concatenate([leftarr[y:y+1254,3981:4096],right[y:y+1254,:627]],axis=1)
        yy,xx=np.mgrid[:1254,:742];gy=yy+y
        alpha=(xx>=115).astype(float)*np.clip((615-xx)/48,0,1)
        lo,hi=bounds[i]
        if i>0:alpha*=np.clip((gy-lo+32)/64,0,1)
        if i<3:alpha*=np.clip((hi+32-gy)/64,0,1)
        alpha=alpha*alpha*(3-2*alpha);mask=np.uint8(np.rint(alpha*255))
        merged,flow,tone,report=mj.registered_join(context,patch,mask,max_shift=6,flow_inner=230,flow_full=130,tone_inner=280,tone_full=140)
        assert np.array_equal(merged[:,:115],context[:,:115]);right[y:y+1254,:627]=merged[:,115:]
        fields={}
        for name,a in [('mask',mask),('flow',flow),('colorCorrection',tone)]:
            p=OUT/(f'west{i+1}.'+name+('.png' if name=='mask' else '.npy'))
            if name=='mask':Image.fromarray(a).save(p)
            else:np.save(p,a)
            fields[name]=dict(file=str(p),sha256=sha(p))
        records.append(dict(id=f'west{i+1}',source=str(src),sourceSha256=sha(src),sourceCropLTRB=[512,0,1254,1254],patchGlobalRectXYWH=[49037,32768+y,742,1254],newTileEditableRectXYWH=[0,y,500,1254],rowCore=[lo,hi],parameters=report,fields=fields))
    assert np.array_equal(right[:,500:],old[:,500:]),'Changed outside editable west500px'
    final=Image.fromarray(right);target=OUT/'r09_c13.png';final.save(target)
    deriv(target,[base]+[ROOT/'repairs/west'/f'west{i+1}.png' for i in range(4)],dict(kind='AI_reconstructed_west_connections_masked_native_merge',nativeSourceScale=1,sourceUpscaling=False,oldWesternTileUnchanged=True,unchangedBeyondNewTileX=500,repairs=records))
    g=read(str(target)+'.generation.json');g.update(productionPixels=True,formalAccepted=False);write(str(target)+'.generation.json',g)
    qa=[]
    # Full shared edge and full return-to-base edge; native100% strips.
    pair=Image.new('RGB',(8192,4096));pair.paste(Image.fromarray(leftarr),(0,0));pair.paste(final,(4096,0))
    for label,x in [('shared',4096),('return',4596)]:
        sheet=Image.new('RGB',(1024,1280))
        for n in range(4):sheet.paste(pair.crop((x-160,n*1024,x+160,(n+1)*1024)).transpose(Image.Transpose.ROTATE_90),(0,n*320))
        p=QA/f'{label}-full.png';sheet.save(p);qa.append(dict(file=str(p),sha256=sha(p),scope=f'4096px full{label} edge,320wide',actuallyViewed=False,scale=1))
    for i,y in enumerate([1100,2050,3000]):
        p=QA/f'repair-crossing-{y}.png';pair.crop((3936,y-160,4756,y+160)).save(p);qa.append(dict(file=str(p),sha256=sha(p),actuallyViewed=False,scale=1))
    p=QA/'endpoints.png';im=Image.new('RGB',(1320,320));im.paste(pair.crop((3936,0,4596,320)),(0,0));im.paste(pair.crop((3936,3776,4596,4096)),(660,0));im.save(p);qa.append(dict(file=str(p),sha256=sha(p),actuallyViewed=False,scale=1))
    final.resize((1254,1254),Image.Resampling.LANCZOS).save(ROOT/'current-preview.png');deriv(ROOT/'current-preview.png',[target],dict(kind='candidate_preview_downsample',scale='1254/4096'))
    write(OUT/'manifest.json',dict(createdAt=now(),tile='r09_c13',file=str(target),sha256=sha(target),pixels=[4096,4096],globalPixelRectXYWH=[49152,32768,4096,4096],completePixelCoverage=True,internalQA=read(ROOT/'qa/registered/review.json'),oldWesternTileUnchanged=True,westSource=str(left),westSourceSha256=sha(left),repairs=records,qa=qa,formalAccepted=False,clientVerified=False,status='west_repaired_pending_native_QA'))
    print(str(target))
if __name__=='__main__':main()
