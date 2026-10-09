from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h
h.O=O/'west';D=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,f in {'west-1':'exec-93208686-f560-4d94-bc7b-d3284c5501fb.png','west-2':'exec-9b822ce9-37e7-4289-82cf-785d7907d413.png','west-3':'exec-4eac1cc9-17b6-4e0f-b59e-edb52bb75d34.png','west-4':'exec-1a48f64e-eb24-4044-8646-df42f9a1fe64.png'}.items():print(h.ingest(n,D/f))
