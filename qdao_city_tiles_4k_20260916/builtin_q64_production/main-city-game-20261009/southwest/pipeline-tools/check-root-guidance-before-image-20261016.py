from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,sys
R=Path('D:/work/image');expected='57f1ad4f81fdb2256b843923d862308be228130917b99cfced375db256aff01a'
raw=(R/'AGENTS.md').read_bytes();body=raw.decode('utf-8-sig');h=hashlib.sha256(raw).hexdigest()
if h!=expected:
 print(body);print('AGENTS changed: read new instructions before any image call.');raise SystemExit(2)
mraw=(R/'docs/MAP_PARALLEL_SPLIT_20261013.json').read_bytes();m=json.loads(mraw.decode('utf-8-sig'));tile=sys.argv[1]
conflicts=[v for v in m['batches'] if v['map']=='main-city-game-20261009' and v['status']=='allocated_root_reserved' and tile in v['tiles']]
print(json.dumps({'readAtUtc':datetime.now(timezone.utc).isoformat(),'AGENTSReadInFull':True,'AGENTSSha256':h,'unchangedSinceActualFullRead':True,'parallelManifestReadInFull':True,'parallelManifestSha256':hashlib.sha256(mraw).hexdigest(),'tile':tile,'reservedConflicts':conflicts,'builtinOnly':True,'actualModelIfUndisclosed':None,'paidApiAllowed':False},ensure_ascii=False))
if conflicts:raise SystemExit(3)

