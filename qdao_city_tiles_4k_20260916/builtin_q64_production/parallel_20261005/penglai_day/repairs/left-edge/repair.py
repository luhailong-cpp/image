from pathlib import Path
from PIL import Image
import json, hashlib, datetime, shutil, sys
R=Path(__file__).resolve().parent
TASK=R.parent.parent
REPO=Path('D:/work/image')
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x): Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf-8')
def derived(p,src,op):
    write(str(p)+'.generation.json',{'file':str(p),'sha256':sha(p),'createdAt':now(),'pixels':Image.open(p).size,'derivedFrom':[{'file':str(s),'sha256':sha(s),'generationRecord':str(s)+'.generation.json'} for s in src],'operation':op,'productionArt':False})
H=read(TASK/'handoff.json')
BASE=Path(H['baselineCandidates'][-1]['file'])
P11=TASK/'native/p11.png'
STYLE=REPO/'designs/gameplay-ui/04-guild.png'
def prepare():
    assert sha(BASE)==H['baselineCandidates'][-1]['sha256']
    old=Image.open(BASE).convert('RGB'); new=Image.open(P11).convert('RGB')
    canvas=Image.new('RGB',(1254,1254))
    # Exact native pixels. Only y<115 is clamped context, never exported.
    canvas.paste(old.crop((3469,0,4096,1139)),(0,115))
    for y in range(115): canvas.paste(old.crop((3469,0,4096,1)),(0,y))
    canvas.paste(new.crop((115,0,742,1254)),(627,0))
    p=R/'target-native.png'; canvas.save(p)
    derived(p,[BASE,P11],{'method':'native integer crop/composite','globalOriginXY':[48525,32653],'jointX':627,'oldSourceCropLTRB':[3469,0,4096,1139],'oldDestinationXY':[0,115],'newSourceCropLTRB':[115,0,742,1254],'newDestinationXY':[627,0],'clampHalo':[0,0,627,115],'haloForReferenceOnly':True,'resampling':None})
    write(R/'placement.json',{'updatedAt':now(),'globalOriginXY':[48525,32653],'nativePixels':[1254,1254],'sharedTileEdgeGlobalX':49152,'sharedEdgeImageX':627,'tileRowGlobalY':32768,'reviewScopeY':[32768,33792],'rightSideOnly':True,'immutableBaselineFile':str(BASE),'immutableBaselineSha256':sha(BASE),'p11File':str(P11),'p11Sha256':sha(P11),'generatedOutputPolicy':'candidate; no automatic integration','exportY':[115,1139],'maximumCandidateGlobalRectXYWH':[49152,32768,627,1024],'maskPolicy':'No baseline pixels may be replaced. Exact replacement shape chosen only after visual checks. No feathering to hide structure.'})
def ingest(source,name,target='target-native.png',extra=None):
    source=Path(source);dest=R/(name+'.png');shutil.copy2(source,dest)
    prompt=R/(name+'.prompt.txt');refs=[R/target,STYLE]
    if extra: refs.append(R/extra)
    rec={'file':str(dest),'sha256':sha(dest),'generatedAt':now(),'width':Image.open(dest).width,'height':Image.open(dest).height,'format':'PNG','tool':'image_gen.imagegen','route':'builtin','toolResultPath':str(source),'configSnapshot':read(REPO/'config/image-generation.json'),'submittedParameters':{'model':None,'quality':None,'prompt':prompt.read_text(encoding='utf-8'),'referenced_image_paths':[str(x) for x in refs],'transparent_background':False},'actualModel':None,'actualQuality':None,'unverifiedReason':'宿主管理，工具未披露型号/质量，无可核实元数据；提示词不代表选择器。','prompt':str(prompt),'references':[{'file':str(x),'sha256':sha(x),'role':'native edit target; immutable left side geometry/color anchor' if i==0 else 'approved primary style only'} for i,x in enumerate(refs)],'role':'native_geometry_repair_candidate','formalAccepted':False,'evidence':{'toolResultPath':str(source),'displayedInToolResult':True,'modelVerificationInherited':str(TASK/'evidence/model-verification.json')}}
    write(str(dest)+'.generation.json',rec)
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    if sys.argv[1]=='ingest':ingest(sys.argv[2],sys.argv[3],sys.argv[4] if len(sys.argv)>4 else 'target-native.png',sys.argv[5] if len(sys.argv)>5 else None)
