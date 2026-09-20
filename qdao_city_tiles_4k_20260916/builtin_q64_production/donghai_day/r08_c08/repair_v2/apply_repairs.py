from pathlib import Path
from PIL import Image,ImageFilter
from datetime import datetime,timezone
import json,hashlib,importlib.util,sys,numpy as np
root=Path(__file__).resolve().parent.parent;r=root/'repair_v2';out=root/'output_v2';qa=root/'qa_v2'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
manifest=r/'assembly.json'
if '--check' in sys.argv:
 m=json.loads(manifest.read_text(encoding='utf8'))
 assert sha(Path(m['baseExtended']))==m['baseExtendedSha256']
 for record in m['nativeRepairs']:
  assert sha(Path(record['outputPath']))==record['outputSha256']
  assert sha(Path(record['sourceOutputPath']))==record['sourceOutputSha256']
  assert Image.open(record['outputPath']).size==(1254,1254)
  for field in ['prompt','guide','submittedReference']:assert sha(Path(record[field+'Path']))==record[field+'Sha256']
 for f in m['files']:assert sha(root/f['file'])==f['sha256']
 e=np.asarray(Image.open(out/'extended-context.png'));c=np.asarray(Image.open(out/'donghai_day_r08_c08_q64_4k_candidate.png'))
 assert e.shape==(4326,4326,3) and c.shape==(4096,4096,3) and np.array_equal(e[115:4211,115:4211],c)
 for q in m['qa']:
  assert sha(root/q['file'])==q['sha256']
 print(json.dumps({'passed':True,'nativeRepairCount':len(m['nativeRepairs']),'pixels':[4096,4096],'extendedPixels':[4326,4326],'qaFiles':len(m['qa'])}));sys.exit()
spec=importlib.util.spec_from_file_location('mechanical',root/'assemble_builtin.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);seam=mod.load_seam_helper()
basefile=root/'output/extended-context.png';base=np.asarray(Image.open(basefile).convert('RGB')).copy();plan=json.loads((r/'plan.json').read_text(encoding='utf8'))
records=[];masks=[];w=230;axis=np.arange(w)[None,:]
for entry in plan['patches']:
 id=entry['id'];record=json.loads((r/'native'/f'{id}.record.json').read_text(encoding='utf8'));p=np.asarray(Image.open(record['outputPath']).convert('RGB'));assert p.shape==(1254,1254,3)
 x,y=entry['boxInFinal'][:2];x+=115;y+=115;c=base[y:y+1254,x:x+1254].copy();mask=np.full((1254,1254),255,np.uint8)
 for side in ['left','right','top','bottom']:
  if side=='left':path=seam(c[:,:w],p[:,:w]);mask[:,:w]=np.minimum(mask[:,:w],np.uint8(axis>=path[:,None])*255)
  elif side=='right':path=seam(c[:,-w:],p[:,-w:]);mask[:,-w:]=np.minimum(mask[:,-w:],np.uint8(axis<=path[:,None])*255)
  elif side=='top':
   path=seam(c[:w].transpose(1,0,2),p[:w].transpose(1,0,2));mask[:w]=np.minimum(mask[:w],(np.uint8(axis>=path[:,None])*255).T)
  else:
   path=seam(c[-w:].transpose(1,0,2),p[-w:].transpose(1,0,2));mask[-w:]=np.minimum(mask[-w:],(np.uint8(axis<=path[:,None])*255).T)
 mask=np.asarray(Image.fromarray(mask).filter(ImageFilter.GaussianBlur(2))).copy();mask[:2]=0;mask[-2:]=0;mask[:,:2]=0;mask[:,-2:]=0
 base[y:y+1254,x:x+1254]=mod.blend_exact(c,p,mask)
 mp=r/f'{id}.placement-mask.png';Image.fromarray(mask).save(mp);masks.append({'file':str(mp.relative_to(root)),'sha256':sha(mp)});records.append(record)
out.mkdir(exist_ok=True);qa.mkdir(exist_ok=True);Image.fromarray(base).save(out/'extended-context.png');candidate=Image.fromarray(base[115:4211,115:4211]);candidate.save(out/'donghai_day_r08_c08_q64_4k_candidate.png')
mod.QA=qa;items=mod.write_qa(candidate)
for entry in plan['patches']:
 f=qa/(entry['id']+'_repair_100pct.png');candidate.crop(entry['boxInFinal']).save(f);items.append({'file':str(f.relative_to(root)).replace('\\','/'),'crop':entry['boxInFinal'],'kind':'native-pixel-crop','size':[1254,1254],'sha256':sha(f)})
for item in items:
 f=root/item['file'];Image.open(f).save(f.with_suffix('.review.jpg'),quality=85)
files=[{'file':str(f.relative_to(root)).replace('\\','/'),'pixels':list(Image.open(f).size),'sha256':sha(f)} for f in out.glob('*.png')]
m={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'baseExtended':str(basefile),'baseExtendedSha256':sha(basefile),'baseAssemblySha256':sha(root/'output/assembly.json'),'sourceResampling':False,'guidePixelsComposited':False,'globalBlur':False,'colorMatching':False,'featherRadius':2,'nativeRepairs':records,'masks':masks,'files':files,'qa':items,'runtimePublished':False,'visualQa':'pending','scriptSha256':sha(Path(__file__))};manifest.write_text(json.dumps(m,indent=2),encoding='utf8');print(json.dumps({'files':files,'nativeRepairs':len(records),'qaFiles':len(items)}))
