from pathlib import Path
import sys,json
from PIL import Image
R=Path(__file__).resolve().parents[1];sys.path.insert(0,str(R))
import production as p
base='east-r09c06-westgrout-v02-r09_c06'
art=R/'qa'/f'{base}-candidate-4096.png'
im=Image.open(art).convert('RGB')
views=[]
for key,box in [('west-target-upper',[820,420,1120,700]),('west-target-lower',[820,840,1140,1140]),('east-target-pending',[3070,1060,3370,1360])]:
 q=R/'qa'/f'{base}-{key}-native100.png';assert not q.exists();im.crop(box).save(q);views.append(p.metadata(q,'exact 1:1 target crop'))
d=p.load(R/'qa'/'expansion-east-worker-map.json'); west=p.load(R/'qa'/'expansion-east-worker-map.json')['candidateArtifacts']['r09_c05']
wim=Image.open(west['path']).convert('RGB')
for ri in range(4):
 q=R/'qa'/f'{base}-west-pair-row{ri+1}-native100.png';assert not q.exists()
 out=Image.new('RGB',(500,1024));out.paste(wim.crop((3846,ri*1024,4096,(ri+1)*1024)),(0,0));out.paste(im.crop((0,ri*1024,250,(ri+1)*1024)),(250,0));out.save(q);views.append(p.metadata(q,'exact 1:1 paired boundary, west last250 then east first250'))
p.dump(R/'qa'/f'{base}-supplement-manifest.json',{'candidate':p.metadata(art,'best native candidate'),'westCandidate':west,'views':views,'formalAccepted':False})
print(json.dumps({'views':len(views),'candidate':p.metadata(art,'best native candidate')}))
