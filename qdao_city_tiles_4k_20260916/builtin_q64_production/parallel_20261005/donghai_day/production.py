"""Local native-pixel production bookkeeping; never invokes an API."""
import sys,json,hashlib,shutil
from pathlib import Path
from datetime import datetime,timezone
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent
PROJECT=Path('D:/work/image')
PY=Path('C:/Users/luyua/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
LAYOUT=PROJECT/'qdao_city_tiles_4k_20260916/builtin_q64_all_city_references/donghai_day/map-native-layout-reference.png'
WEST=PROJECT/'qdao_city_tiles_4k_20260916/builtin_q64_production/donghai_day/r08_c08_c09_c10_joint/output_v3/r08_c10.png'
STYLE=PROJECT/'designs/gameplay-ui/04-guild.png'
T=ROOT/'r08_c11'
ORIGIN=(40960,28672)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def savej(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def loadj(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def init():
 for d in ['guides','native','prompts','qa','output']: (T/d).mkdir(parents=True,exist_ok=True)
 h=loadj(ROOT/'handoff.json');items=[]
 for e in [h['plan'],h['layout']]+h['baselineCandidates']:
  p=Path(e['file']); actual=sha(p);items.append({'file':str(p),'expected':e['sha256'],'sha256':actual,'matches':actual==e['sha256']})
 assert all(x['matches'] for x in items)
 savej(ROOT/'source-verification.json',{'checkedAt':now(),'files':items})
 # Enlarged low-resolution reference is guidance ONLY, never included in output art.
 layout=Image.open(LAYOUT).convert('RGB');scale=layout.width/65536
 box=[v*scale for v in (40960-115,28672-115,45056+115,32768+115)]
 guide=layout.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC)
 guide.save(T/'guides/local-layout.png')
 savej(T/'guides/local-layout.png.generation.json',{'file':str(T/'guides/local-layout.png'),'sha256':sha(T/'guides/local-layout.png'),'operation':'reference-only enlarged global layout crop','sourceBox':box,'globalBox':[40845,28557,45171,32883],'derivedFrom':[{'file':str(LAYOUT),'sha256':sha(LAYOUT)}],'allowedInFinal':False})
 savej(ROOT/'batch-model-check.json',{'checkedAt':now(),'configSnapshot':loadj(PROJECT/'config/image-generation.json'),'officialSourcesChecked':['https://openai.com/index/introducing-chatgpt-images-2-5/','https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst'],'finding':'Official Images 2.5 release and Sunburst max quality confirmed; host tool exposes neither model nor quality selector. No root configuration modified.','actualModel':None,'actualQuality':None})
 status()
def status():
 natives=list((T/'native').glob('r??_c??.png')); candidates=list((T/'output').glob('r08_c11.png'))
 state={'appearance':'donghai_day','updatedAtUtc':now(),'targetCityPixels':[65536,65536],'targetTiles':256,'baselineCompletePixelCandidates':3,'newCompletePixelCandidates':len(candidates),'formalAccepted':0,'wholeCityComplete':False,'runtimeIntegration':False,'activeTile':'r08_c11','activeGlobalRect':[40960,28672,4096,4096],'nativeCorePixels':1024,'nativeHaloPixels':115,'nativePatchesSaved':len(natives),'nativePatchesRequiredForActiveTile':16,'fragmentsCountAsTiles':False,'phase':'native_expansion_in_progress','nextAction':'Generate next missing adjacent native patch; assemble only after all 16 native patches; inspect all internal seams, west common edge and corners.'}
 savej(ROOT/'progress.json',state);savej(ROOT/'current-work.json',state)
def record(name,src):
 src=Path(src);out=T/('native' if name.startswith('r0') else 'guides')/(name+'.png')
 assert not out.exists(),str(out)
 shutil.copyfile(src,out);im=Image.open(out);im.load()
 refs=loadj(T/'prompts'/(name+'.references.json'))
 savej(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'generatedAt':now(),'width':im.width,'height':im.height,'format':im.format,'tool':'image_gen.imagegen','route':'builtin','configSnapshot':loadj(PROJECT/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'transparent_background':False,'referenced_image_paths':[e['file'] for e in refs]},'actualModel':None,'actualQuality':None,'unverifiedReason':'Host-managed tool exposes no model/quality selectors or returned model/quality metadata.','evidence':{'toolResultSourcePath':str(src),'toolResultSha256':sha(src),'responseMetadata':'Local output path returned by built-in imagegen; no model/quality disclosed.'},'prompt':str(T/'prompts'/(name+'.txt')),'promptSha256':sha(T/'prompts'/(name+'.txt')),'references':refs,'resizedAfterGeneration':False,'finalArtUpscaled':False,'role':'native 1024 core + overlap' if name.startswith('r0') else 'local structural reference only; not final HD pixels'})
 status();print(json.dumps({'saved':str(out),'pixels':im.size,'sha256':sha(out)}))
def guide(r,c):
 name=f'r{r:02}_c{c:02}';ox=(c-1)*1024;oy=(r-1)*1024
 local=Image.open(T/'guides/local-structure.png').convert('RGB')
 scale=local.width/4326
 g=local.transform((1254,1254),Image.Transform.EXTENT,tuple(v*scale for v in (ox,oy,ox+1254,oy+1254)),Image.Resampling.BICUBIC)
 refs=[{'file':str(T/'guides/local-structure.png'),'sha256':sha(T/'guides/local-structure.png'),'role':'reference-only enlarged structural guide'}]
 # Overlay actual existing neighbor pixels. No synthesized or extrapolated margins.
 if c==1:
  west=Image.open(WEST).convert('RGB');y0=max(0,oy-115);y1=min(4096,oy+1139)
  g.paste(west.crop((3981,y0,4096,y1)),(0,y0-(oy-115)))
  refs.append({'file':str(WEST),'sha256':sha(WEST),'role':'actual west neighbor, only existing 115-pixel interior edge copied'})
 for rr,cc in [(r-1,c-1),(r-1,c),(r-1,c+1),(r+1,c-1),(r+1,c),(r+1,c+1),(r,c+1),(r,c-1)]:
  p=T/'native'/f'r{rr:02}_c{cc:02}.png'
  if not p.exists():continue
  px=(cc-1)*1024;py=(rr-1)*1024;x0=max(ox,px);y0=max(oy,py);x1=min(ox+1254,px+1254);y1=min(oy+1254,py+1254)
  if x1>x0 and y1>y0:
   g.paste(Image.open(p).crop((x0-px,y0-py,x1-px,y1-py)),(x0-ox,y0-oy))
   refs.append({'file':str(p),'sha256':sha(p),'role':'actual overlapping native neighbor pixels'})
 out=T/'guides'/(name+'.png');g.save(out)
 savej(str(out)+'.generation.json',{'file':str(out),'sha256':sha(out),'operation':'layout-reference crop plus exact native overlapping neighbors','derivedFrom':refs,'globalBox':[ORIGIN[0]-115+ox,ORIGIN[1]-115+oy,ORIGIN[0]+1139+ox,ORIGIN[1]+1139+oy],'allowedInFinal':False})
 print(str(out))
def prepare(r,c,subject):
 name=f'r{r:02}_c{c:02}';guide(r,c)
 refs=[{'file':str(T/'guides'/(name+'.png')),'role':'edit target, exact field of view; sharp edge strips are real adjacent native context, soft interior is layout reference only'},{'file':str(STYLE),'role':'primary user-confirmed rendering and materials style; no UI content'}]
 for e in refs:e['sha256']=sha(e['file'])
 prompt=f'''Use case: precise-object-edit. Edit IMAGE 1 only. This is native patch {name}, core 1024 with 115 pixel context on each side, inside fishing village daylight map {T.name} for 五行奇谈. Repaint the soft interior into genuinely crisp native hand-painted details. Subject: {subject}. IMAGE 2 is the PRIMARY user-confirmed art style: rounded full forms, delicate controlled volumes, clean outlines and warm bright daylight, quiet materials without micro-noise. Keep image 1 camera, composition, colors, every structural silhouette, leaf mass, stone joint, doorway and timber footprint fixed. Do not zoom, rotate, crop or add objects. Sharp strips at any edge (left, right, top or bottom) are actual already-generated adjacent context: preserve their geometry and color exactly, extend naturally across the sharp/soft junction. That junction is not a physical straight edge; draw continuous structures across it. Use existing leaf and tile shapes as guides, no new random foliage or smaller repeat pattern. Keep clean Q-style volume and material shading. Output one opaque square native image, 1254x1254 target, no enlargement of a low-res image. No text, UI, border, characters, collage, blur, grain, cracks, oversharpening or plastic reflection. Highest available visual finish. Return only image 1 repainted.'''
 (T/'prompts'/(name+'.txt')).write_text(prompt,encoding='utf-8');savej(T/'prompts'/(name+'.references.json'),refs)
 print(json.dumps({'name':name,'prompt':prompt,'references':[e['file'] for e in refs]}))
if __name__=='__main__':
 cmd=sys.argv[1]
 if cmd=='init':init()
 elif cmd=='record':record(sys.argv[2],sys.argv[3])
 elif cmd=='guide':guide(int(sys.argv[2]),int(sys.argv[3]))
 elif cmd=='prepare':prepare(int(sys.argv[2]),int(sys.argv[3]),sys.argv[4])
 elif cmd=='status':status()

