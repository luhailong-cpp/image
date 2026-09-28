import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image, ImageChops, ImageDraw

root=Path('E:/work/image/qdao_city_tiles_4k_20260916')
session=root/'builtin_q64_production/resume_single_city_20260921'
out=Path(__file__).resolve().parent
old=session/'continuation_20260925T132104Z/qa-c07/native-crops.manifest.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp(): return datetime.now(timezone.utc).isoformat()
m=json.loads(old.read_text(encoding='utf-8-sig'))
source=Path(m['source']['file']); im=Image.open(source).convert('RGB')
assert im.size==(4096,4096)
assert sha(source)==m['source']['sha256']
checks=[]
for b in m['boards']:
    bp=Path(b['file']); board=Image.open(bp).convert('RGB')
    assert sha(bp)==b['sha256'], b['id']
    assert list(board.size)==b['pixels'], b['id']
    if b.get('sourceComposition'):
        composed=Image.new('RGB',(4096,320))
        for c in b['sourceComposition']:
            assert sha(c['file'])==c['sha256']
            ci=Image.open(c['file']).convert('RGB')
            composed.paste(ci.crop(c['sourceRectLTRB']),c['destinationRectLTRB'][:2])
        comparison=composed
    else: comparison=im
    for p in b['pieces']:
        xy=p['boardXY']; dims=p['pixels']
        got=board.crop((xy[0],xy[1],xy[0]+dims[0],xy[1]+dims[1]))
        expected=comparison.crop(p['sourceRectLTRB'])
        assert ImageChops.difference(got,expected).getbbox() is None, (b['id'],p)
    checks.append({'id':b['id'],'file':str(bp),'sha256':sha(bp),'pixelEqualityVerified':True,'pieces':b['pieces']})

east=session/'next_tile_r08_c08/correction-20260923T114016880544Z/local-repair-v1/masked-result/r08_c08.png'
south=root/'builtin_q64_production/tianyong_festival/upperpair_r09_c07_c08_row10_c07_c10_20260918/output_v5/r09_c07.png'
southeast=south.with_name('r09_c08.png')
ei=Image.open(east).convert('RGB'); si=Image.open(south).convert('RGB'); sei=Image.open(southeast).convert('RGB')
assert ei.size==si.size==sei.size==(4096,4096)
pair=Image.new('RGB',(320,4096)); pair.paste(im.crop((3936,0,4096,4096)),(0,0)); pair.paste(ei.crop((0,0,160,4096)),(160,0))
board=Image.new('RGB',(1340,1084),'#191f20'); draw=ImageDraw.Draw(board)
for i in range(4):
    draw.text((12+332*i,28),f'east diagnostic y{i*1024}..{(i+1)*1024-1}',fill='white')
    board.paste(pair.crop((0,i*1024,320,(i+1)*1024)),(12+332*i,48))
ep=out/'east-c07-c08-unselected-diagnostic.png'; board.save(ep)
j=Image.new('RGB',(512,512)); j.paste(im.crop((3840,3840,4096,4096)),(0,0)); j.paste(ei.crop((0,3840,256,4096)),(256,0)); j.paste(si.crop((3840,0,4096,256)),(0,256)); j.paste(sei.crop((0,0,256,256)),(256,256))
jp=out/'southeast-four-tiles-c08-unselected-diagnostic.png'; j.save(jp)
repair=[]
for name,rect in [('priority-cross-x2048-y3072',(1421,2445,2675,3699)),('priority-cross-x3072-y1024',(2445,397,3699,1651))]:
    p=out/(name+'.png'); im.crop(rect).save(p)
    repair.append({'id':name,'file':str(p),'sha256':sha(p),'sourceRectLTRB':rect,'pixels':[1254,1254],'resized':False,'purpose':'native repair guide only, not completed repair'})
record={'schemaVersion':1,'createdAtUtc':stamp(),'source':{'file':str(source),'sha256':sha(source),'pixels':list(im.size)},'previousManifest':{'file':str(old),'sha256':sha(old)},'verifiedBoards':checks,'diagnosticSources':[{'file':str(p),'sha256':sha(p),'selected':p!=east} for p in [source,east,south,southeast]],'newDiagnosticBoards':[{'id':'east-unselected','file':str(ep),'sha256':sha(ep),'pixels':list(board.size),'assembly':'c07 [3936,0,4096,4096] plus c08 [0,0,160,4096], 1:1, segments [0,1024),[1024,2048),[2048,3072),[3072,4096)'},{'id':'southeast-unselected','file':str(jp),'sha256':sha(jp),'pixels':list(j.size),'assembly':'256 px each corner; NW c07 bottom-right, NE unselected c08 bottom-left, SW r09c07 top-right, SE r09c08 top-left; no scaling'}],'repairGuides':repair,'sourceUnchangedAtEnd':sha(source)==m['source']['sha256'],'preparationDoesNotImplyVisualPass':True}
(out/'native-verification.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'file':str(out/'native-verification.json'),'sha256':sha(out/'native-verification.json'),'sourceSha256':sha(source),'verifiedBoards':len(checks),'newBoards':record['newDiagnosticBoards'],'repairGuides':repair},ensure_ascii=False))
