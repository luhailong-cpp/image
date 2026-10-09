from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
import ai_helper as h
O=Path(__file__).resolve().parent
base=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,f in {'cliff':'exec-3aba6405-9ff8-4849-bd78-605c3cf0cab3.png','post':'exec-c5104ab1-a6f5-4521-b7a9-852e3b6f5dc4.png','rightpost':'exec-7781d28e-9625-4434-b1ee-988ad66dba60.png'}.items():h.ingest(n+'-ai-v1',base/f)
