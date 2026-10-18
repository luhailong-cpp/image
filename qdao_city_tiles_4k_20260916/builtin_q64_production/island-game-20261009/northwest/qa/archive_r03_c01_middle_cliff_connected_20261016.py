from pathlib import Path
import json,hashlib,shutil,sys
from datetime import datetime,timezone
from PIL import Image
Z=Path(__file__).resolve().parents[1]
stem=sys.argv[1];src=Path(sys.argv[2]);assert stem=='r03_c01_middle_cliff_connected_20261016_a01'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
dst=Z/'native'/f'{stem}.png';assert not dst.exists();shutil.copyfile(src,dst)
w,h=Image.open(dst).size;inp=json.loads((Z/'guides'/f'{stem}.input.json').read_text())
pp=Z/'prompts'/f'{stem}.prompt.txt';refs=inp['inputs'];when=datetime.now(timezone.utc).isoformat()
receipt=Z/'receipts'/f'{stem}.receipt.json'
rc={'tool':'image_gen.imagegen','route':'builtin','generatedFile':src.as_posix(),'archivedAtUtc':when,'submitted':{'promptText':pp.read_text(),'promptFile':pp.as_posix(),'referenced_image_paths':[e['path'] for e in refs],'transparent_background':False},'actualModel':None,'actualQuality':None,'recoveredSourceSha256':sha(src)}
receipt.write_text(json.dumps(rc,ensure_ascii=False,indent=2))
g=dict(file=dst.as_posix(),sha256=sha(dst),generatedAt=when,nativeWidth=w,nativeHeight=h,format='PNG',sourceOutputPath=src.as_posix(),sourceOutputSha256=sha(src),tool='image_gen.imagegen',route='builtin',configSnapshot=None,submittedParameters=dict(model=None,quality=None,transparent_background=False),actualModel=None,actualQuality=None,unverifiedReason='Builtin tool did not return actual model/quality; existing included route only.',prompt=pp.as_posix(),promptSha256=sha(pp),references=[{k:v for k,v in e.items() if k!='derivedFrom'} for e in refs],evidence={'receipt':receipt.as_posix()},resizedAfterGeneration=False,finalArtUpscaled=False,status='candidate_pending_native_visual_and_seam_QA')
gp=dst.with_suffix('.png.generation.json');gp.write_text(json.dumps(g,ensure_ascii=False,indent=2))
print(json.dumps({'native':dst.as_posix(),'sha256':sha(dst),'dimensions':[w,h],'generation':gp.as_posix(),'receipt':receipt.as_posix()}))

