from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime
R=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    fp=R/'tiles/r10_c14-candidate.png'
    im=Image.open(fp).convert('RGB')
    west=Image.open(R.parent/'r10_c13/repairs/r10_c13-combined-v8.png').convert('RGB')
    out=R/'qa/native-initial';out.mkdir(parents=True,exist_ok=True)
    records=[]
    for axis in ['x','y']:
        for pos in [1024,2048,3072]:
            sheet=Image.new('RGB',(1024,1152),(30,30,30));d=ImageDraw.Draw(sheet)
            boxes=[]
            for i in range(4):
                box=(pos-128,i*1024,pos+128,(i+1)*1024) if axis=='x' else (i*1024,pos-128,(i+1)*1024,pos+128)
                crop=im.crop(box)
                if axis=='x': crop=crop.transpose(Image.Transpose.ROTATE_90)
                d.text((8,i*288+4),f'{axis}{pos} segment {i+1}, native pixels; x strips rotated 90 degrees',fill='white')
                sheet.paste(crop,(0,i*288+26));boxes.append(box)
            dst=out/f'{axis}{pos}-full-native.png';sheet.save(dst)
            records.append({'file':str(dst),'source':str(fp),'sourceSha256':sha(fp),'boxesLTRB':boxes,'resize':False,'rotation90':axis=='x'})
    sheet=Image.new('RGB',(1200,1284),(30,30,30));d=ImageDraw.Draw(sheet)
    for r,y in enumerate([1024,2048,3072]):
        for c,x in enumerate([1024,2048,3072]):
            d.text((c*400+6,r*428+4),f'{x},{y}',fill='white');sheet.paste(im.crop((x-200,y-200,x+200,y+200)),(c*400,r*428+26))
    dst=out/'nine-junctions-native.png';sheet.save(dst);records.append({'file':str(dst),'source':str(fp),'sourceSha256':sha(fp),'resize':False,'nineCenters':[1024,2048,3072],'radius':200})
    sheet=Image.new('RGB',(1024,1376),(30,30,30));d=ImageDraw.Draw(sheet)
    for i in range(4):
        strip=Image.new('RGB',(320,1024));strip.paste(west.crop((3936,i*1024,4096,(i+1)*1024)),(0,0));strip.paste(im.crop((0,i*1024,160,(i+1)*1024)),(160,0))
        d.text((8,i*344+4),f'West shared boundary segment {i+1}, rotated90 native pixels',fill='white');sheet.paste(strip.transpose(Image.Transpose.ROTATE_90),(0,i*344+24))
    dst=out/'west-shared-full-native.png';sheet.save(dst);records.append({'file':str(dst),'source':str(fp),'sourceSha256':sha(fp),'westSource':str(R.parent/'r10_c13/repairs/r10_c13-combined-v8.png'),'resize':False,'rotation90':True,'halfWidth':160})
    northfp=R/'references/north-source-combined-v5.png'
    north=Image.open(northfp).convert('RGB')
    sheet=Image.new('RGB',(1024,1376),(30,30,30));d=ImageDraw.Draw(sheet)
    for i in range(4):
        strip=Image.new('RGB',(1024,320));strip.paste(north.crop((i*1024,3936,(i+1)*1024,4096)),(0,0));strip.paste(im.crop((i*1024,0,(i+1)*1024,160)),(0,160))
        d.text((8,i*344+4),f'North shared boundary segment {i+1}, native pixels',fill='white');sheet.paste(strip,(0,i*344+24))
    dst=out/'north-shared-full-native.png';sheet.save(dst);records.append({'file':str(dst),'source':str(fp),'sourceSha256':sha(fp),'northSource':str(northfp),'northSourceSha256':sha(northfp),'resize':False,'halfHeight':160})
    (out/'crop-record.json').write_text(json.dumps({'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records,'visualReviewPending':True},indent=2),encoding='utf8')
    print(out)
if __name__=='__main__':run()
