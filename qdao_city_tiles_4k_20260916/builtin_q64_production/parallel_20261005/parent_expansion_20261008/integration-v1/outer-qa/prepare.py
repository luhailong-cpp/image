from pathlib import Path
from PIL import Image
import numpy as np,json,hashlib
P=Path(__file__).resolve().parent;E=P.parent.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
src=P.parent/'assembled.png';assembly=json.loads((P.parent/'assembly.json').read_text(encoding='utf-8-sig'))
assert sha(src)==assembly['sha256'];a=Image.open(src).convert('RGB')
sel=json.loads(Path(assembly['sourceSelection']['file']).read_text(encoding='utf-8-sig'))
west=next(x for x in sel['candidates'] if x['tile']=='r08_c09');w=Image.open(west['file']).convert('RGB');assert sha(west['file'])==west['sha256']
fix=E/'r02_c01/edge-fix-v2/joined.png';f=Image.open(fix).convert('RGB')
items=[]
def save(name,im,info):
 p=P/(name+'.png');im.save(p);items.append(dict(file=str(p),sha256=sha(p),nativeScale=1,actuallyViewed=False,**info))
for name,b in [('north-c01',(0,780,1024,1050)),('north-c02',(1024,780,2048,1050)),('north-c03',(2048,780,3187,1050)),('south-c01',(0,2030,1024,2300)),('south-c02',(1024,2030,2048,2300)),('south-c03',(2048,2030,3187,2300)),('east-c03-upper',(3040,780,3340,1560)),('east-c03-lower',(3040,1500,3340,2300))]:save(name,a.crop(b),{'operation':'exact native crop','source':{'file':str(src),'sha256':sha(src)},'cropLTRB':b})
joint=Image.new('RGB',(360,1520));joint.paste(w.crop((3916,780,4096,2300)),(0,0));joint.paste(a.crop((0,780,180,2300)),(180,0))
for name,box in [('west-current-upper',(0,0,360,820)),('west-current-lower',(0,700,360,1520))]:save(name,joint.crop(box),{'operation':'native crop and side-by-side concat, tile seam at image x180','sources':[{'file':west['file'],'sha256':west['sha256']},{'file':str(src),'sha256':sha(src)}],'globalC10LTRB':[-180,780+box[1],180,780+box[3]]})
before=np.array(w.crop((3981,909,4096,2163)));after=np.array(f.crop((0,0,115,1254)));diff=np.any(before!=after,axis=2);ys,xs=np.where(diff)
prospective=w.copy();prospective.paste(f.crop((0,0,115,1254)),(3981,909))
joint2=Image.new('RGB',(500,1520));joint2.paste(prospective.crop((3736,780,4096,2300)),(0,0));joint2.paste(a.crop((0,780,140,2300)),(360,0))
for name,box in [('west-prospective-upper',(0,0,500,820)),('west-prospective-lower',(0,700,500,1520))]:save(name,joint2.crop(box),{'operation':'QA-only hypothetical c09 left115 insertion at [3981,909,4096,2163], followed by native side-by-side concat; c09/c10 seam at image x360 and inserted-strip outer edge x245','sources':[{'file':west['file'],'sha256':west['sha256']},{'file':str(src),'sha256':sha(src)},{'file':str(fix),'sha256':sha(fix)}],'globalC10LTRB':[-360,780+box[1],140,780+box[3]]})
result={'assembledSource':{'file':str(src),'sha256':sha(src)},'westSource':west,'c01Source':{'file':str(fix),'sha256':sha(fix)},'c09Transfer':{'sourceCropLTRB':[0,0,115,1254],'targetLTRB':[3981,909,4096,2163],'changedPixels':int(diff.sum()),'changedBoundingLTRB':[int(xs.min())+3981,int(ys.min())+909,int(xs.max())+3982,int(ys.max())+910],'hypotheticalOnly':True,'writtenBackToC09':False},'qa':items,'formalAccepted':False,'reviewStatus':'pending_actual_visual_review'}
(P/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'qaFiles':len(items),'sourceSha256':sha(src),'transfer':result['c09Transfer']}))
