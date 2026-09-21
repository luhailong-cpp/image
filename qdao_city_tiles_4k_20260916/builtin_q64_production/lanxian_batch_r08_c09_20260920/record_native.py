from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,shutil,sys
from PIL import Image
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
j=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8-sig'))
src=Path(j['source']);out=Path(j['output']);prompt=Path(j['promptFile']);assert not out.exists(),out
with Image.open(src) as im:
    assert im.size==(1254,1254),im.size
    assert im.convert('RGBA').getchannel('A').getextrema()==(255,255)
out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out);assert sha(src)==sha(out)
refs=[{'order':i+1,'path':p,'sha256':sha(p)} for i,p in enumerate(j['refs'])]
rec={'schemaVersion':1,'id':j['id'],'role':j['role'],'route':'builtin_image_gen','createdAtUtc':datetime.now(timezone.utc).isoformat(),'configuredProduct':'ChatGPT Images 2.5','configuredModelTarget':'gpt-image-2.5-sunburst','configuredQualityTarget':'max','backendModelVerified':False,'actualBackendModel':None,'actualQualityPreset':None,'actualNativePixels':[1254,1254],'nativePixels':[1254,1254],'opaque':True,'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':str(out),'outputSha256':sha(out),'sourceBytesPreserved':True,'promptFile':str(prompt),'promptSha256':sha(prompt),'promptText':prompt.read_text(encoding='utf-8-sig').rstrip(),'submittedImages':refs,'actualInputCount':len(refs),'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':j['refs'],'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'guidePath':j['refs'][0],'guideSha256':refs[0]['sha256'],'finalArtUpscaled':False,'resizedAfterGeneration':False,'separateBilledApiAuthorized':False,'toolOutputReceipt':j.get('receipt',{})}
out.with_suffix('.record.json').write_text(json.dumps(rec,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
B=Path(__file__).parent;P=B.parent;checkpoint_dir=B/'checkpoints';checkpoint_dir.mkdir(exist_ok=True)
snapshot={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'lastRecord':str(out.with_suffix('.record.json')),'lastOutputSha256':sha(out),'route':'builtin_image_gen','dayDetailRecords':[str(p) for p in sorted((P/'lanxian_day/r08_c09/native').glob('*.record.json'))],'springDetailRecords':[str(p) for p in sorted((P/'lanxian_spring/r08_c09/native').glob('*.record.json'))],'regionalRecords':[str(p) for p in sorted((P/'lanxian_day/r08_c09/regional-reference').glob('*.record.json'))],'rootLedgerMutated':False,'runtimePublished':False}
cf=checkpoint_dir/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json');cf.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(B/'checkpoint-latest.json').write_text(json.dumps({'checkpoint':str(cf),'sha256':sha(cf),'dayCount':len(snapshot['dayDetailRecords']),'springCount':len(snapshot['springDetailRecords']),'regionalCount':len(snapshot['regionalRecords'])},indent=2)+'\n',encoding='utf-8')
print(json.dumps({'output':str(out),'sha256':rec['outputSha256'],'nativeSize':[1254,1254]}))
