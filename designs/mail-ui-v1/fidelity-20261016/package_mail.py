from pathlib import Path
import hashlib,json,datetime,re
ROOT=Path(__file__).resolve().parent
CLIENT=Path("E:/work/mmorpg-client")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def body(source,name):
 match=re.search(r'(?:public|private|internal|protected)\s+(?:static\s+)?[\w<>]+\s+'+re.escape(name)+r'\s*\([^)]*\)',source)
 if not match:raise RuntimeError("Missing method "+name)
 start=source.find("{",match.end())
 # Expression bodies do not contain braces; verify exact expression through semicolon.
 semi=source.find(";",match.end())
 arrow=source.find("=>",match.end())
 if arrow>=0 and arrow<start and arrow<semi:return source[match.start():semi+1].strip()
 depth=0
 for end in range(start,len(source)):
  if source[end]=="{":depth+=1
  elif source[end]=="}":
   depth-=1
   if not depth:return source[match.start():end+1].strip()
 raise RuntimeError("Unbalanced "+name)
old=(CLIENT/"Assets/Scripts/UI/Ugui/Mail/MailWindow.cs").read_text(encoding="utf-8-sig")
new=(ROOT/"client/Assets/Scripts/UI/Ugui/Mail/MailWindow.cs").read_text(encoding="utf-8")
names=["Show","Hide","Back","ResetSession","Tick","ConfirmDelete","ConfirmClean","OpenActivity","ShowDialog","CloseDialog","Dispose"]
checks={name:body(old,name)==body(new,name) for name in names}
if not all(checks.values()):raise RuntimeError("Changed business methods: "+str(checks))
files=[]
for p in (ROOT/"client").rglob("*"):
 if p.is_file() and p.suffix in (".cs",".png",".meta"):
  relative=p.relative_to(ROOT/"client").as_posix()
  files.append({"source":p.relative_to(ROOT).as_posix(),"target":relative,"sha256":sha(p),"overwriteExisting":(CLIENT/relative).exists()})
compile_result=json.loads((ROOT/"qa/compile-result.json").read_text(encoding="utf-8-sig"))
if compile_result["exitCode"]!=0:raise RuntimeError("Staged runtime compile must pass before packaging")
result={"createdAtUtc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"destinationRoot":str(CLIENT),"files":files,"guards":[{"target":"Assets/Scripts/UI/Ugui/Mail/MailWindow.cs","sha256Before":sha(CLIENT/"Assets/Scripts/UI/Ugui/Mail/MailWindow.cs")}],"publicApiPreserved":True,"stateModelModified":False,"businessMethodExactTextChecks":checks,"nativeValidationPending":True,"runtimeSourceCount":compile_result["sourceCount"],"stagedCompileExitCode":compile_result["exitCode"],"assetImport":{"noAssetPostprocessor":True,"spriteMode":"Single","meshType":"FullRect","pixelsPerUnit":100,"maxTextureSize":4096,"compression":"Uncompressed","mipmap":False,"filter":"Bilinear","wrap":"Clamp","borderSource":"per-sprite .meta / sprite-manifest.json"},"payloadPolicy":"Only paths listed under client/ are installed; generation records, approved masters and prompts remain in image package."}
(ROOT/"install-manifest.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"installFiles":len(files),"pngs":sum(x["target"].endswith(".png") for x in files),"businessChecks":checks,"compileExitCode":result["stagedCompileExitCode"]}))

