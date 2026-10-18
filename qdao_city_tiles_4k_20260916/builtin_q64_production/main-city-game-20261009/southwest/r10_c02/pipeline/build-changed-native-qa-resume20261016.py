from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
B=Path(__file__).resolve().parents[2]
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
oldp=B/'r10_c02/pipeline/output/68ed540e96c6b98d/assembly.json'
newp=B/'r10_c02/pipeline/output/7f5a9e7db824dfe1/assembly.json'
old,new=read(oldp),read(newp)
om={s['id']:s['nativeSha256'] for s in old['nativeSources']}
nm={s['id']:s['nativeSha256'] for s in new['nativeSources']}
changed=[k for k in om if om[k]!=nm[k]]; assert set(changed)=={'p03_04','p04_04'}
im=Image.open(new['output']['file']).convert('RGB'); assert im.size==(4096,4096)
assert sha(new['output']['file'])==new['output']['sha256']
q=newp.parent/'left-worker-changed-qa-resume20261016-v01';q.mkdir(exist_ok=False)
views=[]
def save(name,panel,n):
 p=q/(name+'.png');panel.save(p);views.append({'id':name,'file':str(p),'sha256':sha(p),'nativeRegionCount':n,'nativeRegionResampling':False,'viewed':False})
panel=Image.new('RGB',(560,1048),'white');d=ImageDraw.Draw(panel)
for i,r in enumerate([2,3]):
 panel.paste(im.crop((2944,r*1024,3200,(r+1)*1024)),(i*280,24));d.text((i*280+3,3),f'V3 row{r+1}',fill='black')
save('changed-V3-rows3-4',panel,2)
panel=Image.new('RGB',(1024,560),'white');d=ImageDraw.Draw(panel)
for i,y in enumerate([2048,3072]):
 panel.paste(im.crop((3072,y-128,4096,y+128)),(0,i*280+24));d.text((3,i*280+3),f'H{i+2} col4',fill='black')
save('changed-H2-H3-col4',panel,2)
panel=Image.new('RGB',(560,280),'white');d=ImageDraw.Draw(panel)
for i,y in enumerate([2048,3072]):
 panel.paste(im.crop((2944,y-128,3200,y+128)),(i*280,24));d.text((i*280+3,3),f'corner row{i+2} col3',fill='black')
save('changed-two-corners',panel,2)
doc={'tile':'r10_c02','assembly':{'file':str(newp),'sha256':sha(newp)},'core':new['output'],'context':new['contextOutput'],'priorAssembly':{'file':str(oldp),'sha256':sha(oldp)},'changedNativeIds':changed,'unchangedNativeIds':[k for k in om if om[k]==nm[k]],'unchangedFailureEvidence':str(oldp.parent/'left-worker-qa-resume20261016-v01/worker-review-and-repair-queue.json'),'views':views,'internalPassed':False,'externalPassed':False,'formalAccepted':False,'reviewStatus':'constructed_pending_visual_inspection'}
mp=q/'manifest.json';mp.write_text(json.dumps(doc,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({'qa':str(q),'manifest':str(mp)},ensure_ascii=False))
