from pathlib import Path
from PIL import Image,ImageDraw
import sys,json,hashlib,datetime,shutil
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
import production as p
ROOT=Path(__file__).resolve().parent
p.ROOT=ROOT
STYLE='D:/work/image/designs/gameplay-ui/04-guild.png'
H=p.read(BASE/'handoff.json')
def init():
 for name in ['references','prompts','native','evidence','guides','qa','tiles']:(ROOT/name).mkdir(exist_ok=True)
 verified=[]
 for item in [H['plan'],H['layout'],H['baselineCandidates'][-1]]:
  fp=Path(item['file']);actual=p.sha(fp);assert actual==item['sha256']
  verified.append({'file':str(fp),'sha256':actual,'matchesHandoff':True})
 plan=p.read(H['plan']['file']);tile=next(x for x in plan['tiles'] if x['id']=='r10_c12')
 assert tile['finalPixelRect']==[45056,36864,4096,4096]
 p.write(ROOT/'evidence/input-verification.json',{'verifiedAt':p.stamp(),'inputs':verified})
 nav=Path('D:/work/mmorpg-client/Docs/CityTiles4K.md')
 p.write(ROOT/'plan.json',{'tile':tile,'halo':115,'core':1024,'nativePatch':[1254,1254],'grid':[4,4],'worldMapping':{'wholeCityWorldRectXYWH':[50,0,300,300],'YisWorldZ':True},'navigationSource':str(nav),'navigationSourceSha256':p.sha(nav),'sharedGeometry':'Day layout plus verified north tile constrain roof/water/harbor/routes. Festival independently generated references are not declared aligned. No movement/navigation runtime changes or acceptance; source navigation coordinates preserved.','formalAccepted':False})
 layout=Path(H['layout']['file']);im=Image.open(layout).convert('RGB');scale=1254/65536
 box=tuple(v*scale for v in [45056-115,36864-115,49152+115,40960+115])
 dest=ROOT/'references/layout-only.png';im.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(dest)
 p.derived(dest,[layout],{'method':'layout-only crop resampled, not final pixels','sourceBoxLTRB':box,'globalBoxLTRB':[44941,36749,49267,41075]})
 north=Path(H['baselineCandidates'][-1]['file']);im=Image.open(north).convert('RGB')
 dest=ROOT/'references/north-preview.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(dest);p.derived(dest,[north],{'method':'downscale context preview only'})
 dest=ROOT/'references/north-bottom115.png';im.crop((0,3981,4096,4096)).save(dest);p.derived(dest,[north],{'method':'exact native north context','sourceBoxLTRB':[0,3981,4096,4096]})
 update('layout_structure_pending')
