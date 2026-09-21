from pathlib import Path
import json,hashlib,shutil
from datetime import datetime,timezone
SRC=Path('E:/work/mmorpg-client');DST=Path('E:/work/tmp/city4k-review-20260921-r24')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not DST.exists(),'Preserve previous verification workspaces'
catalog=json.loads((SRC/'Assets/Editor/CityTiles4KReview/catalog.json').read_text())
assert len(catalog['candidates'])==24 and not catalog['runtimePublished']
files=['Assets/Scripts/World/Tianyong/CityTileManifest.cs','Assets/Editor/Tianyong/CityTile4KImporter.cs','Assets/Editor/Tianyong/CityTileCandidateReview.cs','Assets/Editor/CityTiles4KReview/catalog.json','ProjectSettings/ProjectVersion.txt','ProjectSettings/ProjectSettings.asset','ProjectSettings/GraphicsSettings.asset']+[e['assetPath'] for e in catalog['candidates']]
proof=[]
for f in files:
 a=SRC/f;b=DST/f;b.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(a,b);assert sha(a)==sha(b)
 proof.append({'relativePath':f,'source':str(a),'copy':str(b),'sha256':sha(a),'byteIdentical':True})
package=Path('E:/work/tmp/city4k-review-20260918/Packages/manifest.json');(DST/'Packages').mkdir();shutil.copyfile(package,DST/'Packages/manifest.json')
record={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'kind':'isolated_Unity_editor_import_render_verification','sourceProject':str(SRC),'isolationProject':str(DST),'unityVersion':'6000.6.0f1','copiedSources':proof,'candidateCount':24,'sourceLedgerSha256':catalog['sourceLedgerSha256'],'packageManifestSource':str(package),'packageManifestSha256':sha(package),'mainProjectCompileCheck':{'tool':'tools/client_compile_check.ps1','exitCode':1,'errorCount':8,'file':'Assets/Scripts/Game/Guild/GuildClient.cs','missingMessageIds':['NotifyGuildChanged','ListMyGuildApplications','ListGuildApplications','CancelGuildApplication','SetGuildMemberRole','KickGuildMember','TransferGuildLeader','ReviewGuildApplication'],'errorsUnrelatedToCityCandidateReview':True},'limits':['Same current city source code, PNG bytes, catalog and rendering settings; minimal built-in packages.','Does not establish a passing main project compile or whole-city runtime/foreground/navigation/device acceptance.'],'runtimePublished':False}
(DST/'isolation-provenance.json').write_text(json.dumps(record,indent=2),encoding='utf-8');print(str(DST))
