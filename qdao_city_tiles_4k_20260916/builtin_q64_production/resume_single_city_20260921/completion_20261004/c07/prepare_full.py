import datetime,hashlib,json
from pathlib import Path
from PIL import Image
R=Path(__file__).resolve().parent;S=R.parents[1];A=S.parents[1];REPO=A.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
state=json.loads((S/'continuation_20261004/current-work.json').read_text(encoding='utf-8-sig'))
item=next(x for x in state['currentOutputs'] if x['tile']=='r08_c07');source=A/item['candidate']['file'];assert sha(source)==item['candidate']['sha256']
R.mkdir(exist_ok=True);q=R/'baseline-qa';q.mkdir(exist_ok=False)
with Image.open(source) as im:
 im.load();assert im.size==(4096,4096)
 entries=[]
 for axis in ['vertical','horizontal']:
  for at in [1024,2048,3072]:
   board=Image.new('RGB',(768,2048) if axis=='vertical' else (2048,768))
   parts=[]
   for n in range(4):
    rect=[at-192,n*1024,at+192,(n+1)*1024] if axis=='vertical' else [n*1024,at-192,(n+1)*1024,at+192]
    xy=[(n%2)*384,(n//2)*1024] if axis=='vertical' else [(n%2)*1024,(n//2)*384]
    board.paste(im.crop(rect),xy);parts.append({'cropLTRB':rect,'pasteXY':xy})
   p=q/f'{axis}-{at}.png';board.save(p);entries.append({'file':str(p),'sha256':sha(p),'parts':parts,'resized':False,'source':str(source),'sourceSha256':sha(source)})
 board=Image.new('RGB',(1152,1152));rects=[]
 for ri,y in enumerate([1024,2048,3072]):
  for ci,x in enumerate([1024,2048,3072]):
   rect=[x-192,y-192,x+192,y+192];board.paste(im.crop(rect),(ci*384,ri*384));rects.append(rect)
 p=q/'junctions-nine.png';board.save(p);entries.append({'file':str(p),'sha256':sha(p),'cropLTRB':rects,'resized':False})
 im.resize((1024,1024),Image.Resampling.LANCZOS).save(q/'overview-preview-only.png')
(q/'index.json').write_text(json.dumps({'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':item,'entries':entries},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
full=R/'full-native-attempt';full.mkdir(exist_ok=False)
prompt='''Use case: precise-object-edit. Repair this game-city-map tile as one seamless native 4096x4096 pixel artwork. Return a genuine 4096 by 4096 output at the identical source scale and crop, with crisp native detail throughout. Do not upscale a smaller image.
Reference image 1 is the exact fixed-layout 4096-square edit target. Its paving, curved rings, inset panels, cloud-carved slab motifs, true grout, tiny round gold fitting and camera geometry must remain in exactly the same places and sizes. It contains unwanted artificial assembly seams on the three full-height grid lines x=1024,2048,3072 and the three full-width grid lines y=1024,2048,3072. These are sharp rectangular material/lighting changes, small edge steps and false joins through continuous stone, gold trims and carvings. Eliminate those artificial grid discontinuities over their full lengths and all nine intersections, matching existing curves and bevel trajectories smoothly across them. Preserve every genuine stone boundary and engraved shape.
Keep the entire scene aligned with the source. No zoom, crop, rotate, camera or perspective change; no redesign, new slabs, new objects, extra grooves, characters, text, UI, labels or border. Match the four outer tile edges with the original as closely as possible. Clean warm ivory and calm blue-gray stone, thin gold, rounded bevels, soft upper-left lighting, restrained native fine detail; no clouds, cracks, noisy speckles, blur, artificial sharpening, doubled contours or repeated image tiles. The slab surfaces should have unified material inside each real slab and retain gentle shading.
Reference image 2 is the approved original project's Daoist Q-style finish reference only. Borrow its rounded clean high-quality hand-painted material and warm restrained finish, never its interface, objects, writing, people or layout. Reference image 3 is a small native clean ivory material sample for appearance only; never stretch or paste it. Prioritize exact fixed geometry and a truly seamless final image at full native4096 resolution. Highest host-managed quality available.'''
refs=[str(source),str(REPO/'designs/gameplay-ui/04-guild.png'),str(S/'next_tile_r08_c08/correction-20260923T114016880544Z/native-ivory-material-reference.png')]
request={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False}
(full/'request.json').write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(full/'prompt.txt').write_text(prompt,encoding='utf-8');(full/'config.snapshot.json').write_bytes((REPO/'config/image-generation.json').read_bytes())
(full/'references.json').write_text(json.dumps([{'file':p,'sha256':sha(p),'role':role} for p,role in zip(refs,['full4096_edit_target','approved_style','native_material_sample'])],ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(R/'baseline.json').write_text(json.dumps({'source':item,'purpose':'complete_tile_interior_seams_and_junctions','formalAccepted':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'source':str(source),'request':str(full/'request.json'),'baselineQA':str(q)},ensure_ascii=False))
