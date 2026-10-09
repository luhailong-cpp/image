import helper as h
from pathlib import Path
src=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,p in {'p13':'exec-72b14693-42fc-4865-a544-0dcf8d52648b.png','p22':'exec-d6f3241f-9606-4157-8848-5f39f027da53.png','p31':'exec-0f23368a-5228-406d-9a42-80cfd1fa38ce.png'}.items():h.ingest(str(src/p),n)
