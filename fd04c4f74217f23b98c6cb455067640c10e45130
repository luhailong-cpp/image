from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import sys,json,hashlib,shutil
root=Path(__file__).resolve().parent
tile_id=sys.argv[1];source=Path(sys.argv[2]);qa=sys.argv[3]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
out=root/'native'/f'{tile_id}.png'
if out.exists():raise RuntimeError('Refusing to overwrite native output')
shutil.copyfile(source,out)
with Image.open(out) as im:size=list(im.size)
if size!=[1254,1254]:raise RuntimeError('Unexpected native dimensions; never resize')
prompt=root/'prompts'/f'{tile_id}.prompt.txt';guide=root/'guides'/f'{tile_id}.layout-only.png';reference=root/'guides'/f'{tile_id}.input-preview.jpg'
r={'id':tile_id,'route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':size,'outputPath':str(out),'outputSha256':sha(out),'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'promptPath':str(prompt),'promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedReferencePath':str(reference),'submittedReferenceSha256':sha(reference),'submittedReferencePixels':[1254,1254],'submittedReferenceEncoding':'JPEG quality85 no resize','finalArtUpscaled':False,'resizedAfterGeneration':False,'generatedAtUtc':datetime.now(timezone.utc).isoformat(),'visualQa':qa,'crossDeliveryTileSeamsVerified':False}
appearance=root/'guides'/f'{tile_id}.appearance-reference.jpg'
r['additionalSubmittedReferences']=[{'role':'appearance_only_geometry_from_primary','path':str(appearance),'sha256':sha(appearance)}]
(root/'native'/f'{tile_id}.record.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'id':tile_id,'actualPixels':size,'sha256':r['outputSha256']}))