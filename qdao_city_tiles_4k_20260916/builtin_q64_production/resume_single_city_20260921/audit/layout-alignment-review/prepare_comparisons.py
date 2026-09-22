from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
OUT=Path(__file__).resolve().parent
SESSION=OUT.parents[1]
REPO=SESSION.parents[2]
MASTER=REPO/'tianyong_festival_hd_20260910/tianyong_city_master_6144.png'
PLAZA=REPO/'qdao_city_tiles_4k_20260916/builtin_4x4/output/tianyong_plaza_4k_candidate_v3b.png'
C09=SESSION/'tools/repairs/versions/r09_c09_repair_v6/r09_c09.png'
C10=SESSION/'next_tile_r09_c10/output/r09_c10.candidate.png'
NAV=REPO/'tianyong_festival_hd_20260910/runtime/navigation.json'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
master=Image.open(MASTER).convert('RGB');plaza=Image.open(PLAZA).convert('RGB')
nav=json.loads(NAV.read_text(encoding='utf-8'))
manifest={'purpose':'Geometry-only visual comparison, intentionally scaled to shared map coordinates; NOT100-percent detail QA or production artwork',
 'sourceFiles':[{'file':str(p),'sha256':sha(p)} for p in [MASTER,PLAZA,C09,C10,NAV]],'evidence':[]}
def emit(name,img,info):
 p=OUT/(name+'.jpg');img.save(p,quality=97,subsampling=0)
 manifest['evidence'].append({'file':str(p),'sha256':sha(p),'pixels':list(img.size),'role':'analysis preview only','resized':True,**info})
def board(panels,labels,w=768):
 im=Image.new('RGB',(len(panels)*w, w+32),(25,25,25));d=ImageDraw.Draw(im)
 for k,(p,label) in enumerate(zip(panels,labels)):
  im.paste(p.resize((w,w),Image.Resampling.LANCZOS),(k*w,32));d.text((k*w+8,8),label,fill='white')
 return im
center=master.crop((2048,2048,4096,4096))
emit('plaza_geometry_overview',board([center,plaza],['MASTER original crop [2048,2048,4096,4096] at 1/2','GENERATED plaza4096 at 1/4'],1024),{'nominalMasterCropLTRB':[2048,2048,4096,4096]})
overview=master.resize((1024,1024),Image.Resampling.LANCZOS);d=ImageDraw.Draw(overview)
d.rectangle((2048/6,2048/6,4096/6,4096/6),outline='red',width=3)
for r,c in [(8,9),(8,10),(9,9),(9,10),(9,11)]:
 x=(c-1)*384/6;y=(r-1)*384/6;d.rectangle((x,y,x+64,y+64),outline='cyan',width=2);d.text((x,y+4),f'{r},{c}',fill='cyan')
emit('master_city_locator',overview,{'fullMasterPixels':[6144,6144],'redBox':'nominal local plaza source','cyanTiles':'next/active tile regions'})
for row,col,candidate in [(9,9,C09),(9,10,C10),(8,9,None),(8,10,None),(9,11,None)]:
 x=(col-1)*384;y=(row-1)*384
 pb=[2*(x-2048),2*(y-2048),2*(x+384-2048),2*(y+384-2048)]
 panels=[master.crop((x,y,x+384,y+384))];labels=['MASTER original384px enlarged2x for geometry']
 p=Image.new('RGB',(768,768),(90,20,80));inter=(max(0,pb[0]),max(0,pb[1]),min(4096,pb[2]),min(4096,pb[3]))
 if inter[0]<inter[2] and inter[1]<inter[3]:p.paste(plaza.crop(inter),(inter[0]-pb[0],inter[1]-pb[1]))
 panels.append(p);labels.append('PLAZA nominal768px (purple=NO SOURCE)')
 if candidate:panels.append(Image.open(candidate).convert('RGB'));labels.append('Q64 candidate4096px reduced for geometry')
 emit(f'r{row:02d}_c{col:02d}_geometry',board(panels,labels),{'masterCropLTRB':[x,y,x+384,y+384],'plazaNominalCropLTRB':pb,'candidate':str(candidate) if candidate else None})

# Same-coordinate navigation overlay on the authoritative master and nominal plaza.
for source,label,scale,offset in [(center,'master',1024/2048,(2048,2048)),(plaza,'plaza',1024/4096,(4096,4096))]:
 result=source.resize((1024,1024),Image.Resampling.LANCZOS);d=ImageDraw.Draw(result)
 for category,color in [('regions',(0,255,150)),('obstacles',(255,40,70))]:
  for name,poly in nav[category].items():
   points=[]
   for nx,ny in poly:
    sx=nx*6144/896;sy=ny*6144/896
    px=(sx-2048)*.5;py=(sy-2048)*.5
    points.append((px,py))
   d.line(points+[points[0]],fill=color,width=2)
 for name,pt in nav['probes'].items():
  x=(pt[0]*6144/896-2048)*.5;y=(pt[1]*6144/896-2048)*.5
  if 0<=x<1024 and 0<=y<1024:d.ellipse((x-4,y-4,x+4,y+4),fill='cyan');d.text((x+6,y),name,fill='cyan')
 emit(f'{label}_navigation_overlay',result,{'sameNominalMapCoordinates':True,'green':'walkable region boundary','red':'obstacle outline','cyan':'existing navigation probes','semanticAcceptance':False})
(OUT/'comparison-manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'files':len(manifest['evidence']),'repo':str(REPO)},indent=2))
