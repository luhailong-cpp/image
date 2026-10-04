from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib
BASE=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
review={'recordedAt':datetime.now(timezone.utc).isoformat(),'scope':'This subtask: W01-06 and targeted corrections E01/E03','staticReview':'All eight returned native images viewed; W six-frame contact and cleaned W06 viewed at 1024. Full reaction phases visibly distinct; no duplicate image, mirror or synthesis.','dynamicReview':{'status':'not_browser_verified','reason':'CUA createBrowserTab(iab) returned Browser is not available: iab; cua.listBrowsers returned []','normalGif':'preview/hit-W-normal.gif','slowGif':'preview/hit-W-slow.gif','interactivePreview':'preview/hit-W.html','normalMsPerFrame':40,'segmentMs':240},'observations':['W01 surprise, W02 increasing lean, W03 peak recoil, W04 knee compression, W05 rising, W06 recovered. Both hands/fox/crystal stay readable.','W planted-foot locations drift slightly during independently drawn phases; no per-frame coordinate normalization was applied.','Small hair/fur/crystal-detail changes remain at enlarged size.','E03 far-side ornament reduced substantially; torso still has slight rotation during recoil and needs combined E-sequence judgement.','Edge cleanup is restricted to highly saturated blue/magenta within the alpha boundary band; no alpha reshaping before uniform resize.'],'clientIntegrated':False,'files':[]}
for direction,nums in [('W',range(1,7)),('E',[1,3])]:
    for n in nums:
        p=BASE/'hit'/direction/f'{n:02}.png'; recpath=Path(str(p)+'.generation.json')
        r=json.loads(recpath.read_text(encoding='utf-8'))
        im=Image.open(p)
        assert im.size==(1024,1024) and im.mode=='RGBA'
        assert sha(p)==r['sha256']
        if direction=='E':
            request=json.loads((BASE/r['evidence']['request']).read_text(encoding='utf-8'))
            old=Path(request['editTarget']); oldrecord=Path(request['oldGenerationRecord'])
            r['editedFrom']={'path':old.as_posix(),'sha256':sha(old),'generationRecord':oldrecord.as_posix(),'generationRecordSHA256':sha(oldrecord),'oldRecordPreservedUnchanged':True}
            recpath.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
            (BASE/'provenance'/Path(r['prompt']).with_suffix('.generation.json').name).write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
        review['files'].append({'path':p.relative_to(BASE).as_posix(),'sha256':sha(p),'nativeSize':r['nativeSize'],'pngSize':[1024,1024],'mode':'RGBA','generationRecord':recpath.relative_to(BASE).as_posix(),'fullyVisualApproved':False})
assert len({f['sha256'] for f in review['files']})==8
(BASE/'hit/review-subtask.json').write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding='utf-8')
print('Verified 8 distinct RGBA exports, provenance SHA links and old E source evidence.')
