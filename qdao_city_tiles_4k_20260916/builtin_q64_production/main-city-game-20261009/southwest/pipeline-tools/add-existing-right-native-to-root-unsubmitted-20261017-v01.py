from pathlib import Path
from PIL import Image
import sys,json,hashlib
from datetime import datetime,timezone
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B))
from native_pipeline import Pipeline,pid
tile,request=sys.argv[1:];assert tile in {f'r{r:02d}_c06' for r in range(9,17)}
rp=Path(request);r=json.loads(rp.read_text(encoding='utf-8-sig'));a=r['coordinates'];row=a['row'];col=a['column'];assert col<4
receipt=B/tile/'pipeline/receipts'/rp.name.replace('.request.json','.receipt.json');assert not receipt.exists()
p=Pipeline(tile);selected_path,selection_evidence=p.selected_record(tile,row,col+1);rec=json.loads(selected_path.read_text(encoding='utf-8-sig'))
src=Path(rec['file']);sha=lambda x:hashlib.sha256(Path(x).read_bytes()).hexdigest();assert sha(src)==rec['sha256']
old=Path(r['referenced_image_paths'][0]);out=old.with_name(old.stem+'.existing-right-native.png');assert not out.exists()
with Image.open(old) as im:im2=im.convert('RGB')
with Image.open(src) as im:im2.paste(im.crop((0,230,230,1254)),(1024,230))
im2.save(out)
d={'file':str(out),'sha256':sha(out),'operation':'exact RIGHT neighbor left230 crop pasted below TOP230 into unsubmitted mechanical seed','gameArt':False,'sourceResampling':False,'sources':[{'file':str(old),'sha256':sha(old)},{'file':str(src),'sha256':sha(src),'sourceCrop':[0,230,230,1254],'targetBox':[1024,230,1254,1254]}],'formalAccepted':False}
dp=Path(str(out)+'.derivation.json');dp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
r['references'][0]={'file':str(out),'sha256':sha(out),'role':'mechanical layout with actual top/left and existing right native strips, not final art','derivationFile':str(dp),'derivationSha256':sha(dp)}
r['referenced_image_paths']=[x['file'] for x in r['references']]
r.setdefault('neighborSources',[]).append({'file':str(src),'sha256':sha(src),'sourceTile':tile,'sourcePatch':pid(row,col+1),'role':'exact existing selected RIGHT native strip','sourceCrop':[0,230,230,1254],'targetBox':[1024,230,1254,1254],'effectiveTargetBox':[1024,230,1254,1254],'sourceResampling':False,'formalAccepted':False})
r['preparedAtUtc']=datetime.now(timezone.utc).isoformat()
rp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'request':str(rp),'seed':str(out),'rightSource':str(src),'rightSha256':sha(src)},ensure_ascii=False))

