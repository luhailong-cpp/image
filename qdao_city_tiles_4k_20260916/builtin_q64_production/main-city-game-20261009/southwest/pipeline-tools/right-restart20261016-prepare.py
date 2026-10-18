from pathlib import Path
import importlib.util,json,sys,hashlib
from argparse import Namespace
B=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('right_restart_native_pipeline',B/'native_pipeline.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
tile,row,col,attempt=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
assert ((tile=='r11_c08' and row in (2,3,4) and col in (2,3,4)) or (tile in ('r14_c08','r15_c08','r16_c08') and row in (1,2,3,4) and col in (3,4)))
p=mod.Pipeline(tile);original=p.neighbor
def neighbor(r,c,side):
 if side=='left' and c>1 and p.selected_record(tile,r,c-1,optional=True) is None:
  p.warn('independent_missing_internal_left_neighbor',sourceTile=tile,patch=mod.pid(r,c-1),side='left',reason='Upstream left sources unresolved or absent; missing native not invented. Independent stable native top continues.')
  return None
 return original(r,c,side)
p.neighbor=neighbor
result=p.prepare(Namespace(row=row,col=col,attempt=attempt,anchor_left=None,anchor_top=None,content_prefix=None,content_prefix_file=None))
request=Path(result['request']);r=json.loads(request.read_text(encoding='utf-8-sig'))
quiet=B/'r12_c08/pipeline/guides/quiet-native-stone-20261016-v01.png'
r['references'].append({'file':str(quiet),'sha256':hashlib.sha256(quiet.read_bytes()).hexdigest(),'role':'quiet native stone material only; exact geometry is image1'})
r['referenced_image_paths']=[x['file'] for x in r['references']]
prefix=Path(sys.argv[5]).read_text(encoding='utf-8-sig') if len(sys.argv)>5 else ''
prompt=prefix+'\n'+r['prompt']
pf=Path(r['promptFile']);pf.write_text(prompt,encoding='utf-8')
r['prompt']=prompt;r['promptSha256']=hashlib.sha256(pf.read_bytes()).hexdigest()
request.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
