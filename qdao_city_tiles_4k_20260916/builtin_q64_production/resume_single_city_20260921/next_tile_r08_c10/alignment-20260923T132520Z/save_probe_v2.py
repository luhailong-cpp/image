"""Save one returned native image unchanged; prepare exact-coordinate QA only."""
from pathlib import Path
from datetime import datetime,timezone
from io import BytesIO
import json,re,hashlib
from PIL import Image
D=Path(__file__).resolve().parent;P=D.parent;B=D/'probe-aligned-halo-v2'
def sha(b):return hashlib.sha256(b).hexdigest()
def rec(p):return {'file':str(p),'sha256':sha(p.read_bytes())}
def dump(p,o):
 with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(o,f,ensure_ascii=False,indent=2);f.write('\n')
pre=json.loads((B/'preflight.json').read_text(encoding='utf-8'))
receipt=json.loads((B/'tool-receipt.json').read_text(encoding='utf-8'))
for ref in pre['references']:assert rec(Path(ref['file']))['sha256']==ref['sha256']
source=Path(re.search(r' as (.+?\.png) by default\.',receipt['rawTextReturn']['output_hint']).group(1))
raw=source.read_bytes();im=Image.open(BytesIO(raw));im.load()
out=B/'native-r04_c02.png'
with out.open('xb') as f:f.write(raw)
assert out.read_bytes()==raw
generation={'schemaVersion':1,'tile':'r08_c10','patch':'r04_c02','role':'unselected_native_probe_not4k_candidate',**rec(out),'nativePixels':list(im.size),'format':im.format,'mode':im.mode,'nativeSizeMatchesRequested':im.size==(1254,1254),'resampled':False,'pixelEdited':False,
 'generatedAt':receipt['after']['current_time'],'generatedAtEvidence':'observed completion clock UTC, not provider timestamp','clockBefore':receipt['before'],'clockAfter':receipt['after'],
 'tool':'image_gen.imagegen','route':'builtin_host_managed','currentExperimentCalls':1,
 'configSnapshot':pre['configSnapshot'],'configFile':pre['configFile'],'actualRequest':pre['actualRequest'],'prompt':pre['prompt'],'references':pre['references'],
 'submittedParameters':{'model':None,'quality':None},'actualModel':None,'actualQuality':None,'backendModelVerified':False,'unverifiedReason':'Callable input has no model/quality fields; result only exposes image_url and output_hint.',
 'evidence':{'preflight':rec(B/'preflight.json'),'receipt':rec(B/'tool-receipt.json'),'staticReview':pre['staticReview'],'registeredGuideRecord':pre['registeredGuideRecord']},
 'hostReturnedFile':{**rec(source),'bytes':len(raw)},'imageReturnDataUri':{'field':'image_url','payloadRetainedAsHostPNG':str(out),'pngSha256':sha(raw)},
 'futureSelectedCoreLTRB':[115,115,1139,1139],'coreSelectionPermittedOnlyAfterVisualReview':True,'guidePixelsUsedInSavedOutput':False,
 'selected':False,'formalArtAcceptancePassed':False,'clientRuntimeAccepted':False,'wholeTileReady':False}
dump(B/'native-r04_c02.png.generation.json',generation)
qa=B/'qa';qa.mkdir(exist_ok=False);entries=[]
if im.size==(1254,1254):
 neighborpath=P/'references/r04_c02.bottom-neighbor-native-context.png';neighborraw=neighborpath.read_bytes();assert sha(neighborraw)==pre['references'][3]['sha256']
 neighbor=Image.open(BytesIO(neighborraw)).convert('RGB')
 specs=[('halo-comparison-generated-top-neighbor-bottom.png',230,[(im,(0,1139,1254,1254),0),(neighbor,(0,0,1254,115),115)],'Same global area twice: generated bottom115 above native lower-neighbor top115; not real assembly.'),
 ('hypothetical-core-to-bottom-seam-native.png',256,[(im,(0,1011,1254,1139),0),(neighbor,(0,0,1254,128),128)],'New native core last128 above selected lower-neighbor first128; actual contact at review y128.'),
 ('generated-y1139-context-native.png',371,[(im,(0,883,1254,1254),0)],'Generated target rows883:1254 at native pixels; conceptual boundary at review y256, no line overlaid.')]
 for name,height,parts,operation in specs:
  image=Image.new('RGB',(1254,height))
  for src,box,y in parts:image.paste(src.crop(box).convert('RGB'),(0,y))
  path=qa/name
  with path.open('xb') as f:image.save(f,format='PNG')
  entries.append({'image':rec(path),'operation':operation,'sources':[rec(out),rec(neighborpath)],'notArtwork':True,'resampled':False})
 dump(qa/'derived-review-images.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'entries':entries,'role':'current_native_qa_only'})
print(json.dumps({'output':rec(out),'pixels':list(im.size),'qaImages':len(entries),'generationRecord':rec(B/'native-r04_c02.png.generation.json')},ensure_ascii=False,indent=2))
