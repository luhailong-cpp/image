"""Remove redundant embedded image payloads per the user's final-only retention request."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib
ROOT=Path(__file__).resolve().parent.parent
now=datetime.now(timezone.utc).isoformat()
changes=[]
def strip(value,path,removed):
    if isinstance(value,dict):
        for key in list(value):
            item=value[key]
            if isinstance(item,str) and item.startswith('data:image/'):
                removed.append({'field':path+'.'+key,'encodedCharacters':len(item)})
                del value[key]
            else:strip(item,path+'.'+key,removed)
    elif isinstance(value,list):
        for index,item in enumerate(value):strip(item,path+'['+str(index)+']',removed)
for p in sorted((ROOT/'20-generation').rglob('*.json')):
    before=p.read_bytes()
    if b'data:image/' not in before:continue
    data=json.loads(before.decode('utf-8-sig'));removed=[]
    strip(data,'$',removed)
    if not removed:continue
    data['storageCleanup']={'at':now,'userInstruction':'Discard original and rollback image versions; keep final game images/designs and necessary metadata',
        'removedEmbeddedImages':removed,'originalMetadataFileSha256':hashlib.sha256(before).hexdigest(),
        'note':'Image payload fields removed; exact prompts, returned output_hint and reported model/quality metadata retained.'}
    after=(json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    p.write_bytes(after)
    changes.append({'path':str(p),'beforeSha256':hashlib.sha256(before).hexdigest(),
        'afterSha256':hashlib.sha256(after).hexdigest(),'bytesFreed':len(before)-len(after),'removed':removed})
log=ROOT/'20-tools'/'embedded-payload-cleanup-20260923.json'
assert not log.exists(),'Use a fresh log instead of overwriting earlier cleanup'
log.write_text(json.dumps({'at':now,'files':changes,'bytesFreed':sum(x['bytesFreed'] for x in changes)},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'modifiedJsonFiles':len(changes),'bytesFreed':sum(x['bytesFreed'] for x in changes)}))
