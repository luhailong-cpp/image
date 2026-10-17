from pathlib import Path
import subprocess,json,re
ROOT=Path(__file__).resolve().parent;PACKAGE=ROOT.parent
DOTNET='C:/Program Files/dotnet/dotnet.exe'
CSC='C:/Program Files/dotnet/sdk/10.0.400/Roslyn/bincore/csc.dll'
CLIENT=Path('E:/work/mmorpg-client')
old_stage=str(PACKAGE/'staged').replace('/','\\')
client=str(CLIENT).replace('/','\\')
new_stage=str(ROOT/'staged').replace('/','\\')
runtime=(PACKAGE/'equipment-compat-runtime.rsp').read_text(encoding='utf-8-sig').replace(old_stage,client)
for p in ['Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.cs','Assets/Scripts/UI/Ugui/Gameplay/GameplayWindow.Fidelity.cs']:
    runtime=runtime.replace(client+'\\'+p.replace('/','\\'),new_stage+'\\'+p.replace('/','\\'))
runtime=re.sub(r'-out:"[^"]+"','-out:"'+str(ROOT/'runtime.dll').replace('\\','/')+'"',runtime)
(ROOT/'runtime.rsp').write_text(runtime,encoding='utf-8')
result={'executed_in_unity':False}
def run(name):
    process=subprocess.run([DOTNET,'exec',CSC,'@'+str(ROOT/(name+'.rsp'))],cwd=CLIENT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace')
    result[name+'_exit_code']=process.returncode;result[name+'_output']=process.stdout.splitlines()
    (ROOT/(name+'.log')).write_text(process.stdout,encoding='utf-8');print(name,process.returncode,flush=True)
run('runtime')
if result['runtime_exit_code']==0:
    tests=(PACKAGE/'equipment-compat-tests.rsp').read_text(encoding='utf-8-sig').replace(old_stage,client)
    for p in ['Assets/Tests/EditMode/Battle/EquipForgeWindowTests.cs','Assets/Tests/EditMode/Battle/GameplayWindowTests.cs']:
        tests=tests.replace(client+'\\'+p.replace('/','\\'),new_stage+'\\'+p.replace('/','\\'))
    tests=tests.replace(str(PACKAGE/'equipment-compat-runtime.dll').replace('/','\\'),str(ROOT/'runtime.dll').replace('/','\\'))
    tests=re.sub(r'-out:"[^"]+"','-out:"'+str(ROOT/'tests.dll').replace('\\','/')+'"',tests)
    (ROOT/'tests.rsp').write_text(tests,encoding='utf-8')
    result['test_source_count']=sum(1 for line in tests.splitlines() if line.startswith('"') and '.cs"' in line)
    run('tests')
(ROOT/'compile-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
