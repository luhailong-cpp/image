from pathlib import Path
import sys
F=Path(__file__).resolve().parent;sys.path.insert(0,str(F.parent))
from production import read,write,sha,now
from PIL import Image
items=[]
for c in range(1,5):
 p=F/f'native/p1{c}.png';g=read(str(p)+'.generation.json');req=read(F/f'native/p1{c}.request.json')
 assert sha(p)==g['sha256'] and Image.open(p).size==(1254,1254)
 assert sha(req['prompt'])==req['promptSha256'] and req['submittedParameters']['prompt']==Path(req['prompt']).read_text(encoding='utf-8')
 for a in req['references']:assert sha(a['file'])==a['sha256']
 items.append(dict(file=str(p),sha256=sha(p),generation=str(p)+'.generation.json',actuallyViewed=True,reviewer='root',nativePixels=[1254,1254],sourceUpscaled=False,modelAndQualityActual=None,verdict='native_detail_retained_pending_assembled_seam_QA',observations=['Cropped framing, established posts, cloth, wood, stone and water retained.','Fresh native painted edges and organized brushwork; no new sky, scene, writing or extra objects.','Final true-N and internal seam acceptance remains pending exact assembly and current-pixel inspection.']))
write(F/'qa/native-row1-root-review.json',dict(reviewedAt=now(),reviewer='root',items=items,count=4,allReferencesVerified=True,planningStructureAuthorized=read(F/'qa/root-structure-authorization.json')['planningGeometryAccepted'],formalAccepted=False,assembledQAClaimed=False))
print('4 native products provenance verified and actual raw inspections recorded.')
