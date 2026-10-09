from pathlib import Path
from PIL import Image
import sys,json,hashlib,numpy as np
D=Path(__file__).resolve().parent;T=D.parents[1];R=T.parent;sys.path.insert(0,str(R/'tools/multi_edge'));import engine
def ref(p):return dict(file=str(p),sha256=hashlib.sha256(Path(p).read_bytes()).hexdigest())
def ar(p):return np.asarray(Image.open(p).convert('RGB'))
def write(p,v):p.write_bytes((json.dumps(v,indent=2)+'\n').encode())
plan=json.loads((T/'plan.json').read_text(encoding='utf-8-sig'));neighbors={k:ar(plan[key]) for k,key in [('north','northCandidate'),('east','eastCandidate'),('northeast','northEastCandidate')]};layout=engine.Layout();out=D/'current-only-v4/exact-north';out.mkdir(exist_ok=False)
source=D/'current-only-v4/bounded/p11-proposal.png';proposal=Image.open(source).convert('RGB');proposal.paste(Image.fromarray(neighbors['north']).crop((0,3981,1139,4096)),(115,0));p=out/'p11-proposal.png';proposal.save(p)
write(Path(str(p)+'.generation.json'),dict(**ref(p),derivedFrom=[ref(source),ref(plan['northCandidate'])],operation=dict(script=ref(__file__),sourceCropLTRB=[0,3981,1139,4096],pasteXY=[115,0],purpose='Restore exact known NORTH halo only to prevent repeated tone fitting to old AI approximation; current-owned pixels unchanged.'),actualModel=None,actualQuality=None,canonicalUnchanged=True,approvedForPromotion=False))
canvas,covered,_=engine.seed_neighbors(layout,neighbors);reports=[]
for c in [3,2,1,0]:
 src=p if c==0 else T/'native'/f'p1{c+1}.png';patch=ar(src);x,y=layout.origin(0,c);s=1254;context=canvas[y:y+s,x:x+s].copy();known=covered[y:y+s,x:x+s].copy();edges=engine.active_edges(layout,0,c,'NE',neighbors);owner=engine.owner_mask(known,edges,layout)
 merged,flow,tone,report=engine.register_native(context,patch,known,owner,edges,layout,max_shift=6.,tone_cap=18.,return_depth=256);canvas[y:y+s,x:x+s]=merged;covered[y:y+s,x:x+s]=True;reports.append(dict(source=ref(src),registration=report))
result=Image.fromarray(canvas[115:1254,115:4211]);row=out/'row1-assembled.png';result.save(row)
for label,box in [('qa-p11-north',(0,0,1024,400)),('qa-owner-x1024',(724,0,1324,400))]:
 x0,y0,x1,y1=box;joint=Image.new('RGB',(x1-x0,550));joint.paste(Image.fromarray(neighbors['north']).crop((x0,3946,x1,4096)),(0,0));joint.paste(result.crop(box),(0,150));q=out/(label+'.png');joint.save(q);write(Path(str(q)+'.generation.json'),dict(**ref(q),nativeScale=1,actuallyViewed=False,source=ref(row),north=ref(plan['northCandidate']),operation=dict(currentCropLTRB=list(box),northLast150=True)))
write(out/'diagnostic.json',dict(script=ref(__file__),plan=ref(T/'plan.json'),proposal=ref(p),registration=reports,pending=True,canonicalUnchanged=True,bottom230Unchanged=bool(np.array_equal(ar(p)[1024:],ar(T/'native/p11.png')[1024:]))));print(out)
