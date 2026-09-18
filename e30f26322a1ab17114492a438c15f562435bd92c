from pathlib import Path
from PIL import Image
import json,hashlib,shutil,sys
from datetime import datetime,timezone
root=Path(__file__).resolve().parent;d=root/sys.argv[1];s=Path(sys.argv[2]);out=d/'native.png'
if out.exists():raise RuntimeError('No overwrite')
shutil.copyfile(s,out);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
im=Image.open(out);assert im.size==(1254,1254);assert 'A' not in im.getbands() or im.getchannel('A').getextrema()==(255,255)
plan=json.loads((d/'plan.json').read_text());prompt=d/'prompt.txt';ref=d/'input.jpg';guide=d/'input.png'
r=dict(id=d.name,route='builtin_image_gen',backendModelVerified=False,actualNativePixels=list(im.size),sourceOutputPath=str(s),sourceOutputSha256=sha(s),outputPath=str(out),outputSha256=sha(out),promptPath=str(prompt),promptSha256=sha(prompt),guidePath=str(guide),guideSha256=sha(guide),submittedReferencePath=str(ref),submittedReferenceSha256=sha(ref),actualInputReferences=[dict(imageIndex=1,path=str(ref),sha256=sha(ref))],inputCount=1,selectedImageIndex=1,toolParameters=dict(num_last_images_to_include=1),cropXYXY=plan['cropXYXY'],coordinateSpace=plan['coordinateSpace'],generatedAtUtc=datetime.now(timezone.utc).isoformat(),finalArtUpscaled=False,resizedAfterGeneration=False,sourceBytesPreserved=True,visualQa='Native targeted repair retained; source and repair reconnect QA pending')
(d/'native.record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(dict(record=str(d/'native.record.json'),sha256=sha(out))))