def update(stage=None):
 names=sorted(x.stem for x in(ROOT/'native').glob('p??.png'))
 complete=(ROOT/'tiles/r10_c12-candidate.png').exists()
 p.write(ROOT/'progress.json',{'updatedAt':p.stamp(),'appearance':'penglai_day','tile':'r10_c12','nativeDetailPatches':len(names),'expectedPatches':16,'completePixelCandidateTiles':int(complete),'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False,'stage':stage or 'native_details'})
 p.write(ROOT/'current-work.json',{'updatedAt':p.stamp(),'tile':'r10_c12','stage':stage or 'native_details','completedPatches':names,'next':next((f'p{r}{c}'for r in range(1,5)for c in range(1,5)if f'p{r}{c}'not in names),'assemble_and_qa')})
 if names:
  im=Image.new('RGB',(4096,4096),(210,214,210));d=ImageDraw.Draw(im)
  for r in range(1,5):
   for c in range(1,5):
    n=f'p{r}{c}';fp=ROOT/'native'/(n+'.png')
    if fp.exists():im.paste(Image.open(fp).convert('RGB').crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
    else:d.text(((c-1)*1024+50,(r-1)*1024+50),n+' PENDING',fill=(80,80,80))
  dest=ROOT/'current-preview.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(dest)
  p.derived(dest,[ROOT/'native'/(n+'.png')for n in names],{'method':'core hardcut review montage downscale','containsPlaceholderForMissingPatches':len(names)<16,'notProductionArt':True})
def ingest(source,name,role):
 call=p.read(ROOT/'prompts'/(name+'.call.json'));dest=p.ingest(source,name,str(ROOT/'prompts'/(name+'.prompt.txt')),call['referenced_image_paths'],role)
 rec=p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['submittedParameters']['promptFile']=str(ROOT/'prompts'/(name+'.prompt.txt'))
 rec['visualInspection']={'at':p.stamp(),'scope':'full displayed native tool output inspected against guide and style; assembled seam acceptance pending'}
 rec['evidence']['toolOutputHintFile']=str(ROOT/'evidence'/(name+'.tool-result.json'))
 p.write(str(dest)+'.generation.json',rec);update('native_details' if role!='layout_only' else 'structure_generated');print(dest,Image.open(dest).size)
def guides():
 src=ROOT/'references/structure-corrected.png';im=Image.open(src).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS)
 north=Path(H['baselineCandidates'][-1]['file']);im.paste(Image.open(north).convert('RGB').crop((0,3981,4096,4096)),(115,0))
 dest=ROOT/'references/layout-canvas-only.png';im.save(dest);p.derived(dest,[src,north],{'method':'resample structure guide for reference only; paste exact115px north overlap at[115,0]','neverFinalPixels':True})
 records=[]
 for r in range(1,5):
  for c in range(1,5):
   n=f'p{r}{c}';box=((c-1)*1024,(r-1)*1024,(c-1)*1024+1254,(r-1)*1024+1254)
   dest=ROOT/'guides'/(n+'.png');im.crop(box).save(dest);p.derived(dest,[ROOT/'references/layout-canvas-only.png'],{'method':'integer geometry-guide crop,not final pixels','boxLTRB':box})
   records.append({'id':n,'file':str(dest),'globalCoreXYWH':[45056+(c-1)*1024,36864+(r-1)*1024,1024,1024]})
 p.write(ROOT/'guides/index.json',{'patches':records,'finalUseForbidden':True});update()
def prepare(name,scene):
 r=int(name[1]);c=int(name[2]);refs=[(ROOT/'guides'/(name+'.png')).as_posix(),STYLE];extra=[]
 if c>1:
  n=f'p{r}{c-1}';refs.append((ROOT/'native'/(n+'.png')).as_posix());extra.append(f'Image{len(refs)} is completed LEFT NEIGHBOR {n}; target left230px overlaps its right230px.')
 if r>1:
  n=f'p{r-1}{c}';refs.append((ROOT/'native'/(n+'.png')).as_posix());extra.append(f'Image{len(refs)} is completed UPPER NEIGHBOR {n}; target top230px overlaps its bottom230px.')
 prompt=f'Use case: sketch-to-render. Native detailed art patch {name} for r10_c12 of continuous isometric Taoist Q fantasy town map 五行奇谈. Image1 is EXACT crop/geometry guide, reference pixels only. Image2 is approved PRIMARY PAINTING STYLE, never copy UI. '+ ' '.join(extra)+' REDRAW ONLY Image1 with crisp native clean hand-painted detail. Scene: '+scene+' Preserve EXACT camera, crop, object counts, scale, silhouettes, boundaries and edge tangent endpoints; adjacent inputs only constrain overlap/material, never replace target crop. Keep road, roof, water/harbor and stair geometry unchanged. '+('Top115px includes exact original north-tile context: naturally continue its roof and boundary endpoints, removing artificial splice at y115 without changing other geometry. 'if r==1 else '')+'Clean bright rounded full Taoist Q fantasy rendering matching approved style: clear rounded bevels, delicate restrained native material shading, warm day light and cool soft shadows. Do not subdivide tiles or increase object/leaf density, no added objects. Keep all cropped objects cropped. No text,UI,labels,border,watermark,grain,dense cracks,plastic glare,photorealism,blur or sharpen halos. Square exact crop.'
 (ROOT/'prompts'/(name+'.prompt.txt')).write_text(prompt,encoding='utf8')
 call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};p.write(ROOT/'prompts'/(name+'.call.json'),call);print(json.dumps(call))
def assemble():
 assert len(list((ROOT/'native').glob('p??.png')))==16
 im=Image.new('RGB',(4096,4096))
 sources=[]
 for r in range(1,5):
  for c in range(1,5):
   fp=ROOT/'native'/f'p{r}{c}.png';src=Image.open(fp).convert('RGB');assert src.size==(1254,1254);sources.append(fp)
   im.paste(src.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
 dest=ROOT/'tiles/r10_c12-candidate.png';im.save(dest);p.derived(dest,sources,{'method':'16native1024cores integer hardcut,no scaling,no feathering','sourceCoreBoxLTRB':[115,115,1139,1139],'candidateOnly':True,'formalAccepted':False})
 update('complete_pixel_candidate_pending_qa')
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='init':init()
 elif mode=='guides':guides()
 elif mode=='ingest':ingest(sys.argv[2],sys.argv[3],sys.argv[4])
 elif mode=='prepare':prepare(sys.argv[2],sys.argv[3])
 elif mode=='assemble':assemble()


