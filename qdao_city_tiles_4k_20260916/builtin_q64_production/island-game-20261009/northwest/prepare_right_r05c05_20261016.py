from pathlib import Path
from types import SimpleNamespace
import argparse,json,hashlib
from PIL import Image
import prepare_zone_patch as prepare
Z=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
fi=lambda p:dict(path=p.as_posix(),sha256=sha(p))
p=argparse.ArgumentParser();p.add_argument('--row',type=int,required=True);p.add_argument('--col',type=int,required=True);p.add_argument('--attempt',default='a01')
for di in ('left','right','top','bottom'):p.add_argument('--'+di)
a=p.parse_args();assert 1<=a.row<=4 and 1<=a.col<=4
split=json.loads((Z.parents[3]/'docs/MAP_PARALLEL_SPLIT_20261013.json').read_text(encoding='utf8')) if False else json.loads(Path('D:/work/image/docs/MAP_PARALLEL_SPLIT_20261013.json').read_text(encoding='utf8'))
reserved=[t for b in split['batches'] if b['map']=='island-game-20261009' and b['owner']=='01a1216d-5a60-7332-b4ee-8acad0d64dba' and b['status']=='allocated_root_reserved' for t in b['tiles']]
assert 'r05_c05' not in reserved and len(reserved)>=10
base=Z/'tiles/connected-r05-r06-cross-v3/r05_c04_paving-north-v1_4096.png';record=base.with_suffix('.cross-native-repair.json')
assert sha(base)=='496cf0c0019fed1cdd716b44891167a8d7eaae6c45272cd096d20e5201cbaa9b'
assert sha(record)=='7e5754b6bc0e6a9e385aafaabb74cdab9de8c7723f13e492ef3ae272c93577e0'
anchor=None
if a.col==1:
 cache=Z/'guides/r05_c05_fixed_west_r05_c04_cross_v5_anchors_20261016.json'
 if not cache.exists():
  im=Image.open(base).convert('RGB');assert im.size==(4096,4096);entries=[]
  for i in range(1,5):
   ay=max(0,min((i-1)*1024-115,4096-1254));box=[2842,ay,4096,ay+1254]
   f=Z/f'guides/r05_c05_fixed_west_r05_c04_cross_v5_{i:02d}_anchor_20261016.png';assert not f.exists();im.crop(box).save(f)
   entries.append({**fi(f),'nativeSize':[1254,1254],'index':i,'sourceCoreRowY':(i-1)*1024-ay,'globalBox':[12288+box[0],16384+box[1],12288+box[2],16384+box[3]],'kind':'exact_current_formal_tile_crop_reference_only','derivedFrom':{'image':fi(base),'record':fi(record),'tileCropBoxHalfOpen':box},'resizing':False,'registration':False,'pixelSynthesis':False})
  with cache.open('x',encoding='utf8') as f:json.dump({'source':fi(base),'record':fi(record),'anchors':entries,'policy':'Only actual 115px east formal core is pasted; overview corners are not native art. No old outside-core halo.'},f,indent=2)
 data=json.loads(cache.read_text());assert data['source']==fi(base) and data['record']==fi(record)
 anchor=next(e for e in data['anchors'] if e['index']==a.row);assert sha(anchor['path'])==anchor['sha256'];a.left='fixed-west-core'
original=prepare.load_neighbor
def load(stem,direction,target,contract):
 if stem!='fixed-west-core':return original(stem,direction,target,contract)
 sy=anchor['sourceCoreRowY'];b=target['globalBox']
 entry={**anchor,'direction':'left','sourceZone':'northwest','sourceCrop':[1139,sy,1254,sy+1024],'destination':[0,115],'targetLocalBox':[0,115,115,1139],'globalOverlapBox':[b[0],b[1]+115,b[0]+115,b[1]+1139],'coordinateEvidence':fi(cache),'resized':False,'sameTile':False,'role':'Approved current west neighbor exact east115 actual formal core, no old halo','haloPolicy':'Only actual 1024 tall west core edge; upper/lower115 corners are unanchored layout until another native neighbor supplies them.'}
 return entry,Image.open(anchor['path']).convert('RGB')
prepare.load_neighbor=load
r=prepare.prepare(SimpleNamespace(tile_row=5,tile_col=5,subrow=a.row,subcol=a.col,attempt=a.attempt,left=a.left,right=a.right,top=a.top,bottom=a.bottom,output_dir=None))
print(json.dumps({'guide':r['guide']['path'],'input':r['input'],'references':r['references'],'reservedExcluded':reserved}))

