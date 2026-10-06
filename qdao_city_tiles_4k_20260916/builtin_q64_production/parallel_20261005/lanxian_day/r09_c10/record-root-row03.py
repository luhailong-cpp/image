from pathlib import Path
from datetime import datetime,timezone
import hashlib,json

tile=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
observations={
 'r03_c01':'Actually viewed guide, approved style, top neighbor and native tool output. Original blank red/gold post, layered base, shrub, curb and groove preserved; no obvious truncation or new object in the whole native view. Final seam review remains required.',
 'r03_c02':'Attempt01 rejected because full north-context image induced added crossed grooves in blank upper-center paving. Selected retry used guide+style only; actually viewed native output, unbroken blank area restored, original post/stone pillar/shrub/curb retained, guide gold color-band and white curb scuff removed. Rejected receipt kept.',
 'r03_c03':'Actually viewed guide/top neighbor/style and native output. Original bridge rail aperture, pillars, arch curvature and radial masonry joints retained. Broad gray material cleaned. No new plant/object/opening or obvious contour truncation in whole native view; full seam QA remains required.',
 'r03_c04':'Actually viewed guide/top neighbor/style and native output. Arch, original recessed support, dark inner stone, water boundary and clipped leaves retained. No new opening or decorative water marks; original material planes retained. Full seam QA remains required.'}
items=[]
for cell,note in observations.items():
    p=tile/'native'/f'{cell}.png';rp=Path(str(p)+'.generation.json');j=json.loads(rp.read_text(encoding='utf-8'))
    assert sha(p)==j['sha256']
    receipt=tile/'jobs'/f'{cell}.receipt.json';rc=json.loads(receipt.read_text(encoding='utf-8'))
    assert rc['prompt']==j['submittedParameters']['prompt']
    assert [x['path'] for x in rc['references']]==j['submittedParameters']['referenced_image_paths']
    for ref in j['references']:assert sha(Path(ref['path']))==ref['sha256']
    assert j['actualModel'] is None and j['actualQuality'] is None
    items.append({'cell':cell,'file':str(p),'sha256':sha(p),'generationRecord':str(rp),
                  'generationRecordSha256':sha(rp),'actualReceipt':str(receipt),'receiptSha256':sha(receipt),
                  'sourceAndReferenceHashesVerified':True,'actualNativeOutputViewed':True,'observation':note})
out={'schemaVersion':1,'writtenAtUtc':datetime.now(timezone.utc).isoformat(),'worker':'root','row':3,
     'completedNativeCount':4,'requiredNativeCount':4,'formalAccepted':False,'clientValidated':False,
     'wholeCityComplete':False,'allNativeSourcesActuallyViewed':True,
     'nativeGenerationRoute':'builtin image_gen','actualModel':None,'actualQuality':None,
     'modelEvidenceNote':'Tool exposes no model/quality selectors; config target is not an actual-returned model claim.',
     'rejectedAttemptCount':1,'rejectedReceipt':str(tile/'jobs/r03_c02.attempt01.receipt.json'),
     'seamValidation':'Pending full assembled tile QA; whole-image views alone do not establish edge continuity.','cells':items}
(tile/'worker-row03.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'row':3,'complete':4,'recordSha256':sha(tile/'worker-row03.json')}))
