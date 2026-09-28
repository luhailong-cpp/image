import argparse,json,hashlib,datetime,struct,re
from pathlib import Path
from PIL import Image
ap=argparse.ArgumentParser(description='Archive a builtin tool return; no image generation or resizing.')
ap.add_argument('--run',required=True);ap.add_argument('--name',required=True);ap.add_argument('--request',required=True);ap.add_argument('--source',required=True)
a=ap.parse_args();run=Path(a.run);base=run/'repairs'/a.name
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
reqp=run/'requests'/a.request;req=json.loads(reqp.read_text(encoding='utf-8-sig'))
receipt=base.with_suffix('.tool-response.json');resp=json.loads(receipt.read_text(encoding='utf-8-sig'))
refp=run/'requests'/(a.request.replace('.request.json','.references.json'))
refs=json.loads(refp.read_text(encoding='utf-8-sig'))
for x in refs:
 p=Path(x['path']);assert sha(p)==x['sha256'],f'Reference changed: {p}'
source=Path(a.source);data=source.read_bytes();target=base.with_suffix('.native.png')
with target.open('xb') as f:f.write(data)
with Image.open(target) as im:
 im.load();pixels=[im.width,im.height];fmt=im.format;mode=im.mode
obs=[];off=8
if data[:8]==b'\x89PNG\r\n\x1a\n':
 while off+12<=len(data):
  n=struct.unpack('>I',data[off:off+4])[0];kind=data[off+4:off+8];chunk=data[off+8:off+8+n]
  if kind in (b'caBX',b'tEXt',b'iTXt',b'zTXt'):
   for match in re.finditer(rb'[\x20-\x7e]{6,}',chunk):
    t=match.group().decode('ascii')
    if any(k in t.lower() for k in ['openai','gpt','c2pa','softwareagent','claim_generator','resiz']):
     obs.append({'chunk':kind.decode(),'readableString':t[:512]})
  off+=n+12
  if kind==b'IEND':break
payload=req['payload']
record={'schemaVersion':1,'file':str(target),'sha256':sha(target),'width':pixels[0],'height':pixels[1],'format':fmt,'mode':mode,'generatedAt':None,'hostObservedStartedAtUtc':resp['hostObservedStartedAtUtc'],'hostObservedFinishedAtUtc':resp['hostObservedFinishedAtUtc'],'recordedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','configSnapshot':json.loads((run/'config.snapshot.json').read_text(encoding='utf-8-sig')),'configSnapshotSha256':sha(run/'config.snapshot.json'),'submittedParameters':{'model':None,'quality':None,'size':None},'actualPayloadFile':str(reqp),'actualPayloadSha256':sha(reqp),'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed builtin route; tool returned no model, quality, native-generation size field or server generation time. Dimensions below are decoded raw tool-return file dimensions, with no local resizing.','references':refs,'evidence':{'toolResponse':str(receipt),'toolResponseSha256':sha(receipt),'hostSavedOriginal':str(source),'hostSavedOriginalSha256':sha(source),'byteIdenticalCopy':data==target.read_bytes(),'metadataAsciiObservations':obs,'c2paSignatureVerified':False},'editSourceCandidateSha256':req.get('sourceCandidateSha256'),'sourceCropLTRB':req.get('cropLTRB'),'rawReturnedPixels':pixels,'requestedPixels':req['desiredNativePixels'],'requestedSizeMatched':pixels==req['desiredNativePixels'],'localResizingPerformed':False,'formalAccepted':False}
rp=target.with_name(target.name+'.generation.json')
with rp.open('x',encoding='utf-8') as f:json.dump(record,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'file':str(target),'sha256':sha(target),'pixels':pixels,'generation':str(rp),'requestedSizeMatched':record['requestedSizeMatched']},ensure_ascii=False))

