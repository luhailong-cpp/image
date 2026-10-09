from pathlib import Path
from PIL import Image
import sys,json,hashlib,numpy as np
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
def ref(p):return dict(file=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
plan=json.loads((T/'plan.json').read_text(encoding='utf-8-sig'));neighbors={k:ar(plan[key]) for k,key in [('north','northCandidate'),('east','eastCandidate'),('northeast','northEastCandidate')]};layout=engine.Layout();out=D/'row1-ownership-review';out.mkdir(exist_ok=False)
for variant in ['raw','v4']:
 canvas,covered,_=engine.seed_neighbors(layout,neighbors);reports=[]
 for c in [3,2,1,0]:
  source=(D/'current-only-v4/bounded/p11-proposal.png') if variant=='v4' and c==0 else T/'native'/f'p1{c+1}.png';patch=ar(source);x,y=layout.origin(0,c);s=1254;context=canvas[y:y+s,x:x+s].copy();known=covered[y:y+s,x:x+s].copy();edges=engine.active_edges(layout,0,c,'NE',neighbors);owner=engine.owner_mask(known,edges,layout)
  merged,flow,tone,report=engine.register_native(context,patch,known,owner,edges,layout,max_shift=6.,tone_cap=18.,return_depth=256);canvas[y:y+s,x:x+s]=merged;covered[y:y+s,x:x+s]=True;reports.append(dict(source=ref(source),registration=report))
 result=Image.fromarray(canvas[115:1254,115:4211]);row=out/(variant+'-row1-assembled.png');result.save(row)
 for c in [0,1,2,3]:
  joint=Image.new('RGB',(1024,550));joint.paste(Image.fromarray(neighbors['north']).crop((c*1024,3946,c*1024+1024,4096)),(0,0));joint.paste(result.crop((c*1024,0,c*1024+1024,400)),(0,150));p=out/f'{variant}-qa-p1{c+1}-north.png';joint.save(p);write(Path(str(p)+'.generation.json'),dict(**ref(p),nativeScale=1,actuallyViewed=False,source=ref(row),north=ref(plan['northCandidate']),operation=dict(tileXStart=c*1024,northLast150=True,currentFirst400=True)))
 crossing=Image.new('RGB',(600,550));crossing.paste(Image.fromarray(neighbors['north']).crop((724,3946,1324,4096)),(0,0));crossing.paste(result.crop((724,0,1324,400)),(0,150));crossing.save(out/(variant+'-qa-owner-x1024.png'));write(out/(variant+'-registration.json'),dict(plan=ref(T/'plan.json'),sourcePNGsUnchanged=True,partialRowOnlyNotProductionCandidate=True,row=ref(row),patches=reports,actuallyViewed=False))
print(out)
