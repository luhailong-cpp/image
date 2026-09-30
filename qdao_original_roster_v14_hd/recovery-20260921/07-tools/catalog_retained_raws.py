"""Record genuine retained07 sources without changing any artwork or old evidence."""
import hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image

ROOT=Path(__file__).resolve().parent.parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
selected={read(p)['derivedFrom']['sha256']:read(p)['slot'] for p in (ROOT/'07-tools/candidate/07_moon_shadow_assassin_girl').rglob('*.generation.json')}
rows=[]
for folder in sorted((ROOT/'07-generation').iterdir()):
    if not folder.is_dir(): continue
    p=folder/'raw.png'
    if not p.is_file(): continue
    req,res=folder/'request.json',folder/'result.json'
    request=read(req) if req.is_file() else {}
    result=read(res) if res.is_file() else {}
    with Image.open(p) as im:
        dims=list(im.size);mode=im.mode;extrema=im.getchannel('A').getextrema() if mode=='RGBA' else None
    digest=sha(p)
    status='selected_current' if digest in selected else 'unselected_not_counted_as_delivery'
    row={'attempt':folder.name,'path':str(p),'sha256':digest,'nativeSize':dims,'mode':mode,'alphaExtrema':extrema,'selection':status,'selectedSlot':selected.get(digest)}
    record=Path(str(p)+'.generation.json')
    if not record.exists():
        meta={**row,'generatedAt':result.get('completedAt') or result.get('receivedAt'),'generatedAtScope':'observed_tool_return_time_when_available','cataloguedAt':datetime.now(timezone.utc).isoformat(),'tool':'image_gen.imagegen','route':'builtin','actualModel':result.get('actualModel'),'actualQuality':result.get('actualQuality'),'unverifiedReason':'Host-managed; actual model and quality not disclosed','configSnapshot':request.get('configSnapshot') or request.get('config_snapshot'),'submittedParameters':request.get('submittedParameters',{'model':None,'quality':None}),'requestEvidence':{'path':str(req),'sha256':sha(req)} if req.is_file() else None,'resultEvidence':{'path':str(res),'sha256':sha(res)} if res.is_file() else None,'promptEvidence':str(folder/'prompt.txt'),'referenceBindings':request.get('referenceBindings'),'nativeRecordedFromCurrentFile':True}
        record.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    row['generationRecord']=str(record); rows.append(row)
out=ROOT/'07-tools/raw-inventory-20260928.json'
out.write_text(json.dumps({'observedAt':datetime.now(timezone.utc).isoformat(),'retainedNativeCount':len(rows),'selectedRetainedNativeCount':sum(r['selection']=='selected_current' for r in rows),'unselectedNativeDoNotCount':sum(r['selection']!='selected_current' for r in rows),'rows':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'catalog':str(out),'retained':len(rows),'selected':sum(r['selection']=='selected_current' for r in rows)}))
