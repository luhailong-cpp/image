from pathlib import Path
p=Path(__file__).resolve().parent
s=(p/'repair_r10_c16_internal_color.py').read_text()
s=s.replace("'internal-color-match'","'internal-color-match-v2'").replace('(24,24)','(8,8)').replace('c[49:]','c[17:]').replace('c[:-49]','c[:-17]').replace('c[:,49:]','c[:,17:]').replace('c[:,:-49]','c[:,:-17]').replace('/49','/17').replace('49px','17px')
(p/'repair_r10_c16_internal_color_v2.py').write_text(s,encoding='utf-8')
