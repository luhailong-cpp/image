from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from production import *
f=ROOT/'r10_c13';source=f/'references/structure-aligned-extended.png'
assert sha(source)=='a064afc1665eba71d9e45f0065b5cfa299eb0f6a88c935bbf0cae836ba65867e'
guide=f/'guides/p11.png';guide.parent.mkdir(exist_ok=True)
assert not guide.exists()
scale=1164/4096
box=[90-115*scale,90-115*scale,90+1139*scale,90+1139*scale]
Image.open(source).convert('RGB').transform((1254,1254),Image.Transform.EXTENT,box,Image.Resampling.BICUBIC).save(guide)
deriv(guide,[source],dict(kind='same_frame_structure_guide_only',sourceExtentLTRB=box,coreSourceLTRB=[90,90,1254,1254],coreFinalPixels=4096,coreOffsetIn4326=115,guideUpscaled=True,productionPixels=False,resampling='BICUBIC',globalPatchXYWH=[49037,36749,1254,1254]))
p=read(f/'plan.json');h=read(ROOT/'handoff.json');p['northWestCandidate']=next(b['file'] for b in h['baselineCandidates'] if b['tile']=='r09_c12')
p['candidateSourcesStillUnderScopedRepair']=False
p['frozenCoreSource']=dict(file=str(source),sha256=sha(source),coreLTRB=[90,90,1254,1254],role='planning only')
p['frozenCurrentNeighbors']={k:dict(file=p[k],sha256=sha(p[k])) for k in ['northCandidate','westCandidate','northWestCandidate']}
write(f/'plan.json',p)
print(str(guide))
