from pathlib import Path
import subprocess,json,re
ROOT=Path(__file__).resolve().parent;PACKAGE=ROOT.parent;CLIENT=Path('E:/work/mmorpg-client')
text=(PACKAGE/'equipment-compat-editor.rsp').read_text(encoding='utf-8-sig')
text=text.replace(str(PACKAGE/'staged').replace('/','\\'),str(CLIENT).replace('/','\\'))
relative='Assets/Editor/EquipmentForgeUiVerification.cs'
text=text.replace(str(CLIENT/relative).replace('/','\\'),str(ROOT/'staged'/relative).replace('/','\\'))
text=text.replace(str(PACKAGE/'equipment-compat-runtime.dll').replace('/','\\'),str(PACKAGE/'visual-fixes-20261017/runtime.dll').replace('/','\\'))
text=re.sub(r'-out:"[^"]+"','-out:"'+str(ROOT/'editor.dll').replace('\\','/')+'"',text)
(ROOT/'editor.rsp').write_text(text,encoding='utf-8')
p=subprocess.run(['C:/Program Files/dotnet/dotnet.exe','exec','C:/Program Files/dotnet/sdk/10.0.400/Roslyn/bincore/csc.dll','@'+str(ROOT/'editor.rsp')],cwd=CLIENT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace')
(ROOT/'compile-validation.json').write_text(json.dumps(dict(editor_sources=3,exit_code=p.returncode,output=p.stdout.splitlines(),executed_in_unity=False),ensure_ascii=False,indent=2),encoding='utf-8')
print(p.returncode)
