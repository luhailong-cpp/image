from pathlib import Path
import sys
O=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r11_c14/repairs/internal');sys.path.insert(0,str(O));import ai_helper as h
G=Path(r'C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,g in [('sail-middle-left','c2ce2c03-480d-45c7-bf23-5d7056654f1e'),('mast-middle','7feec191-100a-4d87-aee7-7d84f84da743'),('sail-middle-right','005182a6-c777-470d-996e-f5e8fb61cd5a')]:h.ingest(n,G/('exec-'+g+'.png'))
