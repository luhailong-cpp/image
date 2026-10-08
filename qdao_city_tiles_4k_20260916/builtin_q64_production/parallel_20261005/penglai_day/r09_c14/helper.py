from pathlib import Path
from PIL import Image,ImageDraw
import sys,json,datetime,hashlib,shutil
BASE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(BASE))
import production as p
ROOT=Path(__file__).resolve().parent;p.ROOT=ROOT
STYLE='D:/work/image/designs/gameplay-ui/04-guild.png'
WEST=BASE/'tiles/current/r09_c13-candidate-v4b.png'
H=p.read(BASE/'handoff.json')
TILE='r09_c14';GX=53248;GY=32768
def init():
 for name in ['references','prompts','native','evidence','guides','qa','tiles']:(ROOT/name).mkdir(parents=True,exist_ok=True)
 assert p.sha(WEST)=='10bab639da831dda328f0a9b9e66dd9bc43c64e23cdffd08234bf1b492f33900'
 layout=Path(H['layout']['file']);assert p.sha(layout)==H['layout']['sha256']
 plan=p.read(H['plan']['file']);tile=next(x for x in plan['tiles'] if x['id']==TILE);assert tile['finalPixelRect']==[GX,GY,4096,4096]
 p.write(ROOT/'plan.json',{'tile':tile,'core':1024,'halo':115,'nativePatch':[1254,1254],'grid':[4,4],'westSource':str(WEST),'westSha256':p.sha(WEST),'formalAccepted':False})
 scale=1254/65536;box=tuple(v*scale for v in [GX-115,GY-115,GX+4096+115,GY+4096+115])
 im=Image.open(layout).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)
 dest=ROOT/'references/layout-only.png';im.save(dest);p.derived(dest,[layout],{'method':'layout-only crop resample; never final art','sourceBoxLTRB':box,'globalBoxLTRB':[GX-115,GY-115,GX+4211,GY+4211]})
 west=Image.open(WEST).convert('RGB');dest=ROOT/'references/west-right115-native.png';west.crop((3981,0,4096,4096)).save(dest);p.derived(dest,[WEST],{'method':'exact west anchor native crop','sourceBoxLTRB':[3981,0,4096,4096]})
 dest=ROOT/'references/west-preview.png';west.resize((1254,1254),Image.Resampling.LANCZOS).save(dest);p.derived(dest,[WEST],{'method':'downscale preview only'})
 im.paste(west.crop((3981,0,4096,4096)).resize((33,1188),Image.Resampling.LANCZOS),(0,33))
 dest=ROOT/'references/layout-with-west.png';im.save(dest);p.derived(dest,[layout,WEST],{'method':'layout reference with west actual115px anchored as downscaled 33x1188 strip at0,33; only reference','neverFinalArt':True})
 update('structure_pending')
def update(stage='native_details'):
 names=sorted(x.stem for x in (ROOT/'native').glob('p??.png'));complete=(ROOT/'tiles'/f'{TILE}-candidate.png').exists()
 p.write(ROOT/'progress.json',{'updatedAt':p.stamp(),'appearance':'penglai_day','tile':TILE,'nativeDetailPatches':len(names),'expectedPatches':16,'completePixelCandidateTiles':int(complete),'formalAccepted':0,'wholeCityComplete':False,'clientAccepted':False,'stage':stage})
 p.write(ROOT/'current-work.json',{'updatedAt':p.stamp(),'tile':TILE,'stage':stage,'completedPatches':names,'next':next((f'p{r}{c}' for r in range(1,5) for c in range(1,5) if f'p{r}{c}' not in names),'assemble_and_qa')})
 if names:
  im=Image.new('RGB',(4096,4096),(210,214,210));d=ImageDraw.Draw(im)
  for r in range(1,5):
   for c in range(1,5):
    n=f'p{r}{c}';fp=ROOT/'native'/(n+'.png')
    if fp.exists():im.paste(Image.open(fp).convert('RGB').crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
    else:d.text(((c-1)*1024+50,(r-1)*1024+50),n+' PENDING',fill=(80,80,80))
  dest=ROOT/'current-preview.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(dest);p.derived(dest,[ROOT/'native'/(n+'.png') for n in names],{'method':'core montage downscale review only','containsPlaceholderForMissingPatches':len(names)<16})
def ingest(source,name,role):
 call=p.read(ROOT/'prompts'/(name+'.call.json'));dest=p.ingest(source,name,str(ROOT/'prompts'/(name+'.prompt.txt')),call['referenced_image_paths'],role)
 rec=p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['submittedParameters']['promptFile']=str(ROOT/'prompts'/(name+'.prompt.txt'));rec['visualInspection']={'at':p.stamp(),'scope':'actual displayed output compared to guide/style, joint visual acceptance pending'};rec['evidence']['toolOutputHintFile']=str(ROOT/'evidence'/(name+'.tool-result.json'));p.write(str(dest)+'.generation.json',rec)
 update('structure_generated' if role=='layout_only' else 'native_details');print(dest,Image.open(dest).size)
def guides():
 src=ROOT/'references/structure.png';im=Image.open(src).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS);im.paste(Image.open(WEST).convert('RGB').crop((3981,0,4096,4096)),(0,115))
 dest=ROOT/'references/layout-canvas-only.png';im.save(dest);p.derived(dest,[src,WEST],{'method':'structure scaled for layout only, exact native west115px pasted at0,115','neverFinalArt':True})
 records=[]
 for r in range(1,5):
  for c in range(1,5):
   n=f'p{r}{c}';box=((c-1)*1024,(r-1)*1024,(c-1)*1024+1254,(r-1)*1024+1254);dest=ROOT/'guides'/(n+'.png');im.crop(box).save(dest);p.derived(dest,[ROOT/'references/layout-canvas-only.png'],{'method':'integer reference geometry crop','boxLTRB':box,'neverFinalArt':True});records.append({'id':n,'file':str(dest),'globalCoreXYWH':[GX+(c-1)*1024,GY+(r-1)*1024,1024,1024]})
 p.write(ROOT/'guides/index.json',{'patches':records,'finalUseForbidden':True});update()
