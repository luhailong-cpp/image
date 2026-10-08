"""Export exact-pixel seam views from one ready cell; never grants approval.

Usage: python export_ready_cell_qa.py r09_c08 ROW COL
Requires current cell and available north/east sources, bound by their records.
Existing exports are not overwritten. Each crop maps exactly to final tile QA.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, hashlib,json
from PIL import Image
from workflow import OUTPUT_ROOT,safe_output,sha256,read_json,save_image,write_json

def rgb(im): return hashlib.sha256(im.convert('RGB').tobytes()).hexdigest()

def run(name,row,col):
 assert 1<=row<=4 and 1<=col<=4
 tile=safe_output(OUTPUT_ROOT/name)
 assert tile.parent==OUTPUT_ROOT
 cell=f'r{row:02d}_c{col:02d}'
 out=safe_output(tile/'ready-cell-qa'/cell)
 assert not out.exists(), 'Refusing to overwrite previous QA evidence'
 context=read_json(tile/'regional/context.json')
 sources={}
 def source(p,expected,size,record=None):
  p=Path(p).resolve(strict=True)
  assert sha256(p)==expected
  im=Image.open(p).convert('RGB'); assert im.size==size
  r={'file':str(p),'sha256':expected,'pixels':list(size)}
  if record:r['generationRecord']={'file':str(record),'sha256':sha256(record)}
  sources[str(p)]=(im,r)
  return im,r
 def native(r,c):
  p=tile/f'native/r{r:02d}_c{c:02d}.png';record=Path(str(p)+'.generation.json');g=read_json(record)
  return source(p,g['sha256'],(1254,1254),record)
 current,cr=native(row,col)
 if row>1:
  north,nr=native(row-1,col);nb=[115,1011,1139,1139]
 else:
  e=context['northCore'];north,nr=source(e['file'],e['sha256'],(4096,4096));x=(col-1)*1024;nb=[x,3840,x+1024,4096]
 if col<4:
  east,er=native(row,col+1);eb=[115,115,243,1139]
 else:
  e=context['eastCore'];east,er=source(e['file'],e['sha256'],(4096,4096));y=(row-1)*1024;eb=[0,y,256,y+1024]
 out.mkdir(parents=True)
 checks=[]
 def export(label,size,parts,kind,final_box=None):
  board=Image.new('RGB',size);maps=[]
  for image,reference,box,xy in parts:
   crop=image.crop(box);board.paste(crop,xy)
   maps.append({'source':reference,'sourceBoxXYXY':box,'destinationXY':list(xy),'decodedRgbSha256':rgb(crop)})
  e=save_image(out/(label+'.png'),board)
  e.update(kind=kind,cell=cell,pixelMappings=maps,decodedRgbSha256=rgb(board),
    operation='integer crop/paste only',resampling='none',actuallyViewed=False,reviewStatus='pending')
  if final_box:e['finalCoreBoxXYXY']=final_box
  checks.append(e)
 x,y=(col-1)*1024,(row-1)*1024
 half_n=128 if row>1 else 256
 export('north',(1024,half_n*2),[(north,nr,nb,(0,0)),(current,cr,[115,115,1139,115+half_n],(0,half_n))],
   'internal_north' if row>1 else 'external_north', [x,y-128,x+1024,y+128] if row>1 else None)
 half_e=128 if col<4 else 256
 export('east',(half_e*2,1024),[(current,cr,[1139-half_e,115,1139,1139],(0,0)),(east,er,eb,(half_e,0))],
   'internal_east' if col<4 else 'external_east', [x+896,y,x+1152,y+1024] if col<4 else None)
 export('east-guide',(128,1024),[(current,cr,[960,115,1088,1139],(0,0))],
   'east_guide_transition',[x+845,y,x+973,y+1024])
 if row>1 or context.get('northContextKind')!='partial_core_band':
  export('north-guide',(1024,128),[(current,cr,[115,166,1139,294],(0,0))],
   'north_guide_transition',[x,y+51,x+1024,y+179])
 manifest={'schemaVersion':1,'tile':name,'cell':cell,'createdAtUtc':datetime.now(timezone.utc).isoformat(),
   'currentCell':cr,'checks':checks,'actuallyViewed':False,'reviewStatus':'pending',
   'limitations':'Individual ready-cell scopes only; no intersections, formal or complete-tile acceptance.'}
 write_json(out/'manifest.json',manifest)
 print(json.dumps({'manifest':str(out/'manifest.json'),'checks':len(checks)}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('tile');p.add_argument('row',type=int);p.add_argument('col',type=int)
 a=p.parse_args();run(a.tile,a.row,a.col)
