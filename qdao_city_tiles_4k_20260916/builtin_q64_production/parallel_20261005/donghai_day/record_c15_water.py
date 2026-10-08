import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
R=Path(__file__).resolve().parent
T=R/'r08_c15'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dst=T/'native/r03_c03.png'; rec=Path(str(dst)+'.generation.json')
old=json.loads(rec.read_text(encoding='utf-8')); assert sha(dst)=='f145f699b07f4eff239a0718ede37464e428a633b8881cd30962e2aa61d07655'
src=Path(sys.argv[1]); im=Image.open(src);im.load();assert im.size==(1254,1254)
archive=T/'rejected/r03_c03-water-woodgrain';archive.mkdir(parents=True,exist_ok=True)
save(archive/'generation.json',dict(old,rejectionReason='Water below hull incorrectly painted with wood grain. Superseded after native AI correction.'))
shutil.copyfile(old['prompt'],archive/'prompt.txt')
shutil.copyfile(T/'prompts/r03_c03.references.json',archive/'references.json')
prompt=T/'prompts/r03_c03-water-correction.txt'
style=Path('D:/work/image/designs/gameplay-ui/04-guild.png')
refs=[{'file':str(dst),'sha256':old['sha256'],'role':'AI edit input; superseded pixels, historical record archived','archivedRecord':str(archive/'generation.json')},{'file':str(style),'sha256':sha(style),'role':'primary user-confirmed art style'}]
new=dict(old,sha256=sha(src),generatedAt=datetime.now(timezone.utc).isoformat(),prompt=str(prompt),promptSha256=sha(prompt),references=refs)
new['submittedParameters']=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=[r['file'] for r in refs])
new['evidence']=dict(toolResultSourcePath=str(src),toolResultSha256=sha(src),responseMetadata='Native output returned by image_gen.imagegen; model and quality not disclosed.')
new['supersedes']={'sha256':old['sha256'],'archivedRecord':str(archive/'generation.json')}
shutil.copyfile(src,dst);save(rec,new)
print(json.dumps({'saved':str(dst),'sha256':sha(dst),'size':im.size}))
