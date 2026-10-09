from pathlib import Path
import sys,numpy as np
from PIL import Image
O=Path(__file__).resolve().parent;R=O.parent.parent;B=R.parent;sys.path.insert(0,str(B));import production as p;p.ROOT=O
(O/'native').mkdir(exist_ok=True)
def ingest(name):
 call=p.read(O/(name+'.call.json'));r=p.read(O/(name+'.tool-result.json'));d=O/'native'/(name+'.png')
 if not d.exists():d=p.ingest(r['source'],name,O/(name+'.prompt.txt'),call['referenced_image_paths'],'native_seam_repair')
 rec=p.read(str(d)+'.generation.json');rec['submittedParameters'].update(call);rec['evidence']['actualToolResult']=str(O/(name+'.tool-result.json'));rec['visualInspection']={'at':p.stamp(),'scope':'actual returned native image reviewed; composited return QA separate'};p.write(str(d)+'.generation.json',rec);return d
if __name__=='__main__':
 for n in sys.argv[1:]:print(ingest(n))
