from workflow import *
from PIL import Image
import sys,os,subprocess,re
tid='r08_c13';p=read(ROOT/f'progress-{tid}.json');vv=p['workingVersions']
desc={
'23':'Continue the existing ivory balustrade wall foot cropped along the upper/left part. The wall face continues from exact TOP/LEFT anchors without extra posts or tiers. Below/right is a narrow green planted verge with small existing white/pink flowers and plain broad pale-grey courtyard slabs. RIGHT has the existing large pale rock/garden portion continued exactly. Preserve the one continuous diagonal wall and open paving. No miniature fence, new separate rock group, medallions or colored paving bands.',
'32':'Close crop of the existing large ivory stone pillar lower portion and its base in upper-left, connected to the wall continuing across upper edge. Precisely complete the partial pillar/base crossing the LEFT/TOP anchors; do not fit a new whole pillar, cap or finial. Existing dense green and white-flowered canopy covers left/lower portions, while plain pale-grey paving opens to right. Continue the exact selected BOTTOM foliage edge and slab scale without a guide rectangle. No extra posts or new ornaments.',
'33':'Plain continuous pale-grey blue-grey stone courtyard paving in most of the crop, matching all four exact selected native edge anchors. Keep existing cropped garden/rock and wall-side plants only where the anchor or coordinate guide actually contains them. Broad stone slabs with weak diagonal joints, restrained painted grain and daylight shadow; no medallion, decorative bands, fence or new rock in the open middle.'}
for rc in sys.argv[1:]:
 pid=f'{tid}_p{rc}';v='v01';assert not (ROOT/'native'/f'{pid}_{v}.png').exists();box=patch(pid)['nativeGlobalBox'];layout=ROOT/'guides'/f'{pid}.layout-only.png';im=Image.open(layout).convert('RGB');parts=[]
 for nr,nv in vv.items():
  if nr==rc:continue
  src=ROOT/'native'/f'{tid}_p{nr}_{nv}.png';b=patch(f'{tid}_p{nr}')['coreGlobalBox'];inter=[max(box[0],b[0]),max(box[1],b[1]),min(box[2],b[2]),min(box[3],b[3])]
  if inter[0]>=inter[2] or inter[1]>=inter[3]:continue
  crop=[inter[0]-b[0]+115,inter[1]-b[1]+115,inter[2]-b[0]+115,inter[3]-b[1]+115];dest=[inter[0]-box[0],inter[1]-box[1]];im.paste(Image.open(src).convert('RGB').crop(crop),dest);parts.append({'file':str(src),'sha256':sha(src),'sourceCrop':crop,'destination':dest,'sourceIsSelectedCore':True})
 g=ROOT/'guides'/f'{pid}.selected-core-context-20261016.png';assert not g.exists();im.save(g);write(Path(str(g)+'.generation.json'),{'usableAsFinalArt':False,'nativeGlobalBox':box,'layoutGuide':str(layout),'parts':parts,'operation':'Exact selected-core native intersections pasted only into target outer115 halo; no neighbor unselected halo frozen.'})
 env=dict(os.environ,ISLAND_PROGRESS_FILE=f'progress-{tid}.json');rr=subprocess.run([sys.executable,str(ROOT/'request.py'),pid,v,desc[rc]],check=True,env=env,capture_output=True,text=True);a=json.loads(rr.stdout);a['referenced_image_paths'][0]=str(g)
 a['prompt']=a['prompt'].replace('A horizontal neighbor contributes its rightmost 230 pixels to this crop\'s leftmost 230 pixels; a vertical neighbor contributes its bottommost 230 pixels to this crop\'s topmost 230 pixels.','All sharp strips are exact selected neighbor-core pixels in this crop\'s outer 115-pixel halo only. Continue them naturally into the central 1024-pixel core. Unselected neighbor halo pixels are deliberately not frozen.')
 af=ROOT/'prompts'/f'{pid}_{v}.args.json';write(af,a);rf=ROOT/'prompts'/f'{pid}_{v}.request.json';rq=read(rf);rq['references'][0].update(file=str(g),sha256=sha(g),role='Exact selected neighbor-core context only in outer115px halo; central core must be generated');Path(rq['promptPath']).write_text(a['prompt'],encoding='utf-8');write(rf,rq);print(af)
