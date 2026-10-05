import json,pathlib,hashlib,datetime
from PIL import Image,ImageDraw,ImageFont
out=pathlib.Path(__file__).parent
e=json.loads((out/'source-evidence.json').read_text(encoding='utf8'))
result={'checkedAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'changedSinceViewedSnapshot':[],'unchangedCount':0,'meaning':'Changed files are new unreviewed revisions until specifically viewed; prior visual conclusions do not transfer.'}
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for cid,c in e['characters'].items():
    changed=[]
    for gid,g in c['groups'].items():
        for f in g['frames']:
            path=pathlib.Path(f['file']);sha=hashlib.sha256(path.read_bytes()).hexdigest()
            if sha==f['sha256']: result['unchangedCount']+=1;continue
            item={'character':cid,'group':gid,'frame':f['frame'],'path':str(path),'viewedSnapshotSha256':f['sha256'],'currentSha256':sha,'currentExtraReview':False}
            result['changedSinceViewedSnapshot'].append(item);changed.append(item)
    if changed:
        sheet=Image.new('RGB',(1040,30+((len(changed)+3)//4)*280),(242,239,230));d=ImageDraw.Draw(sheet)
        d.text((6,5),f'{cid}: concurrent new revisions; extra QA',font=font,fill='black')
        for n,item in enumerate(changed):
            x=(n%4)*260;y=30+(n//4)*280
            im=Image.open(item['path']).convert('RGBA');im.thumbnail((255,255),Image.Resampling.LANCZOS)
            sheet.paste(im,(x,y+22),im)
            d.text((x+4,y+3),f"{item['group']}/{item['frame']} {item['currentSha256'][:8]}",font=font,fill='black')
        sheet.save(out/f'{cid[:2]}-concurrent-latest.png')
(out/'concurrent-changes.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'unchanged':result['unchangedCount'],'changed':len(result['changedSinceViewedSnapshot'])}))
