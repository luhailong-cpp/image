from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,re,shutil,sys
import numpy as np
from PIL import Image
P=Path(__file__).resolve().parent; ART=next(p for p in P.parents if (p/'config/image-generation.json').exists())
PROD=P.parents[1];OLD=PROD/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'; V5=P/'external-v5'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,x):
    with Path(p).open('x',encoding='utf-8') as f:json.dump(x,f,ensure_ascii=False,indent=2)
def load(p):
    with Image.open(p) as im:return np.array(im.convert('RGB'))
def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)
def prepare():
    core_path=V5/'output/r09_c10.png';core=load(core_path)
    left_path=P.parent/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png';bottom_path=OLD/'r10_c10.png'
    left=load(left_path);bottom=load(bottom_path)
    yy,xx=np.mgrid[:1254,:1254].astype(np.float32)
    for name in ['bottom-double-line','left-border-step']:
        q=P/'repairs/external-prepared'/name;assert not q.exists();q.mkdir(parents=True)
        if name=='bottom-double-line':
            box=[797,3469,2051,4723];context=np.concatenate([core[3469:,797:2051],bottom[:627,797:2051]],axis=0)
            alpha=smooth((1-((xx-665)/360)**2-((yy-485)/220)**2)/.40)*smooth((626-yy)/30)
            fixed=yy>=627;neighbor=bottom_path
        else:
            box=[-512,853,742,2107];context=np.concatenate([left[853:2107,-512:],core[853:2107,:742]],axis=1)
            alpha=smooth((1-((xx-645)/230)**2-((yy-627)/300)**2)/.40)*smooth((xx-512)/45)
            fixed=xx<512;neighbor=left_path
        mask=np.rint(alpha*255).astype(np.uint8);mask[fixed]=0
        assert context.shape==(1254,1254,3) and not np.any(mask[fixed])
        Image.fromarray(context).save(q/'context-native-1254.png');Image.fromarray(mask).save(q/'mask.png')
        rec={'id':name,'source':{'file':str(core_path),'sha256':sha(core_path)},'sourceRecord':{'file':str(V5/'assembly.json'),'sha256':sha(V5/'assembly.json')},'neighbor':{'file':str(neighbor),'sha256':sha(neighbor)},'worldBoxLTRB':box,'context':{'file':str(q/'context-native-1254.png'),'sha256':sha(q/'context-native-1254.png')},'mask':{'file':str(q/'mask.png'),'sha256':sha(q/'mask.png')},'nativePixels':[1254,1254],'resized':False,'fixedNeighborMaskPixelsAllZero':True,'actualModel':None,'actualQuality':None,'backendModelVerified':False,'configSnapshot':read(ART/'config/image-generation.json')}
        write(q/'prepared.json',rec)
    write(V5/'visual-review.json',{'candidate':{'file':str(core_path),'sha256':sha(core_path)},'reviewedAtUtc':datetime.now(timezone.utc).isoformat(),'reviewMethod':'All full left/bottom boundaries, both treatment returns and true four-core corner viewed at original pixels, plus focused 800-square crops','internalRepairReviewPassed':True,'externalVisualReviewPassed':False,'fourTileJunctionLocalReviewPassed':True,'failedChecks':[{'name':'bottom diagonal brick outline','candidateApproximateBox':[1320,3970,1640,4080],'issue':'Halo-induced tapered duplicate bevel line and fading original edge'},{'name':'left inset-ring border','candidateApproximateBox':[80,1430,180,1530],'issue':'Small stair-step in dark diagonal bevel edge'}],'productionAccepted':False,'scopedLocalContinuityPassed':False})
