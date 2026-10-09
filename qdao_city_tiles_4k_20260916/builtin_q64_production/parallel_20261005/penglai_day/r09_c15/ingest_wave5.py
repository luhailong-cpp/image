import helper as h
from pathlib import Path
src=Path('C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,p in {'p24':'exec-5f867c19-5bd1-41a6-b539-ddc6a7d6489c.png','p33':'exec-03dc389c-430f-4d8c-ad59-0fc7bd200e46.png','p42':'exec-ec53dad8-4e14-4206-835f-ce053058e5bb.png'}.items():h.ingest(str(src/p),n)
