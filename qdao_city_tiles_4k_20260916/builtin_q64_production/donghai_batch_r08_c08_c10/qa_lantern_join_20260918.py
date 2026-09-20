from pathlib import Path
from PIL import Image
import json,hashlib,numpy as np
from datetime import datetime,timezone
PROD=Path(__file__).parent.parent
out=PROD/'donghai_lantern/r08_c08_c09_c10_joint/output_v1';qa=out/'qa';core=Image.open(out/'core12288x4096.png').convert('RGB')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
views=[]
def save(name,img,boxes,role):
 p=qa/(name+'.png');assert not p.exists();img.save(p,compress_level=4);views.append(dict(path=str(p),sha256=sha(p),pixels=list(img.size),sourceBoxes=boxes,source=str(out/'core12288x4096.png'),resized=False,role=role))
for x in (9216,10240,11264):
 im=Image.new('RGB',(1200,1024));boxes=[]
 for k in range(4):
  b=[x-150,k*1024,x+150,(k+1)*1024];im.paste(core.crop(b),(300*k,0));boxes.append(b)
 save(f'internal_x{x}_all4096_native',im,boxes,'Full4096 vertical seam; top-to-bottom panels left-to-right')
for y in (1024,2048,3072):
 im=Image.new('RGB',(1024,1200));boxes=[]
 for k in range(4):
  b=[8192+k*1024,y-150,8192+(k+1)*1024,y+150];im.paste(core.crop(b),(0,300*k));boxes.append(b)
 save(f'internal_y{y}_all4096_native',im,boxes,'Full4096 horizontal seam; left-to-right panels top-to-bottom')
for x in (8192,9216,10240,11264):
 for y in (1024,2048,3072):
  b=[x-450,y-450,x+450,y+450];save(f'junction_x{x}_y{y}_native',core.crop(b),[b],'Native900 square junction')
old=PROD/'donghai_lantern/r08_c09/joined_pair_v3/r08_c08.png'
assert np.array_equal(np.array(Image.open(old)),np.array(Image.open(out/'r08_c08.png')))
assert np.array_equal(np.concatenate([np.array(Image.open(out/f'r08_c{c:02}.png')) for c in (8,9,10)],axis=1),np.array(core))
records=[]
for p in sorted((PROD/'donghai_lantern/r08_c10/native').glob('*.record.json')):
 r=json.loads(p.read_text());assert sha(r['outputPath'])==r['outputSha256']==sha(r['sourceOutputPath'])
 assert sha(r['promptPath'])==r['promptSha256']
 assert sha(r['guidePath'])==r['guideSha256']
 assert sha(r['submittedReferencePath'])==r['submittedReferenceSha256']
 for a in r['actualInputReferences']:assert sha(a['path'])==a['sha256']
 im=Image.open(r['outputPath']).convert('RGBA');assert im.size==(1254,1254) and im.getchannel('A').getextrema()==(255,255)
 records.append(dict(path=str(p),sha256=sha(p),outputSha256=r['outputSha256'],size=[1254,1254],fullyOpaque=True))
report=dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),status='mechanical_pass_visual_pending',nativeRecords=records,nativeRecordCount=len(records),views=views,rejoinPixelIdentical=True,oldC08PixelUnchanged=True,sourceAssemblySha256=sha(out/'assembly.json'),wholeCityComplete=False,accepted=False,runtimePublished=False)
(qa/'qa-mechanical-20260918.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(dict(nativeRecords=len(records),qaViews=len(views),output=str(out))))
