from pathlib import Path
from PIL import Image
import hashlib,json,datetime
R=Path(__file__).resolve().parent;B=R.parent.parent
assembly=B/'qa/r13-c06-water-repair-W08-v1/assembly.json';j=json.loads(assembly.read_text());source=assembly.parent/j['context']['path'];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();assert sha(source)==j['context']['sha256'];im=Image.open(source);records=[]
def crop(name,box,scope):
    p=R/(name+'.png')
    with p.open('xb') as f:im.crop(box).save(f,format='PNG')
    records.append({'path':str(p),'sha256':sha(p),'contextBox':box,'dimensions':[box[2]-box[0],box[3]-box[1]],'scale':1,'operation':'exact integer crop','scope':scope})
for row,(y0,y1) in enumerate([(0,1024),(768,1766)],1):
    for col,x in enumerate([0,1024,2048,3072],1):crop(f'upper-native-r{row}-c{col}',[x,y0,x+1254,y1],'full upper native coverage, overlapping by230px in x and256px in y')
for col,x in enumerate([1139,2163,3187],1):crop(f'vertical-c{col}',[x-192,0,x+192,1766],'original vertical seam')
for col,x in enumerate([115,1139,2163,3187],1):crop(f'horizontal-c{col}',[x,947,x+1024,1331],'original first-row horizontal seam')
write={'source':str(source),'sha256':sha(source),'assembly':str(assembly),'assemblySha256':sha(assembly),'globalContextBox':j['globalContextBox'],'reviewLimitContextYExclusive':1766,'formalAccepted':False,'status':'native-crops-prepared','createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'crops':records}
with (R/'inputs-v1.json').open('x',encoding='utf-8') as f:json.dump(write,f,indent=2)
print(json.dumps({'directory':str(R),'sourceSha256':sha(source),'crops':len(records)}))
