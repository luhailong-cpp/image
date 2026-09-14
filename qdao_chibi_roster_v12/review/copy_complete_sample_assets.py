from pathlib import Path
from PIL import Image
import shutil, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'candidate-stable-body'/'24_lu_dongbin'
SITE=ROOT/'review'/'site'
DIRECTIONS=['S','SW','W','NW','N','NE','E','SE']
pairs=[]
for direction in DIRECTIONS:
    for index in range(1,9):
        rel=Path('walk')/direction/f'{index:02}.png'
        pairs.append((SOURCE/rel,SITE/'sample'/rel))
    rel=Path('idle')/f'{direction}.png'
    pairs.append((SOURCE/rel,SITE/'sample'/rel))
missing=[str(source) for source,_ in pairs if not source.is_file()]
if missing:
    raise SystemExit('Candidate PNG export is not complete: '+str(len(missing))+' missing files. No candidate PNG copied.')
for source,_ in pairs:
    with Image.open(source) as im:
        assert im.size==(512,512),(str(source),im.size)
        assert im.mode=='RGBA',(str(source),im.mode)
        im.verify()
records=[]
for source,target in pairs:
    target.parent.mkdir(parents=True,exist_ok=True)
    before=hashlib.sha256(source.read_bytes()).hexdigest()
    shutil.copy2(source,target)
    after=hashlib.sha256(target.read_bytes()).hexdigest()
    assert before==after
    records.append({'source':str(source.relative_to(ROOT)),'destination':str(target.relative_to(SITE)),'sha256':after})
report={'status':'copied_verified','candidate_only_not_imported_by_this_script':True,'direction_count':8,'authored_walk_png_count':64,'independent_idle_png_count':8,'source_images_modified':False,'files':records}
out=ROOT/'review'/'browser-qc'/'sample-candidate-assets.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in report if k!='files'}))

