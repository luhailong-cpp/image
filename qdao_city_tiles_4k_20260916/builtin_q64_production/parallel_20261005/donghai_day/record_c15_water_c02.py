import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
T=Path(__file__).resolve().parent/'r08_c15'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d): Path(p).parent.mkdir(parents=True,exist_ok=True);Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
dst=T/'native/r04_c02.png';rec=Path(str(dst)+'.generation.json');old=json.loads(rec.read_text(encoding='utf-8'))
assert sha(dst)=='04b8d134e228ed9f5344b7cacfb2cc98a1c00c73d034078eeb6afb0cf322423e'
src=Path(sys.argv[1]);im=Image.open(src);im.load();assert im.size==(1254,1254)
archive=T/'rejected/r04_c02-bright-cellular-water';archive.mkdir(parents=True,exist_ok=True)
hist=archive/'generation.json';save(hist,dict(old,rejectionReason='Overly bright dense cellular water pattern, superseded by calm-water AI correction.'))
shutil.copyfile(old['prompt'],archive/'prompt.txt')
shutil.copyfile(T/'prompts/r04_c02.references.json',archive/'references.json')
prompt=T/'prompts/r04_c02-water-correction.txt';style=Path('D:/work/image/designs/gameplay-ui/04-guild.png');guide=T/'guides/r04_c02.png'
refs=[dict(file=str(dst),sha256=old['sha256'],role='AI edit target, historical rejected pixel version',availability='superseded',historicalRecord=str(hist),historicalRecordSha256=sha(hist),pixelValidation='historical-record-only-not-current-pixels'),dict(file=str(style),sha256=sha(style),role='primary user-confirmed rendering style'),dict(file=str(guide),sha256=sha(guide),role='quiet water color and original structural guidance only')]
new=dict(old,sha256=sha(src),generatedAt=datetime.now(timezone.utc).isoformat(),prompt=str(prompt),promptSha256=sha(prompt),references=refs)
new['submittedParameters']=dict(model=None,quality=None,transparent_background=False,referenced_image_paths=[r['file'] for r in refs])
new['evidence']=dict(toolResultSourcePath=str(src),toolResultSha256=sha(src),responseMetadata='Native output returned by image_gen.imagegen; model/quality undisclosed.')
new['supersedes']=dict(sha256=old['sha256'],historicalRecord=str(hist),reason='Remove excessive light water texture')
shutil.copyfile(src,dst);save(rec,new);save(T/'prompts/r04_c02-water-correction.references.json',refs)
raw=Path(old['evidence']['toolResultSourcePath']);generated=Path('C:/Users/luyua/.codex/generated_images').resolve()
if raw.exists() and raw.resolve().is_relative_to(generated) and sha(raw)==old['sha256']: raw.unlink()
print(json.dumps(dict(saved=str(dst),sha256=sha(dst),size=im.size)))

