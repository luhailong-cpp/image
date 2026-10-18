from pathlib import Path
import importlib.util,json,sys
from argparse import Namespace
b=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('right_native_pipeline',b/'native_pipeline.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
tile,row,col,attempt=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
assert tile=='r13_c08' and row in (1,2,3,4) and col in (3,4)
p=mod.Pipeline(tile)
original=p.neighbor
def independent_neighbor(r,c,side):
 if side=='left' and c>1 and p.selected_record(tile,r,c-1,optional=True) is None:
  p.warn('independent_missing_internal_left_neighbor',sourceTile=tile,patch=mod.pid(r,c-1),side='left',reason='Cloud motif upstream layout unresolved; actual native absent. No invented or guide-based native anchor.')
  return None
 return original(r,c,side)
p.neighbor=independent_neighbor
print(json.dumps(p.prepare(Namespace(row=row,col=col,attempt=attempt,anchor_left=None,anchor_top=None,content_prefix=None,content_prefix_file=None)),ensure_ascii=False,indent=2))


