from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import json,hashlib,sys,shutil
P=Path(__file__).resolve().parent; R=P/'repairs/v5_20260920'
ident,source=sys.argv[1:3]; source=Path(source); out=R/'native'/f'{ident}.png'
assert source.is_file() and not out.exists(); shutil.copy2(source,out)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
prompt=R/'prompts'/f'{ident}.prompt.txt'; guide=R/'guides'/f'{ident}.png'
with Image.open(out) as im:
    im.load(); assert im.size==(1254,1254); alpha=im.convert('RGBA').getextrema()[3]; assert alpha==(255,255)
rec={'id':ident,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'route':'builtin_image_gen','requestedProduct':'ChatGPT Images 2.5','configuredModelTarget':'gpt-image-2.5-sunburst','configuredQualityTarget':'max','backendModelVerified':False,'actualBackendModel':None,'actualQualityPreset':None,'modelSelectorAvailable':False,'qualitySelectorAvailable':False,'sourceOutputPath':str(source),'sourceOutputSha256':sha(source),'outputFile':str(out),'outputSha256':sha(out),'actualNativePixels':[1254,1254],'alphaExtrema':alpha,'promptFile':str(prompt),'promptSha256':sha(prompt),'submittedImages':[{'path':str(guide),'sha256':sha(guide),'pixels':[1254,1254]}],'selectedTargetImageOneBased':1,'toolCall':{'name':'image_gen.imagegen','referenced_image_paths':[guide.as_posix()],'prompt':prompt.read_text(encoding='utf-8').rstrip('\n')},'finalArtUpscaled':False,'resizedAfterGeneration':False,'visualQa':{'status':'pending_roi_selection_and_reconnection'}}
out.with_suffix('.record.json').write_text(json.dumps(rec,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out),'sha256':sha(out)}))
