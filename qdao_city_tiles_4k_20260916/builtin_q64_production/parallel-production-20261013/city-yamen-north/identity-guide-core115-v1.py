from pathlib import Path
import sys,json,hashlib
from PIL import Image
req=Path(sys.argv[1]);identity=Path(sys.argv[2]);slug=sys.argv[3];prompt=Path(sys.argv[4]).read_text(encoding='utf-8')
q=json.loads(req.read_text(encoding='utf-8'));guide=Image.open(identity).convert('RGB');assert guide.size==(1254,1254);world=q['coordinates']['worldBoxWithHalo']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pastes=[]
for p in q['guide']['nativeContextPastes']:
    s=p['source']
    if s['role']!='selected_generated_batch_neighbor' or Path(s['file']).resolve()==identity.resolve():continue
    assert sha(s['file'])==s['sha256'];w=s['worldBox'];core=[w[0]+115,w[1]+115,w[2]-115,w[3]-115]
    x0,y0,x1,y1=max(world[0],core[0]),max(world[1],core[1]),min(world[2],core[2]),min(world[3],core[3])
    if x0>=x1 or y0>=y1:continue
    crop=[x0-w[0],y0-w[1],x1-w[0],y1-w[1]];xy=[x0-world[0],y0-world[1]]
    guide.paste(Image.open(s['file']).convert('RGB').crop(crop),xy);pastes.append({'source':s,'sourceCropLTRB':crop,'guidePasteXY':xy,'resampled':False,'onlyActualNeighborCore':True})
out=req.parent/(slug+'.json');gp=req.parent/(slug+'.guide.png');assert not out.exists() and not gp.exists();guide.save(gp)
q.update(prompt=prompt,referenced_image_paths=[str(gp),'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png'],actualModel=None)
q['guide'].update(file=str(gp),sha256=sha(gp),nativeContextPastes=pastes,onlyActualNeighborCoresUsed=True,baseIdentitySource={'file':str(identity),'sha256':sha(identity),'limitedTo':'Existing identities; specified geometry/background defects require AI correction.'})
out.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'request':str(out),'guide':str(gp)}))
