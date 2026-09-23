from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
import json,hashlib
from datetime import datetime,timezone
OUT=Path(__file__).resolve().parent
RESUME=OUT.parents[1]
PROD=RESUME.parent
OLD=OUT.parent/'r09_c09_review'
SOURCE=RESUME/'tools/repairs/versions/r09_c09_repair_v4/r09_c09.png'
NEIGHBORS=PROD/'tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):
    i=Image.open(p).convert('RGB');i.load();return i
im=load(SOURCE)
entries=[]
def emit(name,img,boxes,role):
    p=OUT/(name+'.png');img.save(p)
    entry={'file':str(p),'sha256':sha(p),'pixels':list(img.size),'sourceBoxesLTRB':boxes,'role':role,'resized':False,'viewed':False}
    old=OLD/p.name
    if old.is_file():
        entry['previousEvidenceSha256']=sha(old)
        entry['identicalToPreviouslyViewedEvidence']=entry['previousEvidenceSha256']==entry['sha256']
    entries.append(entry)
def seam(name,axis,strip,box):
    if axis=='v':
        board=Image.new('RGB',(1176,1048),(38,38,38));draw=ImageDraw.Draw(board)
        for seg in range(4):
            board.paste(strip.crop((0,seg*1024,288,(seg+1)*1024)),(seg*296,24))
            draw.text((seg*296+4,4),f'{name} y={seg*1024}..{(seg+1)*1024-1}',fill='white')
    else:
        board=Image.new('RGB',(1024,1272),(38,38,38));draw=ImageDraw.Draw(board)
        for seg in range(4):
            board.paste(strip.crop((seg*1024,0,(seg+1)*1024,288)),(0,seg*320+24))
            draw.text((4,seg*320+4),f'{name} x={seg*1024}..{(seg+1)*1024-1}',fill='white')
    emit(name+'_full_4096_native',board,[box],'four ordered native seam segments, no resize')
for axis in ['v','h']:
    for k in [1024,2048,3072]:
        # Use byte-identical label wording to support verified inheritance.
        boxes=[]
        if axis=='v':
            board=Image.new('RGB',(1176,1048),(38,38,38));draw=ImageDraw.Draw(board)
            for seg in range(4):
                box=[k-144,seg*1024,k+144,(seg+1)*1024];boxes.append(box)
                board.paste(im.crop(box),(seg*296,24));draw.text((seg*296+4,4),f'x={k} y={seg*1024}..{(seg+1)*1024-1}',fill='white')
        else:
            board=Image.new('RGB',(1024,1272),(38,38,38));draw=ImageDraw.Draw(board)
            for seg in range(4):
                box=[seg*1024,k-144,(seg+1)*1024,k+144];boxes.append(box)
                board.paste(im.crop(box),(0,seg*320+24));draw.text((4,seg*320+4),f'y={k} x={seg*1024}..{(seg+1)*1024-1}',fill='white')
        emit(f'{axis}{k}_full_4096_native',board,boxes,'full internal seam at original art pixel scale')
for y in [1024,2048,3072]:
    for x in [1024,2048,3072]:
        box=[x-256,y-256,x+256,y+256]
        emit(f'junction_x{x}_y{y}',im.crop(box),[box],'native internal four-patch junction')

verification=[]
for v in [2,3,4]:
    folder=RESUME/f'tools/repairs/versions/r09_c09_repair_v{v}'
    rec=json.loads((folder/'repair.json').read_text(encoding='utf-8'))
    checks=[]
    for name,item in rec['files'].items():
        p=folder/item['file'];checks.append({'file':str(p),'expectedSha256':item['sha256'],'actualSha256':sha(p),'matches':sha(p)==item['sha256']})
    for field in ['sourceCandidate','sourceRecord','prepared','originalNativeOutput']:
        item=rec[field];p=Path(item['file']);checks.append({'file':str(p),'expectedSha256':item['sha256'],'actualSha256':sha(p),'matches':sha(p)==item['sha256']})
    before=np.array(load(Path(rec['sourceCandidate']['file'])));after=np.array(load(folder/'r09_c09.png'))
    box=rec['canvasBoxLTRB'];mask=Image.open(folder/'mask.png').convert('L');ma=np.array(mask)
    fullmask=np.zeros((4096,4096),dtype=np.uint8);fullmask[box[1]:box[3],box[0]:box[2]]=ma
    changed=np.any(before!=after,axis=2)
    verification.append({'version':v,'repairRecord':str(folder/'repair.json'),'repairRecordSha256':sha(folder/'repair.json'),
      'fileChecks':checks,'maskNonzeroBoundsLocal':list(mask.getbbox()),'canvasBoxLTRB':box,
      'actualChangedPixels':int(changed.sum()),'changedOutsideMask':int(np.logical_and(changed,fullmask==0).sum()),
      'actualMaxShiftXY':rec['registration']['actualMaxShiftXY'],'resampling':rec['resampling']})
    emit(f'repair_v{v}_final_support',im.crop(box),[box],'entire1254 support from final v4; includes all actual cross/polygon/horizontal mask return contours')
    emit(f'repair_v{v}_mask',mask,[box],'exact actual mask shape used; view with support to inspect all return contours')

left=load(NEIGHBORS/'r09_c08.png');bottom=load(NEIGHBORS/'r10_c09.png');bl=load(NEIGHBORS/'r10_c08.png')
vertical=Image.new('RGB',(288,4096));vertical.paste(left.crop((3952,0,4096,4096)),(0,0));vertical.paste(im.crop((0,0,144,4096)),(144,0))
seam('external_left_r09_c08_c09','v',vertical,[-144,0,144,4096])
horizontal=Image.new('RGB',(4096,288));horizontal.paste(im.crop((0,3952,4096,4096)),(0,0));horizontal.paste(bottom.crop((0,0,4096,144)),(0,144))
seam('external_bottom_r09_c09_r10_c09','h',horizontal,[0,3952,4096,4240])
j=Image.new('RGB',(1024,1024));j.paste(left.crop((3584,3584,4096,4096)),(0,0));j.paste(im.crop((0,3584,512,4096)),(512,0));j.paste(bl.crop((3584,0,4096,512)),(0,512));j.paste(bottom.crop((0,0,512,512)),(512,512))
emit('external_four_tile_junction',j,[[-512,3584,512,4608]],'native r09c08/r09c09/r10c08/r10c09 corner')
neighbors=[{'file':str(NEIGHBORS/n),'sha256':sha(NEIGHBORS/n)} for n in ['r09_c08.png','r10_c08.png','r10_c09.png']]
manifest={'schemaVersion':1,'createdAtUtc':datetime.now(timezone.utc).isoformat(),'source':str(SOURCE),'sourceSha256':sha(SOURCE),
 'sourcePixels':[4096,4096],'processing':'exact-coordinate crops and board paste only; no resizing or art editing','neighbors':neighbors,
 'repairMechanicalVerification':verification,'entries':entries}
(OUT/'crop-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sourceSha256':manifest['sourceSha256'],'entries':len(entries),
 'inheritedIdentical':[Path(e['file']).name for e in entries if e.get('identicalToPreviouslyViewedEvidence')],
 'verification':[{'v':v['version'],'checks':len(v['fileChecks']),'mismatches':sum(not c['matches'] for c in v['fileChecks']),'outsideMaskChanges':v['changedOutsideMask']} for v in verification]},indent=2))
