from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, datetime, shutil, sys

ROOT=Path(__file__).resolve().parent
REPO=Path('D:/work/image')
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,obj):
    p=Path(p); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
H=read(ROOT/'handoff.json')
def derived(p,sources,operation):
    write(str(p)+'.generation.json',{'file':str(p),'sha256':sha(p),'createdAt':stamp(),'pixels':Image.open(p).size,'derivedFrom':[{'file':str(x),'sha256':sha(x)} for x in sources],'operation':operation,'productionArt':False})
def init():
    for name in ['references','prompts','native','evidence','qa','tiles']:(ROOT/name).mkdir(exist_ok=True)
    inputs=[]
    for item in [H['plan'],H['layout']]+H['baselineCandidates']:
        p=Path(item['file']); actual=sha(p)
        assert actual==item['sha256'],p
        inputs.append({'file':str(p),'sha256':actual,'matchesHandoff':True})
    write(ROOT/'evidence/input-verification.json',{'verifiedAt':stamp(),'inputs':inputs})
    write(ROOT/'evidence/model-verification.json',{'checkedAt':stamp(),'configSnapshot':read(REPO/'config/image-generation.json'),'release':'https://openai.com/index/introducing-chatgpt-images-2-5/','model':'https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','officialObserved':'Images 2.5 available to ChatGPT/Work/Codex; Sunburst supports low, medium, high, xhigh, max, auto. Root config unchanged for parallel-task isolation.','submittedModel':None,'submittedQuality':None,'actualModel':None,'actualQuality':None})
    layout=Path(H['layout']['file']); im=Image.open(layout).convert('RGB')
    box=(938.2995300292969,624.7995300292969,1021.0754699707031,707.5754699707031)
    p=ROOT/'references/r09_c13-layout-only.png'
    im.transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(p)
    derived(p,[layout],{'method':'layout crop resampled for reference only','sourceBoxLTRB':box,'notFinalArt':True})
    baseline=Path(H['baselineCandidates'][-1]['file']); im=Image.open(baseline).convert('RGB')
    p=ROOT/'references/c12-context-preview.png';im.resize((1254,1254),Image.Resampling.LANCZOS).save(p);derived(p,[baseline],{'method':'downscale preview only'})
    p=ROOT/'references/c12-right-115.png';im.crop((3981,0,4096,4096)).save(p);derived(p,[baseline],{'method':'exact native crop','sourceBoxLTRB':[3981,0,4096,4096]})
    plan=read(REPO/'qdao_city_tiles_4k_20260916/q64_production_plans/penglai_day.json')
    t=next(x for x in plan['tiles'] if x['id']=='r09_c13')
    write(ROOT/'r09_c13-plan.json',{'tile':'r09_c13','globalPixelRectXYWH':t['finalPixelRect'],'worldRect':t['worldRect'],'core':1024,'halo':115,'nativePatchPixels':[1254,1254],'nativeGrid':[4,4],'layoutSource':str(layout),'baselineSource':str(baseline),'leftAvailableNativeContext':{'globalPixelRectXYWH':[49037,32768,115,4096],'file':str(ROOT/'references/c12-right-115.png')},'historicalExtendedContextExists':False,'sharedGeometry':'Day reference authoritative for new shared structure; festival and navigation require separate verification.','productionStatus':'structure_generation_pending','formalAccepted':False})
    write(ROOT/'progress.json',{'appearance':'penglai_day','updatedAt':stamp(),'targetTiles':256,'inheritedCompleteCandidateTiles':3,'newCompleteCandidateTiles':0,'formalAccepted':0,'newNativeDetailPatches':0,'wholeCityComplete':False,'clientAccepted':False,'currentTile':'r09_c13','status':'preparing_native_structure'})
    write(ROOT/'current-work.json',{'updatedAt':stamp(),'tile':'r09_c13','stage':'native_structure','next':'Generate geometry guide from verified layout and c12 adjacent context; then16 detail patches.','outputDirectory':str(ROOT)})

def ingest(source,name,prompt,refs,role):
    source=Path(source); dest=ROOT/('references' if role=='layout_only' else 'native')/(name+'.png')
    shutil.copy2(source,dest)
    rec={'file':str(dest),'sha256':sha(dest),'generatedAt':stamp(),'width':Image.open(dest).width,'height':Image.open(dest).height,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','toolResultPath':str(source),'configSnapshot':read(REPO/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'prompt':str(prompt),'referenced_image_paths':refs,'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露型号/质量，提示词不代表选择器。','prompt':str(prompt),'references':[{'file':x,'sha256':sha(x),'role':'edit target geometry' if i==0 else ('approved primary style' if '04-guild' in x else 'adjacent context')} for i,x in enumerate(refs)],'role':role,'formalAccepted':False,'evidence':{'toolResultPath':str(source),'displayedInToolResult':True}}
    rec['submittedParameters']['prompt']=Path(prompt).read_text(encoding='utf-8-sig')
    write(str(dest)+'.generation.json',rec)
    return dest

def guides():
    structure=ROOT/'references/r09_c13-structure.png'; im=Image.open(structure).convert('RGB').resize((4326,4326),Image.Resampling.LANCZOS)
    baseline=Path(H['baselineCandidates'][-1]['file']); neighbor=Image.open(baseline).convert('RGB')
    im.paste(neighbor.crop((3981,0,4096,4096)),(0,115))
    p=ROOT/'references/r09_c13-layout-canvas-only.png';im.save(p);derived(p,[structure,baseline],{'method':'resample generated structure for layout only and insert actual c12 last115px at [0,115,115,4211]','notFinalArt':True})
    (ROOT/'guides').mkdir(exist_ok=True)
    records=[]
    for row in range(4):
        for col in range(4):
            name=f'p{row+1}{col+1}'; box=(col*1024,row*1024,col*1024+1254,row*1024+1254)
            p=ROOT/'guides'/(name+'.png');im.crop(box).save(p);derived(p,[ROOT/'references/r09_c13-layout-canvas-only.png'],{'method':'integer guide crop only','boxLTRB':box})
            records.append({'id':name,'file':str(p),'sha256':sha(p),'canvasBoxLTRB':box,'globalCoreXYWH':[49152+col*1024,32768+row*1024,1024,1024]})
    write(ROOT/'guides/index.json',{'patches':records,'all24GuideOverlapsPixelIdentical':True,'finalPixelUseForbidden':True})
    cur=read(ROOT/'current-work.json');cur.update({'updatedAt':stamp(),'stage':'native_details','next':'Generate16 detail patches; all guide pixels reference-only'});write(ROOT/'current-work.json',cur)
    prog=read(ROOT/'progress.json');prog.update({'updatedAt':stamp(),'newStructureGuides':1,'status':'generating_native_details'});write(ROOT/'progress.json',prog)

if __name__=='__main__':
    if sys.argv[1]=='init': init()
    elif sys.argv[1]=='guides': guides()
    elif sys.argv[1]=='ingest': ingest(sys.argv[2],sys.argv[3],sys.argv[4],json.loads(sys.argv[5]),sys.argv[6])
