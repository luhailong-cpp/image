from pathlib import Path
import sys
O=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r11_c14/repairs/internal');sys.path.insert(0,str(O));import ai_helper as h
G=Path(r'C:/Users/luyua/.codex/generated_images/01a11b1b-2c24-7812-88af-b8b4302ee43c')
for n,g in [('yard-upper','10089052-2146-4710-96e8-5eee927d0fc1'),('mast-upper','272f656a-273f-455a-b1f3-3d8ff3f3fbbe'),('dock-upper','e9a9b642-2a45-4ceb-bb12-7018d40acf28')]:h.ingest(n,G/('exec-'+g+'.png'))
