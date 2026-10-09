from pathlib import Path
import sys
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import helper as h
from PIL import Image
R=T/'repairs';D=R/'internal-ai';D.mkdir(exist_ok=True)
for n in ['native','prompts','evidence']:(D/n).mkdir(exist_ok=True)
src=R/'internal-quilt/r11_c10-internal-v2.png';a=Image.open(src)
items={'stone-upper':[397,627],'stone-lower':[397,2445],'leaf':[1900,2445],'post':[2842,1421]}
for n,(x,y) in items.items():
 f=D/(n+'-target.png');a.crop((x,y,x+1254,y+1254)).save(f);h.p.derived(f,[src],{'method':'native1254 QA fault context','originTileXY':[x,y]})
h.p.write(D/'targets.json',{'source':str(src),'sourceSHA':h.p.sha(src),'origins':items,'faults':{'stone-upper':'vertical incompatible material facets around x1024','stone-lower':'L-shape hardcut near x1110 y3040','leaf':'horizontal ownership cut through lower green rosette tips','post':'tiny outline jog left post around y2020'}})

