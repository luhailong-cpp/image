from pathlib import Path
import json, hashlib
d=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/tianyong_festival/r08_c10/r02_c03-v2')
p=d/'preparation.json'; v=json.loads(p.read_text(encoding='utf-8-sig'))
v['prospectiveContext']={'file':str(d.parent/'r02_c02-v1/native.png'),'sha256':'7f19b16fc2c06ea57b8f5ce99eeb8061de19f6f96b1fd7f104ea44a3acf1d79f','cropLTRB':[1024,230,1254,900],'pasteXY':[0,230],'accepted':False,'committed':False,'role':'Uncommitted adjacent native artwork, provisional continuation guide. Must rebase against committed neighbor before placement.','knownStableBoundsOnly':True}
p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print((d/'request.json').read_text(encoding='utf-8-sig'))
