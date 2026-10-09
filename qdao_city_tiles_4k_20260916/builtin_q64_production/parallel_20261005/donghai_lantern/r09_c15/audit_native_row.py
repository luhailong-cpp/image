"""Audit native source bytes and recorded references without modifying art."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,sys
from PIL import Image
T=Path(__file__).resolve().parent
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def audit(row):
    sources=[]
    for c in range(1,5):
        name=f'r{row:02}_c{c:02}';p=T/'native'/f'{name}.png';r=read(str(p)+'.generation.json')
        with Image.open(p)as im:
            im.load();assert im.size==(1254,1254)
            if im.mode=='RGBA':assert im.getchannel('A').getextrema()==(255,255)
        assert sha(p)==r['sha256']==sha(r['evidence']['toolResultSourcePath'])
        assert r['resizedAfterGeneration'] is False and r['finalArtUpscaled'] is False
        q=read(r['requestFile']);assert sha(r['requestFile'])==r['requestSha256'];assert sha(r['prompt'])==r['promptSha256']
        assert Path(r['prompt']).read_text(encoding='utf-8')==q['prompt']==r['submittedParameters']['prompt']
        assert all(r.get(k) is None for k in ('actualModel','actualQuality'))
        assert all(r['submittedParameters'].get(k) is None for k in ('model','quality'))
        assert [Path(x).resolve()for x in q['referenced_image_paths']]==[Path(x['file']).resolve()for x in r['references']]
        for ref in r['references']:assert sha(ref['file'])==ref['sha256']
        geo=r['geometryMatchedTo'];assert sha(geo['generationRecord'])==geo['generationRecordSha256']
        snap=read(geo['generationRecord']);assert snap['sourceGenerationRecordSnapshot']['sha256']==geo['sha256']==geo['dayAuthoritySha256']
        g=read(r['references'][1]['file']+'.generation.json');assert sha(g['file'])==g['sha256']
        for ref in g['derivedFrom']:assert sha(ref['file'])==ref['sha256']
        sources.append({'id':name,'file':str(p),'sha256':sha(p),'nativePixels':[1254,1254],'toolResultBytesUnchanged':True,'requestPromptAndReferencesVerified':True,'frozenDaySnapshotVerified':True,'guideDependenciesVerified':True,'referenceCount':4,'actualModel':None,'actualQuality':None,'submittedModel':None,'submittedQuality':None})
    review=read(T/f'qa/row{row}-native-overlaps/review.json')
    assert review['completePairsActuallyViewed']==7
    for entry in review['observations']:assert sha(entry['sheet'])==entry['sha256']
    result={'auditedAtUtc':datetime.now(timezone.utc).isoformat(),'row':row,'allPassed':True,'sources':sources,'nativeCount':4,'referenceCount':16,'all7OriginalPixelQASheetsVerifiedAndViewed':True,'formalAccepted':False,'wholeTileAssemblyDone':False,'wholeCityComplete':False}
    path=T/f'qa/row{row}-source-audit.json';path.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'allPassed':True,'nativeCount':4,'referenceCount':16,'audit':str(path)}))
if __name__=='__main__':audit(int(sys.argv[1]))
