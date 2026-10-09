from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h
h.O=O/'north'
D=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,f in {'north-1':'exec-c84de01e-3c27-4299-88f2-e17a5fbc31d4.png','north-2':'exec-137fe6cd-d8c5-476f-bad6-742ebab76b8f.png','north-3':'exec-4e82e290-4707-4bc8-9e71-6a12c5bfef9f.png','north-4':'exec-f341f1b3-768d-4104-aed3-18a7334a5391.png'}.items():print(h.ingest(n,D/f))
