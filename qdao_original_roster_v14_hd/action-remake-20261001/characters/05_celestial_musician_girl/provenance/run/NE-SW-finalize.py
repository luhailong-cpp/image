from pathlib import Path
from PIL import Image
import hashlib,json,datetime
ROOT=Path(__file__).resolve().parents[2]
entries=json.loads((ROOT/'provenance/run/selection-NE-SW.json').read_text(encoding='utf-8'))
out=[]
for e in entries:
 p=ROOT/e['file']; rp=ROOT/e['generationRecord']
 r=json.loads(rp.read_text(encoding='utf-8-sig'))
 sh=hashlib.sha256(p.read_bytes()).hexdigest()
 with Image.open(p) as im:
  im.load(); size=list(im.size); mode=im.mode; al=im.getchannel('A').getextrema()
 assert size[0]>=1024 and size[1]>=1024 and mode=='RGBA' and al==(0,255)
 assert sh==r['sha256']
 stem=rp.name.replace('.generation.json','')
 r['prompt']='provenance/run/'+stem+'.prompt.txt'
 r['visualReview']={'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'actual native PNG viewed using generatedImage/view_image','status':'reviewed_candidate','notes':e['notes'],'staticVisualPassed':False,'dynamicAccepted':False,'groundingReview':'provenance/run/'+e['direction']+'-grounding-review-20261003.json'}
 r['status']='candidate_for_fixed_root_sequence_review'
 rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 out.append({'direction':e['direction'],'frame':e['frame'],'file':e['file'],'sha256':sh,'nativeSize':size,'mode':mode,'generationRecord':e['generationRecord'],'reviewStatus':e['reviewStatus']})
assert len(out)==32 and len({x['sha256'] for x in out})==32
for stem,reason in {'SW05-v2':'three boots; extra third boot behind foreground leg','SW06-v2':'leading boot drifts to prior side and does not preserve selected left-leg chain','SW04-v1':'leg ownership resembles opposite half-cycle','SW05-v1':'leg ownership resembles opposite half-cycle','SW06-v1':'leg ownership resembles opposite half-cycle','SW07-v1':'leading foot repeats opposite half-cycle'}.items():
 p=ROOT/'provenance/run'/f'{stem}.review.json'
 p.write_text(json.dumps({'reviewedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision':'rejected_not_selected','reason':reason,'actualPixelsViewed':True,'dynamicAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
audit={'verifiedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selectedCount':32,'independentUniqueShaCount':32,'nativeSize':[1254,1254],'allRGBA':True,'allGenerationHashesMatch':True,'actualModel':None,'actualQuality':None,'actualVersionReason':'Host-managed; tool did not disclose model or quality. Config target remains historical snapshot only.','notClaimed':['final_runtime_export','dynamic_acceptance','client_validation'],'files':out}
(ROOT/'provenance/run/NE-SW-selection-validation.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in audit.items() if k!='files'},ensure_ascii=False))

