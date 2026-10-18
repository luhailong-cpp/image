from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, sys
from datetime import datetime, timezone
B=Path(__file__).resolve().parents[2]
T=B/'r10_c02'
ap=Path(sys.argv[1]).resolve()
assert ap.is_relative_to((T/'pipeline/output').resolve())
read=lambda p: json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=read(ap)
assert a['tile']=='r10_c02' and a['complete4kCandidate'] and a['assembledNativeCount']==16
core=a['output']; context=a['contextOutput']
assert sha(core['file'])==core['sha256'] and sha(context['file'])==context['sha256']
im=Image.open(core['file']).convert('RGB'); assert im.size==(4096,4096)
q=ap.parent/'left-worker-qa-resume20261016-v01'; q.mkdir(exist_ok=False)
views=[]
def save(name,panel,regions,qaOnly=False):
    p=q/(name+'.png'); panel.save(p)
    views.append({'id':name,'file':str(p),'sha256':sha(p),'nativeRegionCount':regions,'nativeRegionResampling':False if not qaOnly else None,'qaOnly':qaOnly,'viewed':False})
overview=im.resize((1600,1600),Image.Resampling.LANCZOS)
save('overview-QA-only-1600',overview,0,True)
for row in range(4):
    panel=Image.new('RGB',(840,1048),'white'); d=ImageDraw.Draw(panel)
    for k,x in enumerate([1024,2048,3072]):
        panel.paste(im.crop((x-128,row*1024,x+128,(row+1)*1024)),(k*280,24)); d.text((k*280+3,3),f'V{k+1} row{row+1}',fill='black')
    save(f'internal-V-row{row+1}',panel,3)
for k,y in enumerate([1024,2048,3072]):
    panel=Image.new('RGB',(1024,1120),'white'); d=ImageDraw.Draw(panel)
    for col in range(4):
        panel.paste(im.crop((col*1024,y-128,(col+1)*1024,y+128)),(0,col*280+24)); d.text((3,col*280+3),f'H{k+1} col{col+1}',fill='black')
    save(f'internal-H{k+1}',panel,4)
panel=Image.new('RGB',(840,840),'white'); d=ImageDraw.Draw(panel)
for r,y in enumerate([1024,2048,3072]):
    for c,x in enumerate([1024,2048,3072]):
        panel.paste(im.crop((x-128,y-128,x+128,y+128)),(c*280,r*280+24)); d.text((c*280+3,r*280+3),f'corner {r+1}-{c+1}',fill='black')
save('internal-nine-corners',panel,9)
cat=read(B/'current-candidates.json')['tiles']['r09_c02']; top=cat['candidate']; assert sha(top['file'])==top['sha256']
tim=Image.open(top['file']).convert('RGB'); assert tim.size==(4096,4096)
panel=Image.new('RGB',(1024,1120),'white'); d=ImageDraw.Draw(panel)
for c in range(4):
    part=Image.new('RGB',(1024,256)); part.paste(tim.crop((c*1024,3968,(c+1)*1024,4096)),(0,0)); part.paste(im.crop((c*1024,0,(c+1)*1024,128)),(0,128))
    panel.paste(part,(0,c*280+24)); d.text((3,c*280+3),f'TOP col{c+1}',fill='black')
save('external-top-native',panel,4)
lap=B/'r10_c01/pipeline/output/3fa66685eea6dfa7/assembly.json'; la=read(lap); left=la['output']; assert sha(left['file'])==left['sha256']
lim=Image.open(left['file']).convert('RGB'); assert lim.size==(4096,4096)
panel=Image.new('RGB',(1120,1048),'white'); d=ImageDraw.Draw(panel)
for r in range(4):
    part=Image.new('RGB',(256,1024)); part.paste(lim.crop((3968,r*1024,4096,(r+1)*1024)),(0,0)); part.paste(im.crop((0,r*1024,128,(r+1)*1024)),(128,0))
    panel.paste(part,(r*280,24)); d.text((r*280+3,3),f'LEFT row{r+1}',fill='black')
save('external-left-native',panel,4)
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r10_c02','assembly':{'file':str(ap),'sha256':sha(ap)},'core':core,'context':context,'topNeighbor':top,'leftNeighbor':left,'views':views,'nativeRegionResampling':False,'onlyOverviewResampledForQa':True,'artPixelsModified':False,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'reviewStatus':'constructed_not_yet_visually_inspected'}
mp=q/'manifest.json'; mp.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps({'qa':str(q),'manifest':str(mp),'core':core,'context':context},ensure_ascii=False))
