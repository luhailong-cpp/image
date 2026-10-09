from pathlib import Path
D=Path(__file__).parent
s=(D/'assemble-post-final-v7.py').read_text()
s=s.replace("F=D/'final-v7'","F=D/'final-v8'").replace('(1-s((x-1135)/55))','(1-s((x-1238)/16))')
exec(compile(s,str(__file__),'exec'))
