import datetime,hashlib,json,re
from pathlib import Path
from PIL import Image
RUN=Path(__file__).resolve().parent;ART=RUN.parents[2]
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p,data):p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
work=read(RUN/'current-work.json');rows=work['workingCandidates'];assert len(rows)==11 and len({r['tile'] for r in rows})==11
verified=[]
for row in rows:
    p=ART/row['candidate']['file'];assert p.is_file() and sha(p)==row['candidate']['sha256']
    with Image.open(p) as im:im.load();assert im.size==(4096,4096)
    verified.append({'tile':row['tile'],'sha256':sha(p),'decodedPixels':[4096,4096]})
for row in work['currentOutputs']:
    for k in ['record','review']:
        p=ART/row[k]['file'];assert p.is_file() and sha(p)==row[k]['sha256']
for r in work['generationRecords']:
    p=ART/r['file'];assert p.is_file() and sha(p)==r['sha256']
receipt=read(RUN/'cleanup-receipt.json');assert receipt['status']=='completed'
assert all(not Path(e['path']).exists() for e in receipt['deleted'])
links=re.findall(r'\]\(([^)]+)\)',(RUN/'README.md').read_text(encoding='utf-8'))
for link in links:
    if '://' not in link:assert (RUN/link.split('#')[0]).exists(),link
lookup={r['tile']:r for r in rows};preview=Image.new('RGB',(1536,1024));sources=[]
for y,r in enumerate([8,9]):
    for x,c in enumerate([7,8,9]):
        tile=f'r{r:02}_c{c:02}';item=lookup[tile]['candidate'];p=ART/item['file']
        with Image.open(p) as im:preview.paste(im.convert('RGB').resize((512,512),Image.Resampling.LANCZOS),(x*512,y*512))
        sources.append({'tile':tile,**item,'previewXY':[x*512,y*512]})
f=RUN/'plaza-preview-1536x1024.png';preview.save(f)
write(f.with_name(f.name+'.generation.json'),{'file':str(f),'sha256':sha(f),'width':1536,'height':1024,'derivedFrom':sources,'operation':'Preview only: six 4096-square current working tiles individually downscaled to512 then assembled by map coordinates r08..09,c07..09. No blend, no enlargement.','formalAccepted':False,'newGeneration':False})
result={'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'checkpoint_files_verified_not_art_acceptance','workingTilesVerified':verified,'workingCoordinateCount':11,'currentOutputCount':4,'newGenerationRecordCount':7,'allCurrentReadmeLinksExist':True,'deletedFilesConfirmedAbsent':len(receipt['deleted']),'cleanupReceiptSha256':sha(RUN/'cleanup-receipt.json'),'currentWorkSha256':sha(RUN/'current-work.json'),'preview':{'file':str(f),'sha256':sha(f)},'formalAccepted':False,'clientRuntimeAccepted':False}
write(RUN/'validation.json',result)
print(json.dumps({k:v for k,v in result.items() if k!='workingTilesVerified'},ensure_ascii=False))
