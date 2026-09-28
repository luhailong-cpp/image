from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json
from datetime import datetime, timezone

ROOT = Path('E:/work/image')
ART = ROOT / 'qdao_city_tiles_4k_20260916'
SESSION = ART / 'builtin_q64_production/resume_single_city_20260921'
OUT = SESSION / 'continuation_20260925T132104Z/qa-c07'
POINTER = SESSION / 'next_tile_r08_c07/latest-candidate.json'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc(): return datetime.now(timezone.utc).isoformat()
pointer_bytes = POINTER.read_bytes()
pointer = json.loads(pointer_bytes)
source = ART / pointer['candidate']['file']
assert sha(source) == pointer['candidate']['sha256']
im = Image.open(source); im.load()
assert im.size == (4096,4096)
manifest = {'schemaVersion':1, 'createdAtUtc':utc(), 'purpose':'fresh_visual_QA_not_formal_acceptance',
 'source':{'file':str(source),'sha256':sha(source),'pixels':list(im.size)},
 'pointer':{'file':str(POINTER),'sha256':hashlib.sha256(pointer_bytes).hexdigest()},
 'nativePixelRule':'Every source crop pasted 1:1 without resizing, filtering, color correction or overlay; only captions and gutters added outside crop rectangles.',
 'boards':[], 'externalPending':[]}

def save_board(name, board, pieces, kind):
 p = OUT / (name+'.png'); board.save(p)
 manifest['boards'].append({'id':name,'kind':kind,'file':str(p),'sha256':sha(p),'pixels':list(board.size),'pieces':pieces})

def seam_board(name, vertical, coordinate, seam_image=None, source_refs=None):
 # Four exact 1024-pixel longitudinal segments cover the full 4096-pixel seam.
 width = 320
 board = Image.new('RGB',(4*(width+12)+12,1084) if vertical else (1048,4*(width+36)+12),(25,30,32))
 draw = ImageDraw.Draw(board); pieces=[]
 for q in range(4):
  a,b=q*1024,(q+1)*1024
  if seam_image is None:
   rect=(coordinate-160,a,coordinate+160,b) if vertical else (a,coordinate-160,b,coordinate+160)
   crop=im.crop(rect)
  else:
   rect=(0,a,320,b) if vertical else (a,0,b,320)
   crop=seam_image.crop(rect)
  dest=(12+q*332,48) if vertical else (12,36+q*356)
  draw.text((dest[0],dest[1]-22),f'{name} segment {q+1}: {a}..{b-1}',fill='white')
  board.paste(crop,dest)
  pieces.append({'sourceRectLTRB':list(rect),'boardXY':list(dest),'pixels':list(crop.size),'longitudinalRange':[a,b],'seamAtCropPixel':160})
 save_board(name,board,pieces,'internal_full_seam' if seam_image is None else 'external_full_seam')
 if source_refs is not None: manifest['boards'][-1]['sourceComposition']=source_refs

for coord in (1024,2048,3072):
 seam_board(f'vertical-x{coord}',True,coord)
 seam_board(f'horizontal-y{coord}',False,coord)

board=Image.new('RGB',(1212,1272),(25,30,32)); draw=ImageDraw.Draw(board); pieces=[]
for row,y in enumerate((1024,2048,3072)):
 for col,x in enumerate((1024,2048,3072)):
  rect=(x-192,y-192,x+192,y+192); dest=(12+col*400,36+row*420)
  draw.text((dest[0],dest[1]-22),f'junction x{x} y{y}',fill='white')
  board.paste(im.crop(rect),dest)
  pieces.append({'sourceRectLTRB':list(rect),'boardXY':list(dest),'pixels':[384,384],'junctionXY':[x,y]})
save_board('internal-junctions-nine',board,pieces,'internal_junctions')

ledger_path=SESSION/'current-coverage-ledger.json'; ledger_bytes=ledger_path.read_bytes()
ledger=json.loads(ledger_bytes); tiles={t['tile']:t for t in ledger['tiles']}
manifest['ledger']={'file':str(ledger_path),'sha256':hashlib.sha256(ledger_bytes).hexdigest()}
south=tiles['r09_c07']['candidate']; sp=ART/south['file']
assert sha(sp)==south['sha256']; sim=Image.open(sp); sim.load(); assert sim.size==(4096,4096)
joined=Image.new('RGB',(4096,320)); joined.paste(im.crop((0,3936,4096,4096)),(0,0)); joined.paste(sim.crop((0,0,4096,160)),(0,160))
seam_board('south-r08_c07--r09_c07',False,160,joined,[{'file':str(source),'sha256':sha(source),'sourceRectLTRB':[0,3936,4096,4096],'destinationRectLTRB':[0,0,4096,160]},{'file':str(sp),'sha256':sha(sp),'sourceRectLTRB':[0,0,4096,160],'destinationRectLTRB':[0,160,4096,320]}])
for edge,tile in [('north','r07_c07'),('west','r08_c06'),('east','r08_c08')]:
 manifest['externalPending'].append({'type':'edge','edge':edge,'neighbor':tile,'status':'pending_missing_selected_neighbor','ledgerCandidateExists':tiles[tile]['candidateExists']})
for corner,neighbors in [('northwest',['r07_c06','r07_c07','r08_c06']),('northeast',['r07_c07','r07_c08','r08_c08']),('southwest',['r08_c06','r09_c06','r09_c07']),('southeast',['r08_c08','r09_c07','r09_c08'])]:
 manifest['externalPending'].append({'type':'four_tile_junction','corner':corner,'neighbors':neighbors,'missingSelectedNeighbors':[t for t in neighbors if not tiles[t]['candidateExists']],'status':'pending_missing_selected_neighbor'})
assert source.exists() and sha(source)==manifest['source']['sha256']
manifest['pointerUnchangedDuringCapture'] = POINTER.read_bytes()==pointer_bytes
manifest['sourceShaVerifiedAtUtc']=utc()
manifest['script']={'file':str(Path(__file__)),'sha256':sha(__file__)}
(OUT/'native-crops.manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'sourceSha256':manifest['source']['sha256'],'boards':[(b['id'],b['pixels']) for b in manifest['boards']],'pending':manifest['externalPending'],'pointerUnchanged':manifest['pointerUnchangedDuringCapture']},ensure_ascii=False))
