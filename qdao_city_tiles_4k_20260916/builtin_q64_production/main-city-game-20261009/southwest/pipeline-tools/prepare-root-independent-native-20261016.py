from pathlib import Path
import sys,json,argparse
B=Path(__file__).resolve().parents[1];sys.path.insert(0,str(B))
from native_pipeline import Pipeline,pid
class IndependentPipeline(Pipeline):
 def neighbor(self,row,col,side):
  rr,cc=(row,col-1) if side=='left' else (row-1,col)
  if rr>=1 and cc>=1 and self.selected_record(self.tile,rr,cc,optional=True) is None:
   self.warn('independent_internal_native_neighbor_unavailable',sourceTile=self.tile,patch=pid(rr,cc),side=side,acceptance=False,note='Actual absent internal source; independent continuation keeps guide at this side, never claims a native or passed seam.')
   return None
  return super().neighbor(row,col,side)
a=argparse.ArgumentParser();a.add_argument('tile');a.add_argument('--row',type=int,required=True);a.add_argument('--col',type=int,required=True);a.add_argument('--attempt',required=True);a.add_argument('--anchor-top');a.add_argument('--anchor-left');a.add_argument('--content-prefix');a.add_argument('--content-prefix-file');args=a.parse_args()
assert args.tile in {f'r{r:02d}_c06' for r in range(9,17)}
p=IndependentPipeline(args.tile);out=p.prepare(args);print(json.dumps(out,ensure_ascii=False))

