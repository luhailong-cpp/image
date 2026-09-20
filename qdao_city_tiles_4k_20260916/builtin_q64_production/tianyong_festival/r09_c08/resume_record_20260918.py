from pathlib import Path
import json,hashlib,sys,shutil
from datetime import datetime,timezone
from PIL import Image
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
if sys.argv[1]=='quarantine':
    ident='r01_c03'
    dest=P/'rejected'/'r01_c03_attempt1_20260918'
    dest.mkdir(parents=True,exist_ok=False)
    rec=json.loads((P/'native'/f'{ident}.record.json').read_text())
    for rel in [f'native/{ident}.png',f'native/{ident}.record.json',f'prompts/{ident}.prompt.txt']:
        shutil.copyfile(P/rel,dest/Path(rel).name)
    assert sha(dest/f'{ident}.png')==rec['outputSha256']
    rec.update(status='rejected_wrong_reference_target',failureReason='Prompt targeted image3 but result visually matches image4. Not selected for assembly.',retainedNativePath=str(dest/f'{ident}.png'),originalRecordPath=str(dest/f'{ident}.record.json'))
    (dest/'rejection.json').write_text(json.dumps(rec,indent=2),encoding='utf8')
    print(json.dumps({'preservedAt':str(dest),'sha256':rec['outputSha256']}))
elif sys.argv[1]=='record':
    ident,source,promptName,refName=sys.argv[2:6]
    src=Path(source); prompt=P/'prompts'/promptName; ref=P/'guides'/refName
    with Image.open(src) as im:
        im.load(); size=im.size; alpha=im.getextrema()[3] if im.mode=='RGBA' else [255,255]
        assert size==(1254,1254) and tuple(alpha)==(255,255),(size,alpha)
    out=P/'native'/f'{ident}.png'; old=P/'native'/f'{ident}.record.json'
    if out.exists() or old.exists(): raise RuntimeError('Refusing to overwrite existing native')
    shutil.copyfile(src,out)
    guide=P/'guides'/f'{ident}.layout-only.png'
    rec={'schemaVersion':3,'id':ident,'route':'builtin_image_gen','backendModelVerified':False,'actualNativePixels':list(size),'sourceOutputPath':str(src),'sourceOutputSha256':sha(src),'outputFile':f'native/{ident}.png','outputSha256':sha(out),'promptFile':f'prompts/{promptName}','promptSha256':sha(prompt),'guidePath':str(guide),'guideSha256':sha(guide),'submittedImages':[{'path':str(ref),'sha256':sha(ref),'pixels':list(size)}],'selectedTargetImageOneBased':1,'finalArtUpscaled':False,'resizedAfterGeneration':False,'alphaExtrema':list(alpha),'createdAtUtc':datetime.now(timezone.utc).isoformat(),'toolCall':{'name':'image_gen.imagegen','num_last_images_to_include':1,'modelSelectorAvailable':False,'qualitySelectorAvailable':False},'visualQa':{'status':'native_review_done_assembly_pending','note':'Single target generation reviewed; full seams and neighbor join still required.'}}
    old.write_text(json.dumps(rec,indent=2),encoding='utf8');print(json.dumps({'id':ident,'sha256':sha(out),'pixels':size}))
