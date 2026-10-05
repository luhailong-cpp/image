"""Task-local provenance and native-pixel preparation. No API calls."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
REPO = Path('D:/work/image')
def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def write(p, data):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def deriv(p, sources, operation):
    im=Image.open(p)
    write(str(p)+'.generation.json',dict(file=str(p),sha256=sha(p),createdAt=now(),width=im.width,height=im.height,format=im.format,derivedFrom=[dict(file=str(s),sha256=sha(s)) for s in sources],operation=operation,productionPixels=False))

def prepare():
    h=read(ROOT/'handoff.json')
    checked=[]
    for source in [h['plan'],h['layout']]+h['baselineCandidates']:
        p=Path(source['file']); actual=sha(p)
        checked.append(dict(file=str(p),expectedSha256=source['sha256'],sha256=actual,matches=source['sha256']==actual))
        assert checked[-1]['matches'], str(p)
    write(ROOT/'evidence/input-verification.json',dict(checkedAt=now(),sources=checked))
    write(ROOT/'evidence/model-verification.json',dict(verifiedAt=now(),configSnapshot=read(REPO/'config/image-generation.json'),officialSources=['https://developers.openai.com/api/docs/models/gpt-image-2.5-sunburst','https://developers.openai.com/api/reference/resources/images/methods/generate'],finding='Official page lists Sunburst as most capable image model; max is highest named quality. Builtin schema exposes neither selector nor returned model/quality.',submittedModel=None,submittedQuality=None,actualModel=None,actualQuality=None))
    ref=ROOT/'references'; ref.mkdir(exist_ok=True)
    c12=Path(h['baselineCandidates'][2]['file']); im=Image.open(c12)
    p=ref/'c12-right-115.png'; im.crop((3981,0,4096,4096)).save(p)
    deriv(p,[c12],dict(kind='crop',boxLTRB=[3981,0,4096,4096],scale=1,globalRectXYWH=[49037,32768,115,4096]))
    p=ref/'c12-context-preview.png'; im.resize((1254,1254),Image.Resampling.LANCZOS).save(p)
    deriv(p,[c12],dict(kind='downsample_reference_only',outputPixels=[1254,1254]))
    # Native left neighbour crop alongside the second micro-row. No source enlargement.
    p=ref/'c12-p02-edge-context.png'; im.crop((2842,909,4096,2163)).save(p)
    deriv(p,[c12],dict(kind='crop',boxLTRB=[2842,909,4096,2163],scale=1))
    preview=Image.new('RGB',(1536,512),'#202a32')
    for n,b in enumerate(h['baselineCandidates']):
        src=Image.open(b['file']); preview.paste(src.resize((512,512),Image.Resampling.LANCZOS),(512*n,0))
    p=ROOT/'current-preview.png'; preview.save(p)
    deriv(p,[Path(b['file']) for b in h['baselineCandidates']],dict(kind='candidate_overview_downsample_only',tileIds=[b['tile'] for b in h['baselineCandidates']],scale=0.125))
    write(ROOT/'r09_c13-plan.json',dict(tile='r09_c13',globalPixelRectXYWH=[49152,32768,4096,4096],core=1024,halo=115,overlap=230,nativePatchPixels=[1254,1254],nativeGrid=[4,4],wholeCityPixels=[65536,65536],availableLeftContextGlobalRectXYWH=[49037,32768,115,4096],missingHistoricalOutsideContext=True,sharedGeometry='Reuse newly reviewed penglai_day r09_c13 structure when available; independent festival layout is appearance only.',navigationVerified=False,formalAccepted=False))
    write(ROOT/'current-work.json',dict(updatedAt=now(),appearance=h['appearance'],tile='r09_c13',stage='preparing_shared_structure',next='Read current day shared structure; builtin Mid-Autumn geometry-preserving edit; generate native 1024-core detail patches.',outputDirectory=str(ROOT)))
    write(ROOT/'progress.json',dict(updatedAt=now(),appearance=h['appearance'],targetTiles=256,existingFullPixelCandidates=3,newFullPixelCandidates=0,totalFullPixelCandidates=3,nativeFragments=0,newAIGenerations=0,formalAccepted=0,wholeCityComplete=False,runtimePublished=False,clientVerified=False,currentTile='r09_c13',currentPreview=str(p),baselineQA=h['latestQA'],baselineQAReusedByHash=True))
    print(json.dumps(dict(hashesVerified=len(checked),baselineCandidates=3,nextTile='r09_c13',output=str(ROOT))))

if __name__=='__main__': prepare()
