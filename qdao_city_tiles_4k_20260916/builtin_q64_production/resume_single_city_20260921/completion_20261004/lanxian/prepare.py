from pathlib import Path
import hashlib,json,datetime
from PIL import Image
R=Path(__file__).resolve().parent
P=R.parent/'production-audit/inventory.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
inventory=json.loads(P.read_text(encoding='utf-8'))
records=[]
for city in [c for c in inventory['sevenPlans'] if c['key'].startswith('lanxian_')]:
    C=R/city['key']/'baseline';C.mkdir(parents=True,exist_ok=True)
    tiles=[]
    for t in city['historicalBatchCandidates']:
        assert sha(t['file'])==t['sha256']
        im=Image.open(t['file']).convert('RGB');assert im.size==(4096,4096)
        tiles.append(im)
        Q=C/t['tile'];Q.mkdir(exist_ok=True)
        views=[]
        for axis in ('x','y'):
            for at in (1024,2048,3072):
                board=Image.new('RGB',(1024,1024))
                boxes=[]
                for seg in range(4):
                    box=(at-128,seg*1024,at+128,(seg+1)*1024) if axis=='x' else (seg*1024,at-128,(seg+1)*1024,at+128)
                    v=im.crop(box)
                    if axis=='x':v=v.transpose(Image.Transpose.ROTATE_90)
                    board.paste(v,(0,seg*256));boxes.append(box)
                f=Q/f'{axis}{at}-all4096.png';board.save(f)
                views.append({'file':str(f),'sha256':sha(f),'kind':'internal_full_seam','axis':axis,'at':at,'cropBoxes':boxes,'resized':False,'losslessRotation':axis=='x'})
        board=Image.new('RGB',(960,960));boxes=[]
        for yi,y in enumerate((1024,2048,3072)):
            for xi,x in enumerate((1024,2048,3072)):
                box=(x-160,y-160,x+160,y+160);board.paste(im.crop(box),(xi*320,yi*320));boxes.append(box)
        f=Q/'junctions-nine.png';board.save(f);views.append({'file':str(f),'sha256':sha(f),'kind':'nine_junctions_row_major','cropBoxes':boxes,'resized':False})
        edges={}
        for side in ('north','south','west','east'):
            board=Image.new('RGB',(1024,1024));boxes=[]
            for seg in range(4):
                start=seg*1024;end=start+1024
                box={'north':(start,0,end,256),'south':(start,3840,end,4096),'west':(0,start,256,end),'east':(3840,start,4096,end)}[side]
                v=im.crop(box)
                if side in ('west','east'):v=v.transpose(Image.Transpose.ROTATE_90)
                board.paste(v,(0,seg*256));boxes.append(box)
            f=Q/f'edge-{side}.png';board.save(f)
            exactbox={'north':(0,0,4096,1),'south':(0,4095,4096,4096),'west':(0,0,1,4096),'east':(4095,0,4096,4096)}[side]
            edges[side]={'rawRgbBoundarySha256':hashlib.sha256(im.crop(exactbox).tobytes()).hexdigest(),'view':str(f),'viewSha256':sha(f),'cropBoxes':boxes}
            views.append({'file':str(f),'sha256':sha(f),'kind':'tile_edge_without_neighbor','side':side,'cropBoxes':boxes,'resized':False})
        im.resize((1024,1024),Image.Resampling.LANCZOS).save(Q/'overview-only.png')
        record={'city':city['key'],'tile':t['tile'],'source':{'file':t['file'],'sha256':t['sha256']},'sourceAssembly':str(Path(t['file']).parent/'assembly.json'),'fourEdges':edges,'qa':views,'status':'pending_actual_view'}
        (Q/'index.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');records.append(record)
    trio=Image.new('RGB',(1536,512))
    for i,im in enumerate(tiles):trio.paste(im.resize((512,512),Image.Resampling.LANCZOS),(i*512,0))
    trio.save(C/'triple-overview-only.png')
    for i in range(2):
        board=Image.new('RGB',(1024,1024));bound=[]
        for seg in range(4):
            start=seg*1024;end=start+1024
            v=Image.new('RGB',(256,1024));v.paste(tiles[i].crop((3968,start,4096,end)),(0,0));v.paste(tiles[i+1].crop((0,start,128,end)),(128,0))
            board.paste(v.transpose(Image.Transpose.ROTATE_90),(0,seg*256));bound.append([start,end])
        f=C/f'common-c0{i+6}-c0{i+7}-all4096.png';board.save(f)
        bind={'left':city['historicalBatchCandidates'][i],'right':city['historicalBatchCandidates'][i+1],'file':str(f),'sha256':sha(f),'segments':bound,'widthEachSide':128,'resized':False,'losslessRotation':True,'status':'pending_actual_view'}
        f.with_suffix('.json').write_text(json.dumps(bind,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'sources.json').write_text(json.dumps({'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inventory':{'file':str(P),'sha256':sha(P)},'tiles':records},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'tiles':len(records),'qaBoards':len(records)*11+4,'sourceHashesVerified':True},ensure_ascii=False))
