"""Preserve returned PNG bytes and make inspection-only crops, never art edits."""
from pathlib import Path
from datetime import datetime,timezone
from io import BytesIO
import json,hashlib,re
from PIL import Image

P=Path(__file__).resolve().parent
B=P/'probe-r04_c02-20260923T125732Z'
def sha(raw):return hashlib.sha256(raw).hexdigest()
def rec(p):return {'file':str(p),'sha256':sha(p.read_bytes())}
def dump(p,o):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
receipt=json.loads((B/'tool-receipt.json').read_text(encoding='utf-8'))
preflight=json.loads((B/'preflight.json').read_text(encoding='utf-8'))
source=Path(re.search(r' as (.+?\.png) by default\.',receipt['rawTextReturn']['output_hint']).group(1))
raw=source.read_bytes(); im=Image.open(BytesIO(raw));im.load()
out=P/'native/r04_c02.probe-20260923T125732Z.png'
with out.open('xb') as f:f.write(raw)
assert out.read_bytes()==raw
bottom=P/'references/r04_c02.bottom-neighbor-native-context.png'
bottomraw=bottom.read_bytes()
assert sha(bottomraw)==preflight['references'][3]['sha256']
neighbor=Image.open(BytesIO(bottomraw));neighbor.load()
output={**rec(out),'pixels':list(im.size),'format':im.format,'mode':im.mode,'nativeSizeMatchesRequested':im.size==(1254,1254),'resampled':False,'pixelEdited':False}
generation={
  'schemaVersion':1,'tile':'r08_c10','patch':'r04_c02','role':'native_probe_not_4k_candidate',
  **output,'generatedAt':receipt['after']['current_time'],'generationTimeKind':'observed tool completion UTC, not provider timestamp',
  'tool':'image_gen.imagegen','route':'builtin_host_managed','toolCallCount':1,
  'configSnapshot':preflight['configSnapshot'],'configSnapshotFile':preflight['configFile'],
  'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,
  'unverifiedReason':'Tool returned image_url and output_hint only, without concrete model or quality evidence.',
  'actualRequest':preflight['request'],'prompt':preflight['prompt'],'references':preflight['references'],
  'evidence':{'toolReceipt':rec(B/'tool-receipt.json'),'preflight':rec(B/'preflight.json'),'rootLayoutObservation':preflight['rootLayoutObservation'],'clockBefore':receipt['before'],'clockAfter':receipt['after']},
  'hostReturnedFile':{'file':str(source),'sha256':sha(raw),'bytes':len(raw)},
  'imageReturnDataUri':{'receiptField':'image_url','payloadStoredAs':str(out),'payloadSha256':sha(raw),'note':'Exact host PNG bytes retained; data URI text not duplicated.'},
  'sourceRetention':'workspace native probe is current in-progress only source; host duplicate pending normal selected-source cleanup decision',
  'wholeTileReady':False,'formalArtAcceptancePassed':False,'clientRuntimeAccepted':False,
  'localReview':'pending visual inspection'
}
dump(Path(str(out)+'.generation.json'),generation)
qa=B/'qa';qa.mkdir(exist_ok=False)
qaentries=[]
if im.size==(1254,1254):
    # Comparison shows the same expected world area twice. It is not artwork.
    pair=Image.new('RGB',(1254,230))
    pair.paste(im.crop((0,1139,1254,1254)).convert('RGB'),(0,0))
    pair.paste(neighbor.crop((0,0,1254,115)).convert('RGB'),(0,115))
    q=qa/'halo-comparison-generated-top-neighbor-bottom.png';pair.save(q)
    qaentries.append({'image':rec(q),'operation':'generated y1139:1254 stacked above neighbor y0:115; same expected world area, native pixels','sources':[rec(out),rec(bottom)],'notArtwork':True})
    # Candidate core meets the selected lower tile at the center of this image.
    seam=Image.new('RGB',(1254,256))
    seam.paste(im.crop((0,1011,1254,1139)).convert('RGB'),(0,0))
    seam.paste(neighbor.crop((0,0,1254,128)).convert('RGB'),(0,128))
    q=qa/'hypothetical-core-to-bottom-seam-native.png';seam.save(q)
    qaentries.append({'image':rec(q),'operation':'generated last 128 core rows y1011:1139 above neighbor first128; hypothetical seam at review y128','sources':[rec(out),rec(bottom)],'notArtwork':True})
    q=qa/'generated-y1139-context-native.png';im.crop((0,1011,1254,1254)).save(q)
    qaentries.append({'image':rec(q),'operation':'unmodified generated rows1011:1254, expected tile boundary at review y128; no overlay line drawn','sources':[rec(out)],'notArtwork':True})
dump(qa/'derived-review-images.json',{'madeAtUtc':datetime.now(timezone.utc).isoformat(),'entries':qaentries,'allImagesReviewOnly':True})
print(json.dumps({'output':output,'generationRecord':rec(Path(str(out)+'.generation.json')),'qaImages':len(qaentries)},ensure_ascii=False,indent=2))
