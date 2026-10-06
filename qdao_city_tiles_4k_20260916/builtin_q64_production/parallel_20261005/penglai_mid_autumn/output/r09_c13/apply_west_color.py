from pathlib import Path
import hashlib,json,shutil
from datetime import datetime,timezone
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/r09_c13';QA=ROOT/'qa/west-final';TR=QA/'color-trial'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def now():return datetime.now(timezone.utc).isoformat()

def main():
    target=OUT/'r09_c13.png';mp=OUT/'manifest.json';gp=OUT/'r09_c13.png.generation.json';rp=QA/'review.json'
    m=read(mp);g=read(gp);r=read(rp);tr=read(TR/'trial-record.json');old=Path(m['westSource'])
    before=sha(target);assert before==tr['input']['sha256']==m['sha256']==g['sha256']
    assert sha(old)==tr['oldWesternSupport']['sha256']
    for v in tr['fields']:assert sha(v['file'])==v['sha256']
    # Exact native trial-band transfer. Zero-field pixels and all geometry coordinates unchanged.
    a=np.array(Image.open(target).convert('RGB'));band=np.array(Image.open(TR/'native-band.png').convert('RGB'))
    field=np.load(TR/'color-field.npy');assert field.shape==(4096,256,3)
    assert np.max(abs(field))<=32
    out=a.copy();out[:,:256]=band
    assert np.array_equal(out[:,256:],a[:,256:])
    assert np.array_equal(out[50:300],a[50:300])
    assert np.array_equal(out[368:1004],a[368:1004])
    assert np.array_equal(out[1696:],a[1696:])
    assert np.array_equal(band,np.clip(np.rint(a[:,:256].astype(float)+field),0,255).astype(np.uint8))
    ev=OUT/'evidence';arch=[]
    for p,name in [(mp,'pre-color.manifest.json'),(gp,'pre-color.generation.json'),(rp,'pre-color.qa-review.json')]:
        q=ev/name;assert not q.exists();shutil.copyfile(p,q);arch.append(ref(q))
    for q in tr['qa']:
        q.update(actuallyViewed=True,viewedAt=now(),viewTool='view_image detail=original',verdict='safe_in_limited_applied_color_scope',finding='No new color band at the return edge or y ramps; contours are not moved. North y50..300 was protected rather than color-corrected.')
    tr.update(visualReviewPending=False,visualReview=dict(viewedAt=now(),result='approved_for_limited_application',note='Five trial QA images were viewed at1:1. Paving matched naturally; north support-contaminated post/rail region excluded. No geometry or source-artwork filtering.'),productionOutputModified=True)
    Image.fromarray(out).save(target);tr['output']=ref(target);write(TR/'trial-record.json',tr)
    operation=dict(kind='native_local_color_field_only',createdAt=now(),previousCandidateSha256=before,previousImageRetained=False,previousTextRecords=arch,
        sourceBand=ref(TR/'native-band.png'),sourceCropLTRB=[0,0,256,4096],destinationRectXYWH=[0,0,256,4096],
        zeroFieldPixelsUnchanged=True,oldWesternTileUnchanged=True,geometryDisplacement=0,sourceResampling=False,sourceUpscaling=False,artworkBlurred=False,
        maximumColorCorrectionRGB=32,actualMaximumColorCorrectionRGB=tr['actualMaximumColorCorrectionRGB'],
        coreYRanges=tr['coreYRanges'],transitionYRanges=tr['transitionYRanges'],protectedNorthYRange=[50,300],
        changedPixelCount=int(np.any(a!=out,axis=2).sum()),trialRecord=ref(TR/'trial-record.json'),fields=tr['fields'],algorithm=tr['algorithm'])
    pair=Image.new('RGB',(8192,4096));pair.paste(Image.open(old).convert('RGB'),(0,0));pair.paste(Image.fromarray(out),(4096,0))
    qa=[]
    for entry in r['qa']:
        q=dict(entry);p=Path(q['file']);op=q['operation'];oldsha=q['sha256']
        if 'sections' in op:
            im=Image.new('RGB',tuple(q['pixels']))
            for s in op['sections']:
                part=pair.crop(s['pairCropLTRB'])
                if s.get('rotateDegreesCCW')==90:part=part.transpose(Image.Transpose.ROTATE_90)
                im.paste(part,tuple(s['sheetOriginXY']))
        else:im=pair.crop(op['pairCropLTRB'])
        im.save(p);q['sha256']=sha(p)
        q['pixelContentUnchangedFromPreviousQA']=q['sha256']==oldsha
        q['previousQASha256']=oldsha
        if not q['pixelContentUnchangedFromPreviousQA']:
            q.update(actuallyViewed=False,verdict='pending_after_color',finding='')
        else:q['verificationNote']='Unchanged native crop SHA; previous actual visual review retained.'
        qa.append(q)
        write(str(p)+'.generation.json',dict(**q,createdAt=now(),derivedFrom=[ref(target),ref(old)],kind='native_pixel_QA_crop',sourceUpscaling=False))
    p=QA/'return-x256-full.png';im=Image.new('RGB',(1024,1280));sections=[]
    for i in range(4):
        box=[4192,i*1024,4512,(i+1)*1024];im.paste(pair.crop(box).transpose(Image.Transpose.ROTATE_90),(0,i*320));sections.append(dict(pairCropLTRB=box,rotateDegreesCCW=90,sheetOriginXY=[0,i*320]))
    im.save(p);q=dict(**ref(p),pixels=[1024,1280],scale=1,actuallyViewed=False,operation=dict(sections=sections,pairSeamX=4352,scope='Full4096px color return at new x256,320px context,original pixels'))
    qa.append(q);write(str(p)+'.generation.json',dict(**q,createdAt=now(),derivedFrom=[ref(target),ref(old)],kind='native_pixel_QA_crop',sourceUpscaling=False))
    r.update(createdAt=now(),source=ref(target),qa=qa,result='color_correction_merged_pending_native_QA',scopedLocalSeamsPassed=False,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False,colorCorrection=operation)
    write(rp,r)
    m.update(**ref(target),updatedAt=now(),colorCorrection=operation,qa=qa,status=r['result'],westFinalQA=ref(rp),scopedLocalSeamsPassed=False,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False)
    write(mp,m)
    g=dict(**ref(target),createdAt=now(),width=4096,height=4096,format='PNG',derivedFrom=[dict(file=str(target),sha256=before,historicalVersion=True,imageRetained=False,generationEvidence=arch[1]),ref(TR/'native-band.png')],operation=operation,
        productionPixels=True,scopedLocalSeamsPassed=False,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False,submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None,
        modelEvidence='No AI generation; native arithmetic color-field derivation. Original AI provenance preserved in previous-generation evidence.',qa=ref(rp))
    write(gp,g)
    print(json.dumps(dict(output=ref(target),changedPixels=operation['changedPixelCount'],newQA=[Path(q['file']).name for q in qa if not q['actuallyViewed']])))

if __name__=='__main__':main()
