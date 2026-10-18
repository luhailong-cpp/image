from pathlib import Path
from PIL import Image
import json,hashlib
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04');D=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r08_c04/repair-batches/row2-x1024-consolidated-20261016');D.mkdir(exist_ok=True)
assert not (D/'edit-target.png').exists()
base=T/'candidate/native-24-source-incremental-20261016T092532143914Z-5c44435606119f4b/candidate.png'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(base)=='00b6fd40e61bceffdf6fd10b9c140c532831c46f63be92a54c5e0f729eb65c68'
im=Image.open(base).convert('RGB').crop((397,909,1651,2163));assert im.size==(1254,1254)
im.save(D/'edit-target.png')
im.crop((450,280,830,570)).save(D/'upper-before.png')
im.crop((450,660,830,980)).save(D/'lower-before.png')
(D/'input-provenance.json').write_text(json.dumps({'tile':'r08_c04','source':str(base),'sourceSha256':sha(base),'candidateCropLTRB':[397,909,1651,2163],'originInTile':[397,909],'worldBox':[12685,29581,13939,30835],'targetSha256':sha(D/'edit-target.png'),'resampled':False,'priorFailedBatch':'row2-west-joints-20261013/joint-x1024-01 and joint-x1024-02; both preserved and not adopted','priorFailureReasons':['Narrow rectangles transferred shifted slopes/vertices to mask perimeter.','Second attempt produced stair-step geometry and failed to remove the hard seam.'],'currentRoundBasis':'Five independent repair points finished; now return for consolidated repair per AGENTS. Current 24-source context includes accepted curb repair. Trace full affected joint to stable endpoints, choose same-world native corridor after output, and verify all mask perimeters.','maxNewGenerationAttemptsWithoutImprovement':2},indent=2),encoding='utf-8')

