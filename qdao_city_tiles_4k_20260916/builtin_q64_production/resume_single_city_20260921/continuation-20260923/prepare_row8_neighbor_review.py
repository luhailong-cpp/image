"""Create unscaled, complete adjacent-edge and four-tile review crops; never assert a pass."""
from pathlib import Path
from PIL import Image
import json,hashlib,datetime,io
S=Path(__file__).resolve().parent.parent
A=S.parent.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
ledger_path=S/'current-coverage-ledger.json'
ledger_bytes=ledger_path.read_bytes()
ledger=json.loads(ledger_bytes.decode('utf-8-sig'))
input_snapshots={str(ledger_path):hashlib.sha256(ledger_bytes).hexdigest()}
refs={t['tile']:t['candidate'] for t in ledger['tiles'] if t['candidateExists']}
for tid in ('r08_c07','r08_c08','r08_c09'):
    p=S/f'next_tile_{tid}/latest-candidate.json'
    if tid=='r08_c08' and not p.exists():
        p=S/'next_tile_r08_c08/correction-20260923T114016880544Z/local-repair-v1/masked-result/repair.json'
    raw=p.read_bytes();input_snapshots[str(p)]=hashlib.sha256(raw).hexdigest()
    d=json.loads(raw.decode('utf-8-sig'));refs[tid]=d['candidate']
ids=['r08_c07','r08_c08','r08_c09','r09_c07','r09_c08','r09_c09']
ims={}
for tid in ids:
    p=A/refs[tid]['file'];raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==refs[tid]['sha256']
    ims[tid]=Image.open(io.BytesIO(raw)).convert('RGB');assert ims[tid].size==(4096,4096)
stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
out=S/'continuation-20260923'/('row8-neighbor-review-'+stamp);out.mkdir()
items=[]
pairs=[('r08_c07','r08_c08','vertical_boundary'),('r08_c08','r08_c09','vertical_boundary')]+[(f'r08_c{c:02}',f'r09_c{c:02}','horizontal_boundary') for c in [7,8,9]]
for left,right,axis in pairs:
    eid=left+'|'+right
    evidence=[]
    for n in range(4):
        start=n*1024
        if axis=='vertical_boundary':
            box1=[3584,start,4096,start+1024];box2=[0,start,512,start+1024]
            canvas=Image.new('RGB',(1024,1024));canvas.paste(ims[left].crop(box1),(0,0));canvas.paste(ims[right].crop(box2),(512,0))
        else:
            box1=[start,3584,start+1024,4096];box2=[start,0,start+1024,512]
            canvas=Image.new('RGB',(1024,1024));canvas.paste(ims[left].crop(box1),(0,0));canvas.paste(ims[right].crop(box2),(0,512))
        p=out/f'{left}--{right}-segment-{n+1:02}.png';canvas.save(p)
        evidence.append({'file':p.relative_to(A).as_posix(),'sha256':sha(p),'sourceBoxesLTRB':{left:box1,right:box2},'pixelScale':'1:1','reviewStatus':'pending'})
    items.append({'id':eid,'type':'full_adjacent_edge','axis':axis,'candidateSha256ByTile':{t:refs[t]['sha256'] for t in [left,right]},'lengthPixels':4096,'contextPixelsEachSide':512,'evidence':evidence,'result':'pending'})
for c in [7,8]:
    tids=[f'r08_c{c:02}',f'r08_c{c+1:02}',f'r09_c{c:02}',f'r09_c{c+1:02}']
    boxes=[[3584,3584,4096,4096],[0,3584,512,4096],[3584,0,4096,512],[0,0,512,512]]
    canvas=Image.new('RGB',(1024,1024))
    for i,(tid,box) in enumerate(zip(tids,boxes)):canvas.paste(ims[tid].crop(box),((i%2)*512,(i//2)*512))
    jid=f'junction_r08_c{c:02}';p=out/(jid+'.png');canvas.save(p)
    items.append({'id':jid,'type':'four_tile_junction','candidateSha256ByTile':{t:refs[t]['sha256'] for t in tids},'evidence':[{'file':p.relative_to(A).as_posix(),'sha256':sha(p),'sourceBoxesLTRB':dict(zip(tids,boxes)),'pixelScale':'1:1','reviewStatus':'pending'}],'result':'pending'})
for path,expected in input_snapshots.items():assert sha(Path(path))==expected,'Concurrent selected state changed; discard this prepared review set'
report={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'role':'original_pixel_review_evidence_not_art_acceptance','inputSnapshotSha256ByFile':input_snapshots,'sourceCandidates':{t:refs[t] for t in ids},'items':items,'wholeCityPassed':False,'formalAccepted':False,'runtimeAccepted':False}
(out/'index.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'directory':str(out),'edges':5,'junctions':2,'images':22,'allReviews':'pending'}))
