"""Additional scale-1 external seam crops; no acceptance or image edits."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import read,write,sha,now,deriv
from PIL import Image
F=Path(__file__).resolve().parent

def main():
    plan=read(F/'plan.json');candidate=F/'output/r10_c14-candidate.png'
    manifest=read(F/'output/native-assembly.json');assert sha(candidate)==manifest['sha256']
    im=Image.open(candidate).convert('RGB');out=F/'qa/external-details';out.mkdir(exist_ok=True)
    records=[]
    def save(p, image, sources, op):
        assert not p.exists();image.save(p);deriv(p,sources,op)
        records.append(dict(file=str(p),sha256=sha(p),pixels=list(image.size),operation=op,actuallyViewed=False,nativeScale=1))
    west=Path(plan['westCandidate']);north=Path(plan['northCandidate']);nw=Path(plan['northWestCandidate'])
    assert sha(west)==plan['westCandidateSha256'];assert sha(north)==plan['northCandidateSha256'];assert sha(nw)==plan['northWestCandidateSha256']
    for i in range(4):
        y=i*1024;view=Image.new('RGB',(640,1024));view.paste(Image.open(west).crop((3776,y,4096,y+1024)),(0,0));view.paste(im.crop((0,y,320,y+1024)),(320,0))
        save(out/f'west-unrotated-{i+1}.png',view,[west,candidate],dict(kind='native external western seam crop',seamX=320,neighborCropLTRB=[3776,y,4096,y+1024],candidateCropLTRB=[0,y,320,y+1024],resampling=False))
    # Include beam's full entry, raised-post attachment and foot, without any scaling.
    view=Image.new('RGB',(1254,1200));view.paste(Image.open(west).crop((3776,2896,4096,4096)),(0,0));view.paste(im.crop((0,2896,934,4096)),(320,0))
    save(out/'west-beam-attachment-native.png',view,[west,candidate],dict(kind='critical full wooden rail entry and same-post attachment/foot',seamX=320,neighborCropLTRB=[3776,2896,4096,4096],candidateCropLTRB=[0,2896,934,4096],resampling=False))
    view=Image.new('RGB',(640,640));view.paste(Image.open(nw).crop((3776,3776,4096,4096)),(0,0));view.paste(Image.open(north).crop((0,3776,320,4096)),(320,0));view.paste(Image.open(west).crop((3776,0,4096,320)),(0,320));view.paste(im.crop((0,0,320,320)),(320,320))
    save(out/'northwest-four-tile-corner.png',view,[nw,north,west,candidate],dict(kind='true four-tile common corner',seamX=320,seamY=320,sourcePixelScale=1,resampling=False))
    write(out/'index.json',dict(createdAt=now(),candidate=dict(file=str(candidate),sha256=sha(candidate)),sources={k:manifest['neighbors'][k] for k in ['north','west','northwest']},records=records,formalAccepted=False))
    print(str(out/'index.json'))

if __name__=='__main__':main()
