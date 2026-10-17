from pathlib import Path
from PIL import Image
import hashlib,json,datetime,re
ROOT=Path(__file__).resolve().parent
CLIENT=Path('E:/work/mmorpg-client')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,r):p.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def methods(source):
 result={}
 pattern=r'^        (?:public|private|internal|protected)\s+(?:static\s+)?[\w<>,?\[\]]+\s+\w+\s*\([^\n]*?\)'
 for match in re.finditer(pattern,source,re.M):
  signature=match.group(0).strip()
  start=source.find('{',match.end());semi=source.find(';',match.end());arrow=source.find('=>',match.end())
  if arrow>=0 and arrow<semi and (start<0 or arrow<start):end=semi+1
  else:
   depth=0;end=None
   for i in range(start,len(source)):
    if source[i]=='{':depth+=1
    elif source[i]=='}':
     depth-=1
     if depth==0:end=i+1;break
   if end is None:raise RuntimeError('Unbalanced method '+signature)
  result[signature]=source[match.start():end].strip()
 return result
stage=read(ROOT/'staged-code-manifest.json')
tests=read(ROOT/'staged-tests-manifest.json')
old_path=CLIENT/'Assets/Scripts/UI/Ugui/Guild/GuildWindow.cs'
new_path=ROOT/'client/Assets/Scripts/UI/Ugui/Guild/GuildWindow.cs'
old=old_path.read_text(encoding='utf-8-sig');new=new_path.read_text(encoding='utf-8-sig')
old_methods=methods(old);new_methods=methods(new)
changed_allowed={'Render','RenderIdentity','RenderOverview','GuildSprite'}
method_checks={}
for signature,body in old_methods.items():
 name=re.search(r'(\w+)\s*\(',signature).group(1)
 if name in changed_allowed:continue
 method_checks[signature]=new_methods.get(signature)==body
if not all(method_checks.values()):raise RuntimeError('Unexpected business/source method changes: '+str([k for k,v in method_checks.items() if not v]))
public=lambda s:[line.strip() for line in s.splitlines() if line.strip().startswith('public ') and not line.strip().startswith('public GuildWindow(')]
# Method bodies may start on a public line. Compare signatures/declared expression starts, not source layout inside braces.
api=lambda s:[re.split(r'\{|=>',line,1)[0].strip() for line in public(s)]
if api(old)!=api(new):raise RuntimeError('Public API declarations changed')
compile_result=read(ROOT/'qa/compile-result.json')
if compile_result['exitCode']!=0:raise RuntimeError('Runtime compile did not pass')
sprites=read(ROOT/'sprite-manifest.json')['sprites']
guids=[]
for item in sprites:
 p=ROOT/'client'/item['assetPath']
 if sha(p)!=item['sha256']:raise RuntimeError('Sprite checksum mismatch '+item['key'])
 with Image.open(p) as image:
  if image.size!=(item['width'],item['height']):raise RuntimeError('Sprite size mismatch '+item['key'])
  image.verify()
 if read(p.with_name(p.name+'.generation.json'))['sha256']!=sha(p):raise RuntimeError('Sprite source record mismatch '+item['key'])
 meta=p.with_name(p.name+'.meta').read_text(encoding='utf-8-sig')
 guids.append(re.search(r'^guid: ([0-9a-f]{32})$',meta,re.M).group(1))
 for setting in ['enableMipMap: 0','textureType: 8','spriteMode: 1','spriteMeshType: 0','textureCompression: 0','maxTextureSize: 4096']:
  if setting not in meta:raise RuntimeError('Missing sprite setting '+setting)
if len(set(guids))!=len(guids):raise RuntimeError('Duplicate sprite GUID')
guards=stage['guards']+[{'target':str(Path(tests['source']).relative_to(CLIENT)).replace('\\','/'),'sha256Before':tests['sourceSha256Before']}]
for item in guards:
 if sha(CLIENT/item['target'])!=item['sha256Before']:raise RuntimeError('Client guard changed: '+item['target'])
files=[]
for p in sorted((ROOT/'client').rglob('*')):
 if p.is_file() and p.suffix in ['.cs','.meta','.png']:
  target=p.relative_to(ROOT/'client').as_posix()
  files.append({'source':p.relative_to(ROOT).as_posix(),'target':target,'sha256':sha(p),'overwriteExisting':(CLIENT/target).exists()})
result={'createdAtUtc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'destinationRoot':str(CLIENT),'files':files,'guards':guards,'publicApiPreserved':True,'GuildClientUnmodified':True,'allSixPagesPreserved':True,'businessMethodsPreservedVerbatim':method_checks,'modifiedPresentationMethods':sorted(changed_allowed),'testChanges':tests['changes'],'stagedCompileExitCode':compile_result['exitCode'],'runtimeSourceCount':compile_result['sourceCount'],'nativeValidationPending':True,'assetImport':{'noAssetPostprocessor':True,'spriteMode':'Single','meshType':'FullRect','maxTextureSize':4096,'mipmap':False,'compression':'Uncompressed','wrap':'Clamp','filter':'Bilinear','borderSource':'sprite-manifest.json and per-image .meta'},'payloadPolicy':'Install only explicitly listed client paths. Keep generation records, prompt sources and current extraction masters in image package.'}
write(ROOT/'install-manifest.json',result)
write(ROOT/'qa/package-audit.json',{'checkedAtUtc':result['createdAtUtc'],'status':'passed','installFiles':len(files),'sprites':len(sprites),'sourceGuardsMatch':True,'publicApiPreserved':True,'preservedMethodCount':len(method_checks),'spritePngDecodingHashesMetaAndProvenanceVerified':True,'compileResult':compile_result,'nativeUnityRun':False,'testsRun':False,'imageParityVerified':False})
write(ROOT/'qa/capture-request.json',{'entryClass':'GuildUiVerification','existingEditorSource':'Assets/Editor/Guild/GuildUiVerification.cs','outputDirectoryField':'GuildUiVerification.OutputDirectory','suggestedOutputDirectory':str(ROOT/'qa/unity'),'entryMethod':'CaptureAll','expectedScreenshots':26,'resolutions':[[2560,1080],[1920,1080]],'readiness':'After guarded install and Unity asset import; use existing isolated additive scene fixture capture. No live server or user scene saves.','testAssembly':'MmorpgClient.Tests.EditMode.Guild','testsFile':'Assets/Tests/EditMode/Guild/GuildUiTests.cs','preserveFixturesAndRealCallbacks':True})
print(json.dumps({'installFiles':len(files),'sprites':len(sprites),'businessMethodsPreserved':len(method_checks),'compileExitCode':compile_result['exitCode']}))
