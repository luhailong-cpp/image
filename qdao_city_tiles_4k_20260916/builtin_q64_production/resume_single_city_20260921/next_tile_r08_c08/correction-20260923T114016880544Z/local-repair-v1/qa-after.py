from pathlib import Path
from PIL import Image
from datetime import datetime,timezone
import hashlib,json
P=Path(__file__).resolve().parent;OUT=P/'masked-result';SRC=P.parent/'diagnostic-20260923T114940236668Z'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();info=lambda p:{'file':str(Path(p).resolve()),'sha256':sha(p)}
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,im):
 assert not p.exists();im.save(p);return dict(info(p),pixels=list(im.size))
base=read(SRC/'qa/index.json');candidate=Image.open(OUT/'r08_c08.png').convert('RGB');bottom=Image.open(base['bottomNeighbor']['file']).convert('RGB');qa=OUT/'qa';qa.mkdir()
items=[];images={}
for old in base['items']:
 ident=old['id']
 if 'cropLTRB' in old:im=candidate.crop(tuple(old['cropLTRB']))
 else:
  a,b=old['range'];im=Image.new('RGB',(1024,384));im.paste(candidate.crop((a,3904,b,4096)),(0,0));im.paste(bottom.crop((a,0,b,192)),(0,192))
 same=im.tobytes()==Image.open(old['artifact']['file']).convert('RGB').tobytes();images[ident]=im
 items.append(dict(old,artifact=save(qa/(ident+'.png'),im),passed=None,priorEvidence=old['artifact'],pixelsEqualPriorInspectedEvidence=same))
boards=[]
for axis in ['vertical','horizontal']:
 for k in [1024,2048,3072]:
  board=Image.new('RGB',(768,2048) if axis=='vertical' else (2048,768))
  for i in range(4):
   im=images[f'{axis}-{k}-segment-{i+1}'];board.paste(im,((i%2)*im.width,(i//2)*im.height))
  boards.append({'id':f'{axis}-{k}','artifact':save(qa/f'board-{axis}-{k}.png',board)})
board=Image.new('RGB',(1152,1152))
for r in range(1,4):
 for c in range(1,4):board.paste(images[f'junction-r{r}-c{c}'],((c-1)*384,(r-1)*384))
boards.append({'id':'nine-junctions','artifact':save(qa/'board-nine-junctions.png',board)})
board=Image.new('RGB',(2048,768))
for i in range(4):board.paste(images[f'bottom-segment-{i+1}'],((i%2)*1024,(i//2)*384))
boards.append({'id':'bottom','artifact':save(qa/'board-bottom.png',board)})
for i in range(4):save(qa/f'near-bottom-full-context-{i+1}.png',candidate.crop((i*1024,3472,(i+1)*1024,4096)))
save(OUT/'preview-not-acceptance.png',candidate.resize((1024,1024),Image.Resampling.LANCZOS))
index={'candidate':info(OUT/'r08_c08.png'),'repair':info(OUT/'repair.json'),'createdAtUtc':datetime.now(timezone.utc).isoformat(),'items':items,'boards':boards,'bottomNeighbor':base['bottomNeighbor'],'formalAccepted':False,'status':'prepared_new_version_QA_not_yet_reviewed'}
with (qa/'index.json').open('x',encoding='utf8',newline='\n') as f:json.dump(index,f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'qa':info(qa/'index.json'),'unchangedEvidenceCount':sum(x['pixelsEqualPriorInspectedEvidence'] for x in items),'changedEvidenceCount':sum(not x['pixelsEqualPriorInspectedEvidence'] for x in items)}))
