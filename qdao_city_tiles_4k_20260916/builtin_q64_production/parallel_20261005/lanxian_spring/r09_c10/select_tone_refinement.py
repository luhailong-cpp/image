from pathlib import Path
from datetime import datetime,timezone
from PIL import Image
import json,hashlib,shutil
T=Path(__file__).resolve().parent;S=T/'tone-refinement';O=T/'selected-v2';O.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def wr(p,d):Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def info(p):
 p=Path(p);return {'file':str(p),'sha256':sha(p),'pixels':list(Image.open(p).size)}
expected={'core4096.png':'389f08d8b0d9ded71be272a52d7975c2c2d10820118d471596d809886903bf75','extended4326.png':'3532108ee8d5eab3f85bee5abb83924e5df41c2a1126b08554a6c754d0bd917d'}
for n,h in expected.items():assert sha(S/n)==h
for n in ['core4096.png','extended4326.png','preview1254.png']:
 shutil.copyfile(S/n,O/n)
 shutil.copyfile(S/(n+'.generation.json'),O/(n+'.generation.json'))
 side=json.loads((O/(n+'.generation.json')).read_text(encoding='utf-8-sig'));side.update({'currentFile':str(O/n),'currentSha256':sha(O/n),'selectedFrom':str(S/n)});wr(O/(n+'.generation.json'),side)
m=json.loads((T/'selected/delivery.manifest.json').read_text(encoding='utf-8-sig'))
m.update({'updatedAtUtc':datetime.now(timezone.utc).isoformat(),'status':'qualified_complete_4k_candidate_tone_refined_pending_remaining_adjacent_edges_and_formal_acceptance','qualifiedComplete4KCandidate':True,'formalAccepted':False,'clientValidated':False,'wholeCityComplete':False,'previousSeasonalSelection':str(T/'selected/delivery.manifest.json'),'previousSeasonalSelectionSha256':sha(T/'selected/delivery.manifest.json'),'toneRefinement':{'processing':str(S/'processing.json'),'sha256':sha(S/'processing.json'),'noNewAIGeneration':True,'noResamplingWarpOrBlur':True,'maxActualRgbChange':[14,13,14],'northHaloAndFirst64CoreRowsUnchanged':True,'reviewScope':'Six internal seams, twelve field return edges and north interface viewed at1:1; root also viewed fullpreview.'},'outputs':{'core':info(O/'core4096.png'),'extended':info(O/'extended4326.png'),'preview':info(O/'preview1254.png')},'knownMinorRemainder':'Original1-3px redpost contour/tone irregularity aroundcore[900,964,1120,1084] retained; seasonal red surfaces excluded from tonefield.'})
wr(O/'delivery.manifest.json',m)
print(json.dumps(m['outputs'],ensure_ascii=False))
