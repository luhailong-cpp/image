"""Publish an explicitly reviewed selected tile without whole-city acceptance."""
from pathlib import Path
from datetime import datetime, timezone
import argparse,hashlib,json,re
from PIL import Image
B=Path(__file__).resolve().parent.parent
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,d): Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=argparse.ArgumentParser(); p.add_argument('tile'); p.add_argument('--next-tile',required=True); a=p.parse_args()
assert re.fullmatch(r'r\d{2}_c\d{2}',a.tile) and re.fullmatch(r'r\d{2}_c\d{2}',a.next_tile)
folder=B/a.tile/'selected'; mf=folder/'delivery.manifest.json'; m=read(mf)
assert m['tile']==a.tile and m['qualifiedComplete4KCandidate'] is True
for key,size in [('core',(4096,4096)),('extended',(4326,4326))]:
 rec=m['outputs'][key]; assert sha(rec['file'])==rec['sha256']
 with Image.open(rec['file']) as im: assert im.size==size
with Image.open(m['outputs']['extended']['file']) as ext, Image.open(m['outputs']['core']['file']) as core:
 assert ext.convert('RGB').crop((115,115,4211,4211)).tobytes()==core.convert('RGB').tobytes()
selection=read(B/'current-selection.json')
tiles=[x for x in selection['currentCandidates'] if x['tile']!=a.tile]
tiles.append({'tile':a.tile,**m['outputs']['core'],'halo':m['outputs']['extended'],'deliveryManifest':mf.as_posix(),'qualifiedComplete4KCandidate':True,'formalAccepted':False,'status':m['status']})
tiles.sort(key=lambda x:x['tile'])
for entry in tiles: assert sha(entry['file'])==entry['sha256']
now=datetime.now(timezone.utc).isoformat()
selection.update(updatedAtUtc=now,currentCandidates=tiles,candidateCount=len(tiles),formalAccepted=0,wholeCityComplete=False,runtimePublished=False)
write(B/'current-selection.json',selection)
for name in ('progress.json','current-work.json'):
 d=read(B/name); d.update(updatedAtUtc=now,status='partial_city_shared_geometry_production',currentTile=a.next_tile,currentPhase='neighbor_source_refresh_and_regional_preparation',newComplete4KCandidates=len(tiles)-3,currentCandidateCount=len(tiles),remainingCoverageTiles=256-len(tiles),formalAccepted=0,wholeCityComplete=False,runtimePublished=False,currentSelection='current-selection.json',nextAction=f'Refresh {a.next_tile} from the selected neighbors and continue native shared-geometry production.')
 d.pop('currentNativePresent',None); d.pop('currentNativeRequired',None); write(B/name,d)
row=int(a.tile[1:3]); col=int(a.tile[5:7]); west_id=f'r{row:02d}_c{col-1:02d}'
west=next((x for x in tiles if x['tile']==west_id),None); current=next(x for x in tiles if x['tile']==a.tile)
pair=[west,current] if west else [current]
preview=Image.new('RGB',(1024*len(pair),1024))
for i,entry in enumerate(pair):
 with Image.open(entry['file']) as im: preview.paste(im.convert('RGB').resize((1024,1024),Image.Resampling.LANCZOS),(i*1024,0))
pp=B/'current-preview.png'; preview.save(pp)
write(str(pp)+'.generation.json',{'file':str(pp),'sha256':sha(pp),'role':'spatial_adjacent_selected_core_preview' if west else 'selected_core_preview','previewOnly':True,'productionPixelsAllowed':False,'sources':pair,'operation':'4096 core to1024 display downsample only','formalAccepted':False})
print(json.dumps({'candidateCount':len(tiles),'selected':a.tile,'nextTile':a.next_tile,'formalAccepted':0}))
