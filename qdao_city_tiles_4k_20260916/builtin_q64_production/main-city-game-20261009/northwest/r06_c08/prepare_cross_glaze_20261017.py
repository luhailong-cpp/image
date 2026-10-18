from pathlib import Path
from datetime import datetime,timezone
import sys
from PIL import Image
T=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08');Z=T.parent;sys.path.insert(0,str(Z));import production_v2 as p
B=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/main-city-game-20261009/northwest/r06_c08/repair-batches/blue-glaze-cross-20261017-fix03');B.mkdir(parents=True,exist_ok=False)
C=T/'candidate/native16-restart-20261017-v1/candidate.png';W=Z/'r06_c07/candidate/r06_c07-candidate-hard-4c0d654c3aae.png'
assert p.sha(C)=='122fd69829f7a019ba1d649356d57990ea84f71873f55eb881cdc52020d9c25c'
assert p.sha(W)=='e3184ae204d0cd8f0ea701bf6b3281449bb1489c18514f525869f37d72326609'
im=Image.new('RGB',(1254,1254));im.paste(Image.open(W).convert('RGB').crop((3936,1421,4096,2675)),(0,0));im.paste(Image.open(C).convert('RGB').crop((0,1421,1094,2675)),(160,0));p.save_png(B/'edit-target.png',im)
p.write_json(B/'edit-target.derivation.json',dict(guideOnly=True,worldBox=[28512,21901,29766,23155],tileOrigin=[-160,1421],size=[1254,1254],nativePixelScale=1,resampled=False,parts=[dict(file=str(W),sha256=p.sha(W),sourceLTRB=[3936,1421,4096,2675],destination=[0,0]),dict(file=str(C),sha256=p.sha(C),sourceLTRB=[0,1421,1094,2675],destination=[160,0])],productionSource=False),replace=False)
p.write_json(B/'reopen-basis.json',dict(parentDirectedConcentratedRepair=True,priorRepairSources=['s03_01_fix01','s03_01_fix02'],priorFailure='Output modified outer anchors when editing a single patch; exact neighbor west core remained darker. Now full candidate plus true west context are composed in same world; select only local own-tile pixels.',targetCrops=['internal_y2048_seg1','west_seg3','west_joint2048'],rootRuleSha256=p.sha(p.REPO/'AGENTS.md'),splitSha256=p.sha(p.REPO/'docs/MAP_PARALLEL_SPLIT_20261013.json'),rulesActuallyRead=True),replace=False)
print(str(B/'edit-target.png'))

