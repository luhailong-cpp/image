from pathlib import Path
from PIL import Image
import json,numpy as np,sys,hashlib
R=Path(__file__).resolve().parent;bindfile=Path(sys.argv[1]);Q=Path(sys.argv[2]);Q.mkdir(exist_ok=True)
bind=json.loads(bindfile.read_text())["sources"];a={k:np.array(Image.open(v["file"]).convert("RGB")) for k,v in bind.items()}
for row in [8,9]:
 for l,r in [(7,8),(8,9)]:
  left=f"r{row:02d}_c{l:02d}";right=f"r{row:02d}_c{r:02d}";key=left+"__"+right
  strip=np.concatenate([a[left][:,-192:],a[right][:,:192]],axis=1)
  board=np.concatenate([strip[i*1024:(i+1)*1024].transpose(1,0,2) for i in range(4)],axis=0)
  Image.fromarray(board).save(Q/(key+"-full.png"))
for c in [7,8]:
 tl=a[f"r08_c{c:02d}"][-627:,-627:];tr=a[f"r08_c{c+1:02d}"][-627:,:627];bl=a[f"r09_c{c:02d}"][:627,-627:];br=a[f"r09_c{c+1:02d}"][:627,:627]
 im=np.concatenate([np.concatenate([tl,tr],axis=1),np.concatenate([bl,br],axis=1)],axis=0);Image.fromarray(im).save(Q/f"corner-r08r09-c{c:02d}c{c+1:02d}.png")
print(Q)
