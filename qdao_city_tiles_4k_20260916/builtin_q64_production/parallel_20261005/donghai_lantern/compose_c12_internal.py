"""Composite two native AI lighting repairs only within recorded local masks."""
from pathlib import Path
import json, sys
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
import internal_c12_repairs as repair
import assemble_c12_shared as shared
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'r08_c12/internal-repaired/output'
QA=OUT.parent/'qa'
MASKS=OUT.parent/'masks'

def main():
    for p in (OUT,QA,MASKS):p.mkdir(parents=True,exist_ok=True)
    shared.OUT,shared.QA=OUT,QA
    helper=shared.load_helpers()
    source=ROOT/'r08_c12/tone-assembly/output/extended-context.png'
    source_record=shared.read(str(source)+'.generation.json')
    base=shared.load_rgb(source,source_record['sha256'],(4326,4326)); result=base.copy()
    support=np.zeros((4326,4326),bool); records=[]
    for name,job in repair.JOBS.items():
        path=repair.R/'native'/f'{name}.png'
        rec=shared.read(str(path)+'.generation.json')
        native=shared.load_rgb(path,rec['sha256'],(1254,1254))
        x,y=job['xy']; l,t,r,b=job['repairBoundsTileXYXY']; yy,xx=np.mgrid[:1254,:1254]
        distance=np.minimum.reduce([xx+x-l,yy+y-t,r-1-xx-x,b-1-yy-y]).astype(np.float32)
        weight=np.clip(distance/48,0,1);weight=weight*weight*(3-2*weight)
        alpha=np.rint(weight*255).astype(np.uint8)
        mask=MASKS/f'{name}.png';Image.fromarray(alpha).save(mask)
        mask_record={'file':str(mask),'sha256':shared.sha(mask),'operation':'Smoothstep48-pixel local AI repair return mask','boundsTileXYXY':[l,t,r,b],'nativePatchXYWH':[x,y,1254,1254]}
        helper.atomic_write(OUT/f'{name}-mask.json',(json.dumps(mask_record,indent=2)+'\n').encode('utf-8'))
        view=result[y+115:y+115+1254,x+115:x+115+1254]
        view[:]=shared.blend(view,native,alpha)
        support[y+115:y+115+1254,x+115:x+115+1254]|=alpha>0
        records.append({'native':{'file':str(path),'sha256':shared.sha(path),'generationRecord':str(path)+'.generation.json'},'mask':mask_record,'placementExtendedXY':[x+115,y+115],'registration':False,'colorMatching':False,'nativeResampled':False})
    assert np.array_equal(result[~support],base[~support])
    assert all(np.array_equal(result.take(i,axis=a),base.take(i,axis=a)) for a in (0,1) for i in (0,114,115,4210,4211,4325))
    common={'operation':'Two native AI local repairs: roof lighting steps and verified paving edge truncations; 48-pixel return masks','derivedFrom':[{'file':str(source),'sha256':shared.sha(source),'generationRecord':str(source)+'.generation.json'}]+[r['native'] for r in records],
            'repairs':records,'outsideMasksPixelIdentical':True,'externalBoundariesPixelIdentical':True,'artResampled':False,'artUpscaled':False,'imageBlur':False,
            'completePixelCandidate':True,'formalAccepted':False,'visualReview':'pending','finalArt':False,'noStructureSynthesizedByCode':True,'dayGeometrySynchronizationRequired':True,'geometryDifferenceScope':'Paving repair ROI only; day reference contains the same false truncated edge. Own text record only; day pixels untouched.'}
    ext=Image.fromarray(result); core=ext.crop((115,115,4211,4211))
    ei=helper.save_image(OUT/'extended-context.png',ext,{**common,'globalRectXYWH':[44941,28557,4326,4326]})
    ci=helper.save_image(OUT/'r08_c12.png',core,{**common,'globalRectXYWH':[45056,28672,4096,4096]})
    pi=helper.save_image(OUT/'preview-1024.png',core.resize((1024,1024),Image.Resampling.LANCZOS),{'operation':'Downsampled overview only','derivedFrom':[ci],'finalArt':False,'notNativePixelQA':True})
    qa=[]
    for name,job in repair.JOBS.items():
        x,y=job['xy']; box=[x,y,x+1254,y+1254]
        qa.append(helper.save_image(QA/f'{name}-complete-return.png',core.crop(box),{'operation':'Exact native crop including complete repair mask and all four returns','derivedFrom':[ci],'sourceCropXYXY':box,'resized':False,'finalArt':False}))
    for name,job in repair.JOBS.items():
        l,t,r,b=job['repairBoundsTileXYXY']
        for side,box in [('left',[l-64,t-48,l+112,b+48]),('right',[r-112,t-48,r+64,b+48]),('top',[l-48,t-64,r+48,t+112]),('bottom',[l-48,b-112,r+48,b+64])]:
            box=[max(0,box[0]),max(0,box[1]),min(4096,box[2]),min(4096,box[3])]
            qa.append(helper.save_image(QA/f'{name}-return-{side}.png',core.crop(box),{'operation':'Exact native crop of full local repair attachment and48-pixel return','derivedFrom':[ci],'sourceCropXYXY':box,'resized':False,'finalArt':False}))
    manifest={**common,'candidate':ci,'extendedContext':ei,'preview':pi,'qa':qa,'script':{'file':str(Path(__file__)),'sha256':shared.sha(__file__)},'changedPixels':int(np.any(result!=base,axis=2).sum())}
    helper.atomic_write(OUT/'internal-integration-manifest.json',(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'candidate':ci,'changedPixels':manifest['changedPixels'],'qa':qa},indent=2))
if __name__=='__main__':main()
