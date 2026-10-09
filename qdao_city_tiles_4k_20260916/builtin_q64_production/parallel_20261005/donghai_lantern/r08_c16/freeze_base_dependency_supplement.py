"""Freeze the verified base-native evidence without revising the repair contract."""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil,hashlib
T=Path(__file__).resolve().parent;D=T/'source-contract-v2';CP=D/'source-contract.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def ref(p):return {'file':str(p),'sha256':sha(p)}
def snap(e,category):
    p=Path(e['file']);assert sha(p)==e['sha256'],str(p)
    target=D/'snapshots'/category/(e['sha256'][:16]+'-'+p.name);target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():assert sha(target)==e['sha256']
    else:shutil.copyfile(p,target)
    return {'authority':e,'snapshot':ref(target)}
def run():
    assert sha(CP)=='e60640e0b49db49ecd7f932c4c99b41146ed2b2fc3fcbbedaaccf7c4d2afb289'
    c=read(CP);out=[];seen=set()
    def add(e,category):
        k=(e['file'],e['sha256'])
        if k not in seen:out.append(snap(e,category));seen.add(k)
    for e in c['baseNativeEvidence']:
        for k in ('native','record','prompt'):add(e[k],'base-'+k)
        for rr in e['references']:
            if rr['currentPixelsVerified']:add(rr['reference'],'base-input-references')
            else:add(rr['historicalRecord'],'superseded-text-records')
    for e in c['nativeSources']:
        rr=read(e['generationRecordSnapshot']['snapshot']['file'])
        add({'file':rr['prompt'],'sha256':rr['promptSha256']},'repair-prompts')
        for x in rr['references']:add(x,'repair-input-references')
    report={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'sourceContract':ref(CP),'supplementPurpose':'Freeze base 16 native/records/prompts and available actual references plus repair prompt/reference evidence; primary contract remains byte-identical.','snapshots':out,'baseNativeCount':16,'baseRecordCount':16,'supersededBaseReferenceCount':5,'supersededPixelClaims':False,'dayWritten':False,'primaryContractUnchanged':True,'script':ref(__file__)}
    p=D/'dependency-snapshot-supplement.json';p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'report':ref(p),'snapshotCount':len(out)}))
if __name__=='__main__':run()
