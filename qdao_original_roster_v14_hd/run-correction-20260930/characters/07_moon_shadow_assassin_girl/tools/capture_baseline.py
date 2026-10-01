import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parent.parent
CHAR=ROOT.name
WORKSPACE=ROOT.parents[3]
CLIENT=WORKSPACE.parent/'mmorpg-client/Assets/Resources/World/Characters/QdaoOriginalRosterV14'/CHAR
OLD=WORKSPACE/'qdao_original_roster_v14_hd/recovery-20260921/07-tools/candidate'/CHAR
def facts(p):
    d={'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'modifiedAt':datetime.fromtimestamp(p.stat().st_mtime,timezone.utc).isoformat()}
    if p.suffix=='.png':
        with Image.open(p) as i: d.update(width=i.width,height=i.height,mode=i.mode)
    return d
rows=[]
for direction in ['E','SE']:
    for frame in ['01','09']:
        a=facts(CLIENT/'walk'/direction/(frame+'.png')); b=facts(OLD/'walk'/direction/(frame+'.png'))
        rows.append({'direction':direction,'frame':frame,'client':a,'oldCandidate':b,'sameSHA':a['sha256']==b['sha256']})
out={'readAt':datetime.now(timezone.utc).isoformat(),'character':CHAR,'sample':rows,'appearance':json.loads((CLIENT/'appearance.json').read_text(encoding='utf-8')),'metadataSources':[facts(CLIENT/'appearance.json'),facts(CLIENT/'manifest.json')],'observedIssues':['Old E and SE legs vary, but arms mostly extended down/out with display-position daggers.','Old exporter forced lowest alpha to y942, removing flight offset.','Asymmetric hair ornament is on anatomical left, mostly hidden in E.'],'newAcceptanceInherited':False,'clientWritten':False,'unityStarted':False}
(ROOT/'baseline-source.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'samples':len(rows),'allMatch':all(r['sameSHA'] for r in rows),'appearanceSHA256':out['metadataSources'][0]['sha256']}))
