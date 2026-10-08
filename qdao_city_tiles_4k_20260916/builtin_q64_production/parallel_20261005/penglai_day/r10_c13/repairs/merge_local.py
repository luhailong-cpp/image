from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
import numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;T=R.parent
sys.path.insert(0,str(R));import seam_local as s
def apply(base,rep,mask,origin):
    x,y=origin;hh,ww=rep.shape[:2];tx0=max(0,x);ty0=max(0,y);tx1=min(base.shape[1],x+ww);ty1=min(base.shape[0],y+hh)
    a=base[ty0:ty1,tx0:tx1];b=rep[ty0-y:ty1-y,tx0-x:tx1-x];m=mask[ty0-y:ty1-y,tx0-x:tx1-x]
    base[ty0:ty1,tx0:tx1]=np.where(m[:,:,None],b,a)
def merge():
    raw=T/'tiles/r10_c13-candidate.png';base=s.arr(raw);sources=[raw];entries=[]
    for name,origin in [('roof-x1024',(397,0)),('paving-y3072',(0,2445)),('wall-y3072',(2842,2445))]:
        rep=R/(name+'-replacement.png');mp=R/(name+'-mask.png');apply(base,s.arr(rep),np.asarray(Image.open(mp))>0,origin);sources.extend([rep,mp]);entries.append({'name':name,'replacement':str(rep),'mask':str(mp),'origin':origin})
    fabric=s.h.p.read(R/'fabric-repairs/fabric-merge-manifest-v4.json')
    for name,e in fabric['repairs'].items():
        rep=Path(e['replacement']);mp=Path(e['mask']);assert s.h.p.sha(rep)==e['replacementSha256'];assert s.h.p.sha(mp)==e['maskSha256'];apply(base,s.arr(rep),np.asarray(Image.open(mp))>0,e['origin']);sources.extend([rep,mp]);entries.append(e)
    dest=R/'r10_c13-internal-ai-v3.png';s.save(base,dest,sources,{'method':'six independent native AI repairs applied with exact binary masks and bounded recorded RGB return fields','resampling':None,'formalAccepted':False});s.qa(base,'internal-ai-v3',dest)
    s.h.p.write(R/'internal-ai-v3-manifest.json',{'file':str(dest),'sha256':s.h.p.sha(dest),'entries':entries,'formalAccepted':False})
if __name__=='__main__':merge()