def apply(name,version,basefile,baserecord):
    prep=P/'repairs/external-prepared'/name;r=read(prep/'prepared.json');receipt=read(prep/'request-receipt.json')
    for key in ['source','sourceRecord','neighbor','context','mask']:assert sha(r[key]['file'])==r[key]['sha256']
    match=re.search(r' as (.+?\.png) by default\.',receipt['response']['output_hint'],re.S);assert match
    raw=Path(match.group(1));native=load(raw);assert native.shape==(1254,1254,3)
    context=load(r['context']['file']);mask=np.array(Image.open(r['mask']['file']))
    sys.path.insert(0,str(P.parent/'tools/vendor'));sys.dont_write_bytecode=True
    hp=PROD/'tools/mechanical_join.py';spec=importlib.util.spec_from_file_location('external_repair_join',hp);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    result,flow,correction,registration=m.registered_join(context,native,mask,max_shift=8.,match_tone=True)
    original=load(basefile);after=original.copy();x0,y0,x1,y1=r['worldBoxLTRB']
    gx0=max(x0,0);gy0=max(y0,0);gx1=min(x1,4096);gy1=min(y1,4096);lx0=gx0-x0;ly0=gy0-y0;lx1=gx1-x0;ly1=gy1-y0
    assert np.array_equal(original[gy0:gy1,gx0:gx1],context[ly0:ly1,lx0:lx1])
    after[gy0:gy1,gx0:gx1]=result[ly0:ly1,lx0:lx1]
    allowed=np.zeros((4096,4096),dtype=bool);allowed[gy0:gy1,gx0:gx1]=mask[ly0:ly1,lx0:lx1]>0
    assert not np.any(np.any(after!=original,axis=2)&~allowed)
    assert np.array_equal(result[mask==0],context[mask==0])
    q=P/'repairs/versions'/version;assert not q.exists();q.mkdir(parents=True)
    for src,n in [(raw,'repair-native-1254.png'),(prep/'request-receipt.json','request-receipt.json'),(prep/'context-native-1254.png','context-before.png'),(prep/'mask.png','mask.png')]:shutil.copyfile(src,q/n);assert sha(src)==sha(q/n)
    Image.fromarray(after).save(q/'r09_c10.png');Image.fromarray(result).save(q/'context-after.png')
    np.savez_compressed(q/'flow.npz',flow=flow);np.savez_compressed(q/'correction.npz',correction=correction)
    (q/'actual-prompt.txt').write_text(receipt['request']['prompt'],encoding='utf-8')
    assert sha(r['neighbor']['file'])==r['neighbor']['sha256']
    references=[{'file':p,'sha256':sha(p),'role':'edit target native true-core context' if i==0 else 'confirmed designs main drawing/material style, no UI content'} for i,p in enumerate(receipt['request']['referenced_image_paths'])]
    gen={'file':'repair-native-1254.png','sha256':sha(q/'repair-native-1254.png'),'generatedAt':receipt['completedAtUtc'],'width':1254,'height':1254,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','configSnapshot':r['configSnapshot'],'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Host-managed tool has no model/quality selector and disclosed no verified model/quality metadata','prompt':{'file':str(q/'actual-prompt.txt'),'sha256':sha(q/'actual-prompt.txt')},'references':references,'evidence':{'file':str(q/'request-receipt.json'),'sha256':sha(q/'request-receipt.json')},'originalNativeOutput':{'file':str(raw),'sha256':sha(raw)}}
    write(q/'repair-native-1254.png.generation.json',gen)
    record={'schemaVersion':1,'status':'native_external_repair_candidate_pending_visual_QA','candidate':{'file':str(q/'r09_c10.png'),'sha256':sha(q/'r09_c10.png')},'sourceCandidate':{'file':str(basefile),'sha256':sha(basefile)},'sourceRecord':{'file':str(baserecord),'sha256':sha(baserecord)},'prepared':{'file':str(prep/'prepared.json'),'sha256':sha(prep/'prepared.json')},'originalNativeOutput':gen['originalNativeOutput'],'actualNativePixels':[1254,1254],'generationRecord':{'file':str(q/'repair-native-1254.png.generation.json'),'sha256':sha(q/'repair-native-1254.png.generation.json')},'worldBoxLTRB':r['worldBoxLTRB'],'appliedCandidateBoxLTRB':[gx0,gy0,gx1,gy1],'registration':registration,'outsideAllowedMaskPixelsUnchanged':True,'neighborCoreUnchanged':True,'sourceFileUnchanged':True,'nativeArtEnlarged':False,'actualModel':None,'actualQuality':None,'backendModelVerified':False,'changedPixels':int(np.any(after!=original,axis=2).sum()),'productionAccepted':False,'visualAcceptancePassed':False,'script':{'file':str(Path(__file__).resolve()),'sha256':sha(__file__)},'helper':{'file':str(hp),'sha256':sha(hp)}}
    write(q/'repair.json',record);print(json.dumps(record,indent=2))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode');ap.add_argument('--name');ap.add_argument('--version');ap.add_argument('--basefile');ap.add_argument('--baserecord');a=ap.parse_args()
    if a.mode=='prepare':prepare()
    else:apply(a.name,a.version,Path(a.basefile),Path(a.baserecord))
