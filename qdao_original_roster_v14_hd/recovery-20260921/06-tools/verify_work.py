"""Independently reconstruct every present 06-work walk PNG without requiring absent slots."""
from pathlib import Path
import argparse,importlib.util,json,hashlib
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];WORK=HERE.parent/'06-work';CHAR='06_thunder_caster_boy'
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
p=argparse.ArgumentParser();p.add_argument('--direction');a=p.parse_args()
v=module('verify_work06',HERE/'alpha_verify.py');v.ROOT=WORK;v.mod=lambda name:module('verify_work06_'+name,ROOT/'tools/vendor'/f'{name}.py')
out=WORK/'candidate'/CHAR;reports=[]
for image in sorted((out/'walk').glob('*/*.png')):
    direction=image.parent.name
    if a.direction and direction!=a.direction:continue
    try:report=v.verify(CHAR,direction,False,int(image.stem))
    except Exception as exc:report={'status':'failed','scope':f'{direction}/{image.stem}','error':str(exc)}
    reports.append(report)
summary={'character':CHAR,'count':len(reports),'all_present_frames_rebuilt':all(r['status']=='partial_sources_pending_visual' for r in reports),
         'manifest_sha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'reports':reports,'visual_review':'pending','formal_approval':False}
dest=out/'review'/f"reconstruction-{a.direction or 'all-present'}.json";dest.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'count':len(reports),'all_present_frames_rebuilt':summary['all_present_frames_rebuilt'],'report':str(dest)}))
raise SystemExit(0 if summary['all_present_frames_rebuilt'] else 1)
