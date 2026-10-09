from pathlib import Path
import json
D=Path(__file__).parent
s=(D.parent/'grid-assemble.py').read_text().replace("D=Path(sys.argv[1]);F=D/'final-v1'","D=Path(__file__).parent;F=D/'final-v2'").replace('smooth((y-1040)/160)','smooth((y-1024)/16)').replace("'bottomSourceSmoothstepY':[1040,1200]","'bottomSourceSmoothstepY':[1024,1040]")
exec(compile(s,str(__file__),'exec'))
r=json.loads((D/'request.json').read_text(encoding='utf-8-sig'));r['selectedFinalDirectory']='final-v2';(D/'request.json').write_text(json.dumps(r,indent=2))
