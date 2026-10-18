import sys,json
from pathlib import Path
T=Path(__file__).resolve().parent;sys.path.insert(0,str(T));import workflow_20261016 as w
identifier,prompt=sys.argv[1:3];e=w.check_rules();a={'prompt':prompt,'referenced_image_paths':[str(T/'layout-only'/(identifier+'.actual-core-guide.png'))],'transparent_background':False}
w.p.write_json(T/'planned'/(identifier+'.parameters.json'),a,replace=False);w.p.write_json(T/'receipts'/(identifier+'.rules-read.json'),e,replace=False);w.p.record_request(w.TILE,identifier,T/'planned'/(identifier+'.parameters.json'));print(json.dumps(a))
