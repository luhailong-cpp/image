from pathlib import Path
import sys,json,hashlib
from PIL import Image
B=Path(__file__).resolve().parent
req=Path(sys.argv[1]);identity=Path(sys.argv[2]);slug=sys.argv[3];prompt=Path(sys.argv[4]).read_text(encoding='utf-8')
q=json.loads(req.read_text(encoding='utf-8'));guide=Image.open(identity).convert('RGB')
assert guide.size==(1254,1254)
pastes=[]
for p in q['guide']['nativeContextPastes']:
    if p['source']['role']!='selected_generated_batch_neighbor':continue
    if Path(p['source']['file']).resolve()==identity.resolve():continue
    guide.paste(Image.open(p['source']['file']).convert('RGB').crop(p['sourceCropLTRB']),p['guidePasteXY']);pastes.append(p)
out=req.parent/(slug+'.json');gp=req.parent/(slug+'.guide.png')
assert not out.exists() and not gp.exists()
guide.save(gp)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
q.update(prompt=prompt,referenced_image_paths=[str(gp),'D:/work/image/designs/mail-ui-v1/01-mail-event.png','D:/work/image/designs/team-ui-v2/team-ui-v2.png'],actualModel=None)
q['guide'].update(file=str(gp),sha256=sha(gp),nativeContextPastes=pastes,baseIdentitySource={'file':str(identity),'sha256':sha(identity),'limitedTo':'Existing object identities and silhouettes only. Architecture background corrected explicitly by prompt.'})
out.write_text(json.dumps(q,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'request':str(out),'guide':str(gp)}))
