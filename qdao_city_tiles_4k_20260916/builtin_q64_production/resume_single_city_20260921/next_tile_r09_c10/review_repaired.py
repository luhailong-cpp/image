from pathlib import Path
from PIL import Image
import hashlib,json
P=Path(__file__).resolve().parent;Q=P/'qa/internal-v4';Q.mkdir(exist_ok=True)
f=P/'repairs/versions/internal-v4/r09_c10.png';tile=Image.open(f).convert('RGB')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
outfiles=[]
def save(im,name):
 f=Q/name;im.save(f);outfiles.append({'path':str(f),'sha256':sha(f),'pixels':list(im.size),'resized':False})
for axis in ('vertical','horizontal'):
 for index in range(1,4):
  out=Image.new('RGB',(920,1024) if axis=='vertical' else (1024,920))
  for n in range(4):
   c=index*1024;box=(c-115,n*1024,c+115,(n+1)*1024) if axis=='vertical' else (n*1024,c-115,(n+1)*1024,c+115);xy=(n*230,0) if axis=='vertical' else (0,n*230);out.paste(tile.crop(box),xy)
  save(out,f'internal-{axis}-{index}-100pct.png')
out=Image.new('RGB',(690,690))
for y in range(1,4):
 for x in range(1,4):out.paste(tile.crop((x*1024-115,y*1024-115,x*1024+115,y*1024+115)),((x-1)*230,(y-1)*230))
save(out,'all-nine-internal-intersections-100pct.png')
for name,box in {'internal-v1-ring-step':(774,1270,1274,1770),'internal-h2-highlight-step':(300,1798,800,2298),'internal-h3-band-step':(3000,2822,3500,3322)}.items():save(tile.crop(box),f'recheck-{name}-100pct.png')
tile.resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'overview-preview-only.jpg',quality=96)
out=Image.open(P/'output/extended-context.png').convert('RGB');out.paste(tile,(115,115));out.save(P/'repairs/versions/internal-v4/extended-context.png')
(Q/'evidence-index.json').write_text(json.dumps({'candidate':str(f),'candidateSha256':sha(f),'files':outfiles,'status':'visual_review_pending','externalBoundaryStatus':'unchanged_from_failed_base_candidate','extendedContext':{'file':str(P/'repairs/versions/internal-v4/extended-context.png'),'sha256':sha(P/'repairs/versions/internal-v4/extended-context.png'),'method':'Repaired4096corepastedintooriginal4326extendedat115,115; originalhalo retained.'}},indent=2),encoding='utf-8')
print(json.dumps({'candidate':str(f),'sha256':sha(f),'qaFiles':len(outfiles)}))
