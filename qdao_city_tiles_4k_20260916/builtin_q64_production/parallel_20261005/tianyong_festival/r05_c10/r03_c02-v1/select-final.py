from pathlib import Path
import json
D=Path(__file__).parent;p=D/'request.json';r=json.loads(p.read_text());r['selectedFinalDirectory']='final-v2';p.write_text(json.dumps(r,indent=2));(D/'qa-accepted.txt').write_text('Whole1254 native tree/floor/planter composition reviewed. Left tree contours remain continuous; bottom horizontal joint selected wholly from new native until clear lower stone face, then exact source; bottom native strip reviewed with no doubled seam. No unresolved local visual finding. Formal acceptance remains false.')
