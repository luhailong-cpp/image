from pathlib import Path
import sys,json,numpy as np
from PIL import Image
sys.dont_write_bytecode=True
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import internal_qa as q
h=q.h;R=T/'repairs'
def prepare(folder,name,detail):
 d=R/folder;target=d/(name+'-target.png');refs=[target.as_posix(),h.STYLE]
 prompt='Use case: precise native map repair. Image1 is the exact EDIT TARGET, native1254 square. Image2 approved painting style only; no UI. '+detail+' Keep identical1254 crop, camera, object counts, architecture, leaf cluster silhouettes, main shapes, edge endpoints and material painting. Repair only the described artificial seams and their connected contours; retain all other pixels and outer200px context as faithfully as possible. Bright clean rounded Taoist Q fantasy handpainting, warm highlights/cool shadows, restrained smooth texture. No new objects, cracks, branches, denser foliage, grain, sharpening, blur or feathering. Reconcile material differences by painting coherent original details.'
 call={'prompt':prompt,'referenced_image_paths':refs,'transparent_background':False};h.p.write(d/'prompts'/(name+'.call.json'),call);(d/'prompts'/(name+'.prompt.txt')).write_text(prompt,encoding='utf8');print(json.dumps(call))
def ingest(folder,name,source):
 d=R/folder;h.p.ROOT=d;call=h.p.read(d/'prompts'/(name+'.call.json'));dest=h.p.ingest(source,name,d/'prompts'/(name+'.prompt.txt'),call['referenced_image_paths'],'native_ai_shared_or_internal_repair');rec=h.p.read(str(dest)+'.generation.json');rec['submittedParameters'].update(call);rec['evidence']['toolOutputHintFile']=str(d/'evidence'/(name+'.tool-result.json'));h.p.write(str(dest)+'.generation.json',rec)
if __name__=='__main__':
 if sys.argv[1]=='prepare':prepare(*sys.argv[2:])
 elif sys.argv[1]=='ingest':ingest(*sys.argv[2:])

