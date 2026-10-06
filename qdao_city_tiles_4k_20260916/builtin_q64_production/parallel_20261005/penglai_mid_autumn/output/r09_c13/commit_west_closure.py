from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'output/r09_c13';QA=ROOT/'qa/west-final';H=ROOT/'repairs/west/closure3'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def ref(p):return dict(file=str(p),sha256=sha(p))
def now():return datetime.now(timezone.utc).isoformat()
def main():
    target=OUT/'r09_c13.png';mp=OUT/'manifest.json';gp=OUT/'r09_c13.png.generation.json';rp=QA/'review.json'
    m=read(mp);g=read(gp);r=read(rp);trial=read(H/'merge-trial-record.json');old=Path(m['westSource'])
    before=sha(target);assert before==trial['inputCurrentSha256']==m['sha256']==g['sha256']
    assert sha(H/'native-merge-trial.png')==trial['output']['sha256']
    for p in trial['passes']:
        assert sha(p['source']['file'])==p['source']['sha256']
        for f in p['fields']:assert sha(f['file'])==f['sha256']
        assert p['actualMaxDisplacementVector']<=12 and p['foldedPixels']==0
    source=np.array(Image.open(target).convert('RGB'));patch=np.array(Image.open(H/'native-merge-trial.png').convert('RGB'))
    context=np.array(Image.open(H/'target.png').convert('RGB'));oldarr=np.array(Image.open(old).convert('RGB'))
    assert np.array_equal(context[:,:627],oldarr[1894:3148,3469:4096])
    assert np.array_equal(context[:,627:],source[1894:3148,:627])
    mask=(np.array(Image.open(H/'upper.mask.png'))>0)|(np.array(Image.open(H/'lower.mask.png'))>0)
    assert np.array_equal(patch[~mask],context[~mask]) and not mask[:,:627].any() and not mask[:,1127:].any()
    result=source.copy();result[1894:3148,:500]=patch[:,627:1127]
    fullmask=np.zeros((4096,4096),bool);fullmask[1894:3148,:500]=mask[:,627:1127]
    assert np.array_equal(result[~fullmask],source[~fullmask])
    assert np.array_equal(result[3692:4096,:100],source[3692:4096,:100])
    # Keep previous text evidence, not previous4K image backups.
    archives=[]
    for p,name in [(mp,'pre-closure.manifest.json'),(gp,'pre-closure.generation.json'),(rp,'pre-closure.qa-review.json')]:
        q=OUT/'evidence'/name;assert not q.exists();shutil.copyfile(p,q);archives.append(ref(q))
    Image.fromarray(result).save(target)
    Image.fromarray(np.uint8(fullmask)*255).save(OUT/'closure-combined-mask.png')
    trial.update(visualReviewPending=False,visualReview=dict(reviewedAt=now(),result='local_merge_trial_passed',basis='Ten native context crops plus two return micro-crops actually viewed; independent agent reviewed shared joins, post contour and critical binary returns after final3px local native alignment.'),productionOutputModified=True,productionOutput=ref(target))
    write(H/'merge-trial-record.json',trial)
    operation=dict(kind='AI_rebuilt_two_broken_paving_connections_native_registered_mask_merge',createdAt=now(),previousCandidateSha256=before,previousImageRetained=False,previousTextRecords=archives,
        source=ref(H/'native-merge-trial.png'),sourceCropLTRB=[627,0,1127,1254],destinationRectXYWH=[0,1894,500,1254],combinedMask=ref(OUT/'closure-combined-mask.png'),maskZeroPixelsUnchanged=True,
        registration=trial['passes'],sourceScale=1,sourceUpscaling=False,geometryFeather=False,oldWesternTileUnchanged=True,approvedRoofEndpointUnchanged=True,
        changedPixelCount=int(np.any(result!=source,axis=2).sum()),repairEvidence=ref(H/'merge-trial-record.json'),
        fixes=[dict(id='W-GROUT-01',tileYRange=[2205,2320],kind='AI_repainted72px_disconnected_grout'),dict(id='W-GROUT-02',tileYRange=[2740,2785],kind='AI_removed_orphan_grout_stub_in_front_of_pillar')])
    pair=Image.new('RGB',(8192,4096));pair.paste(Image.fromarray(oldarr),(0,0));pair.paste(Image.fromarray(result),(4096,0))
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
        im.save(p);q['sha256']=sha(p);q['pixelContentUnchangedFromPreviousQA']=q['sha256']==oldsha;q['previousQASha256']=oldsha
        q.update(actuallyViewed=False,verdict='pending_final_native_inspection',finding='')
        qa.append(q);write(str(p)+'.generation.json',dict(**q,createdAt=now(),derivedFrom=[ref(target),ref(old)],kind='native_pixel_QA_crop',sourceUpscaling=False))
    micro=[]
    for i in range(16):
        p=QA/'closure'/f'final-edge-{i:02}.png';pair.crop((3936,i*256,4256,(i+1)*256)).save(p)
        q=dict(**ref(p),pixels=[320,256],sharedEdgeImageX=160,newTileYRange=[i*256,(i+1)*256],scale=1,actuallyViewed=False)
        micro.append(q);write(str(p)+'.generation.json',dict(**q,derivedFrom=[ref(target),ref(old)],operation='native_pixel_crop_no_resampling'))
    r.update(createdAt=now(),source=ref(target),qa=qa,finalMicroQA=micro,result='AI_structural_closure_merged_pending_final_native_QA',scopedLocalSeamsPassed=False,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False,structuralClosure=operation)
    write(rp,r)
    m.update(**ref(target),updatedAt=now(),structuralClosure=operation,qa=qa,status=r['result'],westFinalQA=ref(rp),scopedLocalSeamsPassed=False,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False)
    write(mp,m)
    newg=dict(**ref(target),createdAt=now(),width=4096,height=4096,format='PNG',derivedFrom=[dict(file=str(target),sha256=before,historicalVersion=True,imageRetained=False,generationEvidence=archives[1]),ref(H/'attempt2.png'),ref(H/'attempt3.png'),ref(H/'native-merge-trial.png')],operation=operation,productionPixels=True,formalAccepted=False,clientVerified=False,navigationVerified=False,navVerified=False,scopedLocalSeamsPassed=False,qa=ref(rp),submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None,modelEvidence='Composite derived from native builtin AI patch sources and recorded finite registration; model/quality selectors and result metadata were not exposed. Source generation sidecars retain config target and actual null evidence.')
    write(gp,newg)
    print(json.dumps(dict(output=ref(target),changedPixels=operation['changedPixelCount'],qaCount=len(qa),microCount=len(micro))))
if __name__=='__main__':main()
