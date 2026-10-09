from pathlib import Path
import sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent;sys.path.insert(0,str(O.parent/'internal'));import ai_helper as h
h.O=O/'west';h.ingest('west-wall-clean','C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c/exec-cab5275e-8718-492d-b49a-1457e494d082.png')