def prepare(name,scene):
 r=int(name[1]);c=int(name[2]);refs=[(ROOT/'guides'/(name+'.png')).as_posix(),STYLE];extra=[]
 if c>1:
  n=f'p{r}{c-1}';refs.append((ROOT/'native'/(n+'.png')).as_posix());extra.append(f'Image{len(refs)} is LEFT NEIGHBOR {n}; target left230px overlaps its right230px.')
 if r>1:
  n=f'p{r-1}{c}';refs.append((ROOT/'native'/(n+'.png')).as_posix());extra.append(f'Image{len(refs)} is UPPER NEIGHBOR {n}; target top230px overlaps its bottom230px.')
 if c==1:
  y=max(0,(r-1)*1024-115);bottom=min(4096,(r-1)*1024+1139);dest=ROOT/'references'/f'west-{name}-native.png';Image.open(WEST).convert('RGB').crop((2957,y,4096,bottom)).save(dest);p.derived(dest,[WEST],{'method':'exact west context crop','sourceBoxLTRB':[2957,y,4096,bottom]});refs.append(dest.as_posix());extra.append(f'Image{len(refs)} is final WEST tile native context; its right115px equals target left115px, at target y{115 if r==1 else 0}. Continue material and tangent endpoints exactly. Guide artificial paste boundary at x115 is not an object; resolve it naturally.')
 prompt=f'Use case: sketch-to-render. Native detail patch {name} for {TILE} of continuous isometric Taoist Q fantasy map 五行奇谈. Image1 is EXACT crop/geometry guide, reference pixels only. Image2 is approved PRIMARY PAINTING STYLE, never copy UI. '+' '.join(extra)+' REDRAW ONLY Image1 with crisp native clean hand-painted detail. Scene: '+scene+' Preserve EXACT camera, crop, object counts, scale, silhouettes, edge endpoints, road and stair geometry. Adjacent images only constrain overlap and material, never replace target crop. Clean bright rounded full Taoist Q fantasy art matching primary style: soft warm daylight, restrained clean native brushwork, rounded bevels, cool soft shadows. No new objects, no extra paving seams, no increased foliage density, no text,UI,labels,borders,watermark,grain,dense cracks,plastic glare,blur or sharpen halos. Keep all cropped objects cropped. Square exact crop.'
 savecall(name,{'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False});print(json.dumps(p.read(ROOT/'prompts'/(name+'.call.json'))))
def savecall(name,call):
 (ROOT/'prompts'/(name+'.prompt.txt')).write_text(call['prompt'],encoding='utf8');p.write(ROOT/'prompts'/(name+'.call.json'),call)
def assemble():
 assert len(list((ROOT/'native').glob('p??.png')))==16;im=Image.new('RGB',(4096,4096));sources=[]
 for r in range(1,5):
  for c in range(1,5):
   fp=ROOT/'native'/f'p{r}{c}.png';src=Image.open(fp).convert('RGB');assert src.size==(1254,1254);sources.append(fp);im.paste(src.crop((115,115,1139,1139)),((c-1)*1024,(r-1)*1024))
 dest=ROOT/'tiles'/f'{TILE}-candidate.png';im.save(dest);p.derived(dest,sources,{'method':'16native1024core integer hardcut; zero scaling','sourceCoreBoxLTRB':[115,115,1139,1139],'candidateOnly':True});update('complete_pixel_candidate_pending_qa')
if __name__=='__main__':
 mode=sys.argv[1]
 if mode=='init':init()
 elif mode=='ingest':ingest(sys.argv[2],sys.argv[3],sys.argv[4])
 elif mode=='guides':guides()
 elif mode=='prepare':prepare(sys.argv[2],sys.argv[3])
 elif mode=='assemble':assemble()
