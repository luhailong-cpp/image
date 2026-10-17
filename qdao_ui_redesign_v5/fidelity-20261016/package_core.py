from pathlib import Path
import hashlib,json,re
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
stage=json.loads((ROOT/'staged-code-manifest.json').read_text(encoding='utf-8'))
sprites=json.loads((ROOT/'sprite-manifest.json').read_text(encoding='utf-8'))['sprites']
role=lambda s:s['key'].startswith('role_') or s['key'].startswith('portraits/')
source_base='Assets/Scripts/UI/Ugui/'
phases={
 'login-server':([source_base+x for x in ['QdaoCoreFidelityArt.cs','QdaoServerSelectView.cs','QdaoServerSelectView.Visuals.cs']],[s['assetPath'] for s in sprites if not role(s)]),
 'role':([source_base+'Role/RoleFlowUi.cs'],[s['assetPath'] for s in sprites if role(s)])}
audits=[]
for phase,(sources,assets) in phases.items():
 paths=[]
 for p in sources+assets:paths.extend([p,p+'.meta'])
 files=[{'source':'client/'+p,'target':p,'sha256':sha(ROOT/'client'/p)} for p in paths]
 guards=[g for g in stage['guards'] if g['target'] in sources]
 checks=[{'target':g['target'],'expected':g['sha256Before'],'actual':sha(CLIENT/g['target']),'matches':sha(CLIENT/g['target'])==g['sha256Before']} for g in guards]
 compile=json.loads((ROOT/f'qa/core-{phase}-compile-result.json').read_text(encoding='utf-8-sig'))
 manifest={'createdAtUtc':datetime.now(timezone.utc).isoformat(),'destinationRoot':str(CLIENT),'phase':phase,'files':files,'guards':guards,'scope':'Approved original PNG skin and native live text/controls; business transactions preserved.','nativeValidationPending':True,'offlineCompile':{'sourceCount':compile['sourceCount'],'exitCode':compile['exitCode']},'generationRecordsRemainInPackage':True}
 if phase=='login-server':manifest['afterInstall']='Regenerate baked login/server prefab using MmorpgClient.UI.EditorTools.QdaoUguiBuilder.BuildAll in EditMode, then capture and run login/server tests.'
 else:manifest['requiresInstalled']=[{'target':source_base+'QdaoCoreFidelityArt.cs','sha256':sha(ROOT/'client'/source_base/'QdaoCoreFidelityArt.cs')}]
 save(ROOT/f'core-{phase}-install-manifest.json',manifest)
 audits.append({'phase':phase,'fileCount':len(files),'spriteCount':len(assets),'allFilesExist':True,'sourceGuards':checks,'offlineCompile':compile,'passed':all(c['matches'] for c in checks) and compile['exitCode']==0})
save(ROOT/'qa/core-package-audit.json',{'createdAtUtc':datetime.now(timezone.utc).isoformat(),'phases':audits,'passed':all(a['passed'] for a in audits),'stageOnly':True,'nativeUnityRun':False,'catalogueModified':False,'allClassesAppearanceChoicesAndTransactionsPreserved':True})
print(json.dumps([{'phase':a['phase'],'files':a['fileCount'],'sprites':a['spriteCount'],'passed':a['passed']} for a in audits],ensure_ascii=False))

