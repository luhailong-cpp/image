"""Prepare reference-only r10_c16 layout at the planned adjacent coordinate."""
from pathlib import Path
R=Path(__file__).resolve().parent
p=R/'prepare_r10_c16.py'
assert not p.exists()
s=(R/'prepare_r09_c16.py').read_text(encoding='utf-8')
s=s.replace('r08_c16','TEMP_NORTH').replace('r09_c16','r10_c16').replace('TEMP_NORTH','r09_c16').replace('r09_c15','r10_c15')
s=s.replace('[61440,32768,4096,4096]','[61440,36864,4096,4096]')
p.write_text(s,encoding='utf-8')
print(p)
