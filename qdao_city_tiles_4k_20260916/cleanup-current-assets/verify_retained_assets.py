"""Verify only retained current city artwork/design and the explicit deletion result."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    with p.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
receipt=read(ROOT/'deletion-receipt.json')
assert receipt['status']=='completed',receipt
plan=read(ROOT/'cleanup-plan-final.json')
assert receipt['planSha256']==sha(ROOT/'cleanup-plan-final.json')
assert receipt['deletedFiles']==len(plan['delete'])
images=0;current4k=0;selected_native=0
for item in plan['keep']:
    p=Path(item['file']);assert p.is_file() and sha(p)==item['sha256'],str(p)
    if p.suffix.lower() in ('.png','.jpg','.jpeg','.webp','.bmp','.gif','.tif','.tiff'):
        with Image.open(p) as im:
            im.load();images+=1
            if any(r.startswith('latest_selected_4K_candidate:') for r in item['reasons']):
                assert im.size==(4096,4096) and im.format=='PNG';current4k+=1
            if any(r.startswith('selected_native_patch_for_incomplete_tile:') for r in item['reasons']):
                assert im.size==(1254,1254) and im.format=='PNG';selected_native+=1
for item in plan['delete']:
    assert not Path(item['file']).exists(),'Deleted file reappeared; inspect concurrent work: '+item['file']
assert current4k==26 and selected_native==16
result={'schemaVersion':1,'checkedAtUtc':datetime.now(timezone.utc).isoformat(),
        'status':'retained_files_match_pre_cleanup_sha_and_decode',
        'retainedFilesVerified':len(plan['keep']),'retainedImagesFullyDecoded':images,
        'current4KCandidatesVerified':current4k,'selectedIncompleteNativePatchesVerified':selected_native,
        'deletedFilesVerifiedAbsent':len(plan['delete']),'deletedBytes':receipt['deletedBytes'],
        'historicalDeletedSourceBytesReverified':False,'productionAcceptedTiles':0,'deliveryReady':False,'errors':[]}
name='verification-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.json'
with (ROOT/name).open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2)
print(json.dumps({'report':str(ROOT/name),**result}))
