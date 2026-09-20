from pathlib import Path
from PIL import Image
import json,hashlib,shutil
from datetime import datetime,timezone
prod=Path(__file__).resolve().parent.parent
d=prod/'donghai_lantern/r08_c08_c09_c10_joint/repairs_v2/fish_basin'
src=Path('C:/Users/luyua/.codex/generated_images/01a0bc85-142b-78e3-8c23-419e70027335/exec-6234db66-80e3-4436-90b4-d1fae3458e28.png')
dst=d/'native.png'; assert not dst.exists()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
shutil.copy2(src,dst)
im=Image.open(dst); a=im.convert('RGBA').getchannel('A').getextrema()
assert im.size==(1254,1254) and a==(255,255)
prep=json.loads((d/'reference-preparation.json').read_text(encoding='utf-8'))
refs=prep['references']; assert all(sha(x['path'])==x['sha256'] for x in refs)
prompt=d/'prompt.txt'
record=dict(id='lantern_fish_basin_v2_20260920',appearance='donghai_lantern',route='builtin_image_gen',configuredModelTarget='gpt-image-2.5-sunburst',configuredQualityTarget='max',actualBackendModel=None,actualQualityPreset=None,backendModelVerified=False,qualityVerified=False,actualNativePixels=list(im.size),fullyOpaque=True,sourceOutputPath=str(src),sourceOutputSha256=sha(src),outputPath=str(dst),outputSha256=sha(dst),promptPath=str(prompt),promptSha256=sha(prompt),guidePath=refs[0]['path'],guideSha256=refs[0]['sha256'],submittedReferencePath=refs[0]['path'],submittedReferenceSha256=refs[0]['sha256'],actualInputReferences=refs,inputCount=2,selectedImageIndex=1,toolParameters=dict(referenced_image_paths=[x['path'].replace('\\','/') for x in refs]),cropXYXY=prep['cropXYXY'],coordinateSpace='triple_core',generatedAtUtc=datetime.now(timezone.utc).isoformat(),finalArtUpscaled=False,resizedAfterGeneration=False,sourceBytesPreserved=sha(src)==sha(dst),visualQa='Native output inspected: single visible eye on each exposed blue head; clean continuous body and lantern lighting; return-edge review pending')
(d/'native.record.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(record=str(d/'native.record.json'),sourceSha256=sha(src),nativePixels=list(im.size),fullyOpaque=True)))
