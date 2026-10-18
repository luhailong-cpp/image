from pathlib import Path
from datetime import datetime,timezone
import json
B=Path(__file__).resolve().parents[1];T=B/'r15_c06'
for p in (T/'pipeline/anchors').glob('*.png'):
 old=p.with_suffix('.derivation.json');new=Path(str(p)+'.derivation.json');assert old.exists() and not new.exists();new.write_bytes(old.read_bytes())
d={'recordedAtUtc':datetime.now(timezone.utc).isoformat(),'tile':'r15_c06','patch':'p01_01','status':'prepared_not_submitted_held_specific_upstream_geometry','actualGuideViewed':True,'upstreamTile':'r15_c05','upstreamCurrentContextSha256':'d78cc862468b1082b7f3dec851bd89263302c6854de0b61e79a08b44e608d214','issue':'Existing source blue band contains extra white rim, also open in source worker QA. Do not propagate it as accepted geometry.','sourceWorkerAcknowledged':True,'next':'Advance true missing p0102 and other independent patches; source worker will inspect only this rim after finishing current near-full block.','formalAccepted':False}
p=T/'pipeline/held-p0101-upstream-rim-20261016-v01.json';assert not p.exists();p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(p)

