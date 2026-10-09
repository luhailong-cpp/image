from pathlib import Path
D=Path(__file__).parent
s=(D.parent/'grid-assemble.py').read_text();s=s.replace("D=Path(sys.argv[1]);F=D/'final-v1'","D=Path(__file__).parent;F=D/'final-v2'").replace('smooth((y-1040)/160)','smooth((y-1125)/40)').replace("'bottomSourceSmoothstepY':[1040,1200]","'bottomSourceSmoothstepY':[1125,1165]")
exec(compile(s,str(__file__),'exec'))
