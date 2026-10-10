from pathlib import Path
r=Path(__file__).resolve().parent
s=(r/'prepare_r10_c16.py').read_text(encoding='utf-8-sig')
p=r/'prepare_r11_c16.py';assert not p.exists()
s=s.replace('r10','TMP10').replace('r09','r10').replace('TMP10','r11').replace('[61440,36864,4096,4096]','[61440,40960,4096,4096]')
p.write_text(s,encoding='utf-8')
