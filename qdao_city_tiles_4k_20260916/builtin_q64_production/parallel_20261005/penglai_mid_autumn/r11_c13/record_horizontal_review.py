"""Record this agent's completed original-scale inspection; only writes horizontal-review.json."""
import hashlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
from PIL import Image

F=Path(__file__).resolve().parent
Q=F/'qa'/'native-candidate'
C=F/'output'/'r11_c13-candidate.png'
EXPECTED='1aa087f96cf986582881560436fb3fba780cbcbe13f3b29a133e4eb9c0ece180'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def ref(p):return dict(file=str(Path(p).resolve()),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
assert sha(C)==EXPECTED
final=Image.open(C).convert('RGB');assert final.size==(4096,4096)
observations={
'internal-y1024-full.png':'Viewed all four original-pixel sections. Wooden uprights and crossbar, stone grout and highlights, and right-side water remain continuous across the row boundary; no abrupt horizontal color band or displaced contour was seen.',
'internal-y1024-return-256-full.png':'Viewed all four original-pixel return sections at y1280. Rounded paving intersections, warm light across the pavement, wooden post edges and blue water brushwork retain continuity without a hard return line.',
'internal-y2048-full.png':'Viewed all four original-pixel sections. Tied parcel, crate planks and corner post, paving and quay cap edges join cleanly across the boundary; no added seam or broken object edge was seen.',
'internal-y2048-return-256-full.png':'Viewed all four original-pixel return sections at y2304. Parcel rope, crate face and diagonal brace, stone cap and wall grout continue without a step or straight tone transition.',
'internal-y3072-full.png':'Viewed all four original-pixel sections. Crate foot and its shadow, capstone joints, broad wall courses and cropped boat rim preserve shape and shading across the boundary.',
'internal-y3072-return-256-full.png':'Viewed all four original-pixel return sections at y3328. Capstone and vertical grout, wall brushwork, fender, boat side and reflective water show no visible registration-return band.',
'junction-1024-1024.png':'Viewed the 320-square original crop. Wooden upright and diagonal crossbar plus paved grout/highlights remain continuous at the four-patch junction.',
'junction-2048-1024.png':'Viewed the 320-square original crop. Diagonal paving junction and cast shadow retain coherent widths and endpoints; no cross-shaped artifact was seen.',
'junction-3072-1024.png':'Viewed the 320-square original crop. Broad stone brushwork and diagonal grout/highlight retain continuity without a four-quadrant tone split.',
'junction-1024-2048.png':'Viewed the 320-square original crop. Tied parcel, crate corner post and horizontal board edges remain coherent across the junction.',
'junction-2048-2048.png':'Viewed the 320-square original crop. Crate post and plank joints keep crisp connected edges and continuous warm shading.',
'junction-3072-2048.png':'Viewed the 320-square original crop. Stone cap upright, dark grout and warm cast-shadow edge remain continuous without displaced endpoints.',
'junction-1024-3072.png':'Viewed the 320-square original crop. Crate base, bright paving surface and diagonal grout line retain continuous contours and brushwork.',
'junction-2048-3072.png':'Viewed the 320-square original crop. Wall-block grout intersection and lower diagonal highlight keep consistent thickness and connected geometry.',
'junction-3072-3072.png':'Viewed the 320-square original crop. Diagonal wall mortar and highlight remain continuous through the junction, with no straight color boundary.'
}
items=[]
for name,note in observations.items():
    p=Q/name;g=Path(str(p)+'.generation.json');m=read(g);op=m['operation']
    assert m['sha256']==sha(p) and m['nativeScale']==1
    assert m['sources']==[ref(C)]
    if name.startswith('internal-y'):
        assert op['axis']=='y' and op['rotationCCW90'] is False
        pos=op['position'];boxes=[[i*1024,pos-160,(i+1)*1024,pos+160] for i in range(4)]
        assert op['sourceCropLTRB']==boxes
        reproduced=Image.new('RGB',(1024,1280))
        for i,box in enumerate(boxes):reproduced.paste(final.crop(box),(0,i*320))
    else:
        x,y=map(int,name.removesuffix('.png').split('-')[1:]);box=[x-160,y-160,x+160,y+160]
        assert op['cropLTRB']==box
        reproduced=final.crop(box)
    saved=Image.open(p).convert('RGB')
    assert saved.size==reproduced.size and saved.tobytes()==reproduced.tobytes()
    buffer=io.BytesIO();reproduced.save(buffer,format='PNG')
    assert buffer.getvalue()==p.read_bytes()
    items.append(dict(**ref(p),pixelSha256=digest(saved.tobytes()),pixels=list(saved.size),actuallyViewed=True,nativeScale=1,verdict='scoped_pass',viewTool='view_image; detail=original',observations=note,appliedToCandidateSha256=EXPECTED,sources=[ref(C)],generationRecord=ref(g),pixelReproduction=dict(operation=op,source=ref(C),decodedRGBPixelsIdentical=True,pngBytesIdentical=True,reproducedPNGByteSha256=digest(buffer.getvalue()),reproducedPixelSha256=digest(reproduced.tobytes()),noResize=True,newImagesSaved=False)))
assert len(items)==15 and sha(C)==EXPECTED
report=dict(reviewedAt=datetime.now(timezone.utc).isoformat(),reviewer='/root/r09c14_row4_resume',rootReview=False,candidate=ref(C),scope='Six original-scale horizontal seam/return sheets and nine four-patch junction crops only',scopedPass=True,items=items,allAssignedQAActuallyViewed=True,allAssignedQAPixelReproduced=True,issueCount=0,issues=[],formalAccepted=False,navigationVerified=False,clientVerified=False,externalSeamsAcceptedByThisReport=False,candidateModified=False,assemblyModified=False)
out=F/'qa'/'horizontal-review.json';assert not out.exists()
out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(dict(report=ref(out),count=len(items),scopedPass=True,pixelAndByteReproductionPassed=True,candidateUnchanged=True),indent=2))
