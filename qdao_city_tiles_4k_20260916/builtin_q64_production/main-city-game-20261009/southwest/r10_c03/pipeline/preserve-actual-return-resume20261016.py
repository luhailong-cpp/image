import sys,json,hashlib,shutil
from pathlib import Path
from PIL import Image
rp,source,started,returned,hint=sys.argv[1:]
p=Path(rp).resolve(); q=json.loads(p.read_text(encoding='utf-8-sig'))
tile=q['tile'];patch=q['coordinates']['id'];t=p.parents[2]
allowed={'r10_c03','r10_c04'}|{f'r{r:02d}_c{c:02d}' for r in [11,12] for c in range(1,5)}
assert tile in allowed and t.name==tile
assert t.parent==Path(__file__).resolve().parents[2]
attempt=p.name.removeprefix(patch+'.').removesuffix('.request.json')
s=Path(source);assert str(s) in hint
d=t/'refinement/versions'/attempt/(patch+'.returned-native.png');assert not d.exists()
d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s,d)
sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest()
h=sha(d);assert h==sha(s)
with Image.open(d) as im:pixels=list(im.size)
pres={'file':str(d),'sha256':h,'source':str(s),'pixels':pixels,'nativePixelsPreserved':True,'resampling':False}
r={'tool':'image_gen.imagegen','status':'returned_image','route':'builtin','sourceOutputPath':str(s),'startedAtUtc':started,'returnedAtUtc':returned,'actualModel':None,'actualQuality':None,'paidApiUsed':False,'formalAccepted':False,'internalAccepted':False,'request':str(p),'actualReferences':q['references'],'outputHint':hint,'workspacePreservation':pres,'visualStatus':'saved_before_visual_inspection','visualDisposition':'Actual returned image copied byte-for-byte immediately in same tool execution; visual selection pending.'}
out=t/'pipeline/receipts'/(patch+'.'+attempt+'.receipt.json');assert not out.exists()
out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'receipt':str(out),'saved':pres},ensure_ascii=False))
