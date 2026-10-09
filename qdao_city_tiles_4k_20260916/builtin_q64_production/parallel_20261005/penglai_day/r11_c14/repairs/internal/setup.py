from pathlib import Path
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_day/r11_c14');O=R/'repairs/internal';O.mkdir(parents=True,exist_ok=True)
s=(R.parent/'r11_c13/repairs/internal/quilt.py').read_text(encoding='utf-8-sig').replace('r11_c13','r11_c14').replace("(f'p{r}{c}.png' if (r,c)!=(3,3) else 'p33-floorfix.png')","f'p{r}{c}.png'")
(O/'quilt.py').write_text(s,encoding='utf8')
a=(R.parent/'r11_c15/repairs/internal/ai_helper.py').read_text(encoding='utf-8-sig');(O/'ai_helper.py').write_text(a,encoding='utf8')
