"""Place five retained native repairs; no generated art enlargement."""
from pathlib import Path
from datetime import datetime, timezone
from PIL import Image
import numpy as np
import hashlib, json, sys
P = Path(__file__).resolve().parent
sys.path.insert(0, str(P.parents[1] / 'tools'))
from mechanical_join import registered_join
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
O, Q = P / 'output_v4', P / 'qa_v4'
O.mkdir(exist_ok=False); Q.mkdir()
source = P / 'output_v1/quad-extended-context.png'
canvas = np.array(Image.open(source).convert('RGB')); original = canvas.copy()
plan = json.loads((P / 'repairs/v2/plan.json').read_text())
touched = np.zeros(canvas.shape[:2], bool); placements = []
for e in plan['entries']:
    ident = e['id']; selected = ident + '.v2' if ident == 'internal_curved_rails' else ident
    native = P / 'repairs/v2/native' / (selected + '.png')
    record = native.with_suffix('.record.json'); rec = json.loads(record.read_text())
    assert sha(native) == rec['outputSha256'] == sha(rec['sourceOutputPath'])
    assert sha(rec['promptFile']) == rec['promptSha256']
    assert all(sha(r['path']) == r['sha256'] for r in rec['submittedImages'])
    with Image.open(native) as im:
        im.load(); assert im.size == (1254, 1254)
        assert im.mode != 'RGBA' or im.getextrema()[3] == (255,255)
        raw = np.array(im.convert('RGB'))
    roi = [440, 350, 850, 1205] if ident == 'internal_curved_rails' else e['roi']
    l,t,r,b = roi; x,y,_,_ = e['box']; ex,ey = x+l+115,y+t+115
    patch = raw[t:b,l:r]; h,w = patch.shape[:2]
    context = canvas[ey:ey+h,ex:ex+w].copy()
    yy,xx = np.indices((h,w), dtype=np.float32)
    d = np.minimum.reduce([xx,w-1-xx,yy,h-1-yy])
    a = np.clip((d-8)/64,0,1); mask = np.rint(a*a*(3-2*a)*255).astype(np.uint8)
    args = dict(max_shift=8,flow_inner=100,flow_full=40,tone_inner=150,tone_full=60)
    result,flow,tone,report = registered_join(context,patch,mask,**args)
    canvas[ey:ey+h,ex:ex+w] = result
    touched[ey:ey+h,ex:ex+w] |= mask > 0
    fields = O / (ident + '.fields.npz'); np.savez_compressed(fields,flow=flow,colorCorrection=tone,mask=mask)
    placements.append(dict(id=ident,selectedNative=selected,box=e['box'],roi=roi,
        native=str(native),nativeSha256=sha(native),record=str(record),recordSha256=sha(record),
        fields=str(fields),fieldsSha256=sha(fields),registration=report))
assert np.array_equal(canvas[~touched],original[~touched])
del original,touched
Image.fromarray(canvas).save(O / 'quad-extended-context.png')
quad = Image.fromarray(canvas[115:8307,115:8307]); quad.save(O / 'quad_8192_candidate.png')
row_source = P / 'output_v1/row10-extended-context.png'
row = np.array(Image.open(row_source).convert('RGB')); old_far = row[:,8422:].copy()
row[:,:8422] = canvas[4096:]; del canvas
assert np.array_equal(row[:,8422:],old_far); del old_far
Image.fromarray(row).save(O / 'row10-extended-context.png')
rim = Image.fromarray(row[115:4211,115:16499]); del row
rim.save(O / 'row10_16384_candidate.png')
files = []
for r,cs,im in [(9,(7,8),quad),(10,(7,8,9,10),rim)]:
    for c in cs:
        path = O / f'r{r:02}_c{c:02}.png'
        im.crop(((c-7)*4096,0,(c-6)*4096,4096)).save(path)
        files.append(dict(tile=path.stem,path=str(path),sha256=sha(path)))
assert np.array_equal(np.concatenate([np.array(Image.open(O/f'r10_c{c:02}.png')) for c in (7,8,9,10)],1),np.array(rim))
assert np.array_equal(np.concatenate([np.concatenate([np.array(Image.open(O/f'r{r:02}_c{c:02}.png')) for c in (7,8)],1) for r in (9,10)],0),np.array(quad))
for e in plan['entries']: quad.crop(e['box']).save(Q / (e['id'] + '_reconnected.png'))
qa_files = []
def save_board(name, parts):
    board = Image.new('RGB',(320*len(parts),1024))
    for i,part in enumerate(parts):
        assert part.size == (320,1024)
        board.paste(part,(i*320,0))
    path = Q / (name + '.png'); board.save(path); qa_files.append(str(path))
tile = quad.crop((4096,0,8192,4096))
for axis in ('v','h'):
    for pos in (1024,2048,3072):
        strip = tile.crop((pos-160,0,pos+160,4096)) if axis=='v' else tile.crop((0,pos-160,4096,pos+160)).transpose(Image.Transpose.ROTATE_90)
        save_board(f'internal_{axis}{pos}',[strip.crop((0,i*1024,320,(i+1)*1024)) for i in range(4)])
for axis in ('v','h'):
    strip = quad.crop((3936,0,4256,8192)) if axis=='v' else quad.crop((0,3936,8192,4256)).transpose(Image.Transpose.ROTATE_90)
    for half in (0,1):save_board(f'quad_boundary_{axis}_half{half+1}',[strip.crop((0,i*1024,320,(i+1)*1024)) for i in range(half*4,half*4+4)])
for c in (1,2,3):save_board(f'row10_boundary_c{c+7:02}',[rim.crop((c*4096-160,i*1024,c*4096+160,(i+1)*1024)) for i in range(4)])
j = Image.new('RGB',(768,768))
for yi,y in enumerate((1024,2048,3072)):
    for xi,x in enumerate((1024,2048,3072)):j.paste(tile.crop((x-128,y-128,x+128,y+128)),(xi*256,yi*256))
j.save(Q/'internal-nine-junctions.png')
quad.crop((3584,3584,4608,4608)).save(Q/'four-tile-junction.png')
quad.resize((1400,1400),Image.Resampling.LANCZOS).save(Q/'quad-overview.jpg',quality=93)
report = dict(createdAtUtc=datetime.now(timezone.utc).isoformat(),status='five_native_repairs_placed_pending_full_visual_qa',
    parent=dict(path=str(source),sha256=sha(source)),scriptSha256=sha(__file__),files=files,placements=placements,
    qaNativePixelBoards=qa_files,outsideMasksUnchanged=True,row10FarRightUnchanged=True,exactTileRejoinVerified=True,
    sourceArtUpscaled=False,limitedSeamResampling=True,runtimePublished=False,accepted=False)
(P/'assembly_v4.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(dict(status=report['status'],files=len(files),qaBoards=len(qa_files))))
