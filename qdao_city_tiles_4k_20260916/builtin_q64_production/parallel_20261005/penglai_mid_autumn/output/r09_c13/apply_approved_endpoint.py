from pathlib import Path
import hashlib, json, shutil
from datetime import datetime, timezone
import numpy as np
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/r09_c13'
QA=ROOT/'qa/west-final'
DIAG=ROOT/'repairs/west/diagnostic'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,v): Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def now(): return datetime.now(timezone.utc).isoformat()
def ref(p): return dict(file=str(p),sha256=sha(p))

def main():
    target=OUT/'r09_c13.png'; mp=OUT/'manifest.json'; gp=OUT/'r09_c13.png.generation.json'
    m=read(mp); g=read(gp); d=read(DIAG/'anchored-record.json')
    before=sha(target)
    assert before==d['inputCurrentSha256']==m['sha256']==g['sha256'], 'Input changed; no mutation permitted.'
    trial=DIAG/'anchored-trial.png'
    assert sha(trial)==next(v['sha256'] for v in d['files'] if Path(v['file']).name==trial.name)
    old=Path(m['westSource']); oldsha=sha(old)
    assert oldsha==m['westSourceSha256']==d['sourceOldSha256']
    for f in d['files']: assert sha(f['file'])==f['sha256']
    arr=np.array(Image.open(target).convert('RGB')); replacement=np.array(Image.open(trial).convert('RGB'))[850:1254,115:215]
    result=arr.copy(); result[3692:4096,:100]=replacement
    assert arr.shape==(4096,4096,3) and replacement.shape==(404,100,3)
    assert np.array_equal(result[:3692],arr[:3692]) and np.array_equal(result[:,100:],arr[:,100:])
    changed=np.any(result!=arr,axis=2)
    yy,xx=np.where(changed)
    evidence=OUT/'evidence'; evidence.mkdir(exist_ok=True); QA.mkdir(parents=True,exist_ok=True)
    archived=[]
    for src,name in [(mp,'pre-endpoint.manifest.json'),(gp,'pre-endpoint.generation.json')]:
        dst=evidence/name
        assert not dst.exists(), 'Archive exists; refusing to replace evidence.'
        shutil.copyfile(src,dst); archived.append(ref(dst))
    final=Image.fromarray(result); final.save(target)
    assert sha(old)==oldsha
    current=ref(target)
    operation=dict(kind='approved_existing_native_endpoint_registration_rectangle_merge',createdAt=now(),
        previousCandidateSha256=before,previousCandidateImageRetained=False,previousTextRecords=archived,
        source=ref(trial),sourceCropLTRB=[115,850,215,1254],destinationRectXYWH=[0,3692,100,404],
        diagnostic=ref(DIAG/'anchored-record.json'),fields=[f for f in d['files'] if Path(f['file']).name in ['anchored-mask.png','anchored-flow.npy','anchored-tone.npy']],
        maxAllowedDisplacementVector=12,actualMaxDisplacementVector=10.0,actualMaxDisplacementXY=[6.0,10.0],
        resampling='No further resampling during merge; exact crop of approved native bicubic registration trial.',
        noNewAIGeneration=True,nativeSourceScale=1,sourceUpscaling=False,oldWesternTileUnchanged=True,
        unchangedOutsideDestinationRect=True,changedPixelCount=int(changed.sum()),actualChangedBoundingBoxLTRB=[int(xx.min()),int(yy.min()),int(xx.max()+1),int(yy.max()+1)],
        geometricMask='binary; no geometry feather',flowJacobian=d['flowJacobianInAppliedRegion'])
    qa=[]
    pair=Image.new('RGB',(8192,4096)); pair.paste(Image.open(old).convert('RGB'),(0,0));pair.paste(final,(4096,0))
    def saveqa(name,im,op):
        p=QA/name; im.save(p)
        entry=dict(**ref(p),pixels=list(im.size),scale=1,actuallyViewed=False,operation=op)
        qa.append(entry)
        write(str(p)+'.generation.json',dict(**entry,createdAt=now(),derivedFrom=[ref(old),current],kind='native_pixel_QA_crop',sourceUpscaling=False))
    for label,x in [('shared',4096),('return-x100',4196),('return-x500',4596)]:
        sheet=Image.new('RGB',(1024,1280))
        sections=[]
        for n in range(4):
            box=[x-160,n*1024,x+160,(n+1)*1024]
            sheet.paste(pair.crop(box).transpose(Image.Transpose.ROTATE_90),(0,n*320))
            sections.append(dict(pairCropLTRB=box,rotateDegreesCCW=90,sheetOriginXY=[0,n*320]))
        saveqa(label+'-full.png',sheet,dict(scope='full4096px seam,320px context,original pixels',sections=sections,pairSeamX=x))
    for y in [1100,2050,3000]:
        box=[3936,y-160,4756,y+160]
        saveqa(f'repair-crossing-{y}.png',pair.crop(box),dict(pairCropLTRB=box,sharedEdgeImageX=160,returnX100ImageX=260,returnX500ImageX=660,crossingImageY=160))
    for y in [1024,2048,3072]:
        box=[3936,y-160,4756,y+160]
        saveqa(f'internal-crossing-{y}.png',pair.crop(box),dict(pairCropLTRB=box,sharedEdgeImageX=160,returnX100ImageX=260,returnX500ImageX=660,crossingImageY=160))
    im=Image.new('RGB',(1320,320)); im.paste(pair.crop((3936,0,4596,320)),(0,0)); im.paste(pair.crop((3936,3776,4596,4096)),(660,0))
    saveqa('endpoints.png',im,dict(sections=[dict(pairCropLTRB=[3936,0,4596,320],sheetOriginXY=[0,0],sharedEdgeImageX=160),dict(pairCropLTRB=[3936,3776,4596,4096],sheetOriginXY=[660,0],sharedEdgeImageX=820)]))
    saveqa('endpoint-return-region.png',pair.crop((3936,3532,4756,4096)),dict(pairCropLTRB=[3936,3532,4756,4096],sharedEdgeImageX=160,returnX100ImageX=260,returnX500ImageX=660,correctionBeginsImageY=160))
    generation=dict(**current,createdAt=now(),width=4096,height=4096,format='PNG',
        derivedFrom=[dict(file=str(target),sha256=before,historicalVersion=True,imageRetained=False,generationEvidence=archived[1]),ref(trial)],
        operation=operation,productionPixels=True,formalAccepted=False,clientVerified=False,navigationVerified=False,
        submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None,
        modelEvidence='No new generation: previous AI source model/quality records retained verbatim in evidence and source sidecars.')
    write(gp,generation)
    m.update(**current,updatedAt=now(),endpointCorrection=operation,qa=qa,formalAccepted=False,clientVerified=False,navigationVerified=False,status='endpoint_correction_merged_pending_scoped_native_QA')
    write(mp,m)
    write(QA/'review.json',dict(createdAt=now(),source=current,westSource=ref(old),scope='West shared edge; new tile x100 and x500 return edges; repair crossings1100/2050/3000; internal crossings1024/2048/3072; endpoints.',result='pending',scopedLocalSeamsPassed=False,formalAccepted=False,clientVerified=False,navigationVerified=False,qa=qa))
    print(json.dumps(dict(output=current,changedPixelCount=operation['changedPixelCount'],changedBoundingBox=operation['actualChangedBoundingBoxLTRB'],qaCount=len(qa)),ensure_ascii=False))

if __name__=='__main__': main()
