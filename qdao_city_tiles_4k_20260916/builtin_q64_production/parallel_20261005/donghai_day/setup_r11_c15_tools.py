from pathlib import Path
import json,hashlib
r=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/donghai_day')
s=(r/'prepare_r10_c15.py').read_text()
s=s.replace("T=R/'r10_c15'","T=R/'r11_c15'").replace("=='r10_c15'","=='r11_c15'").replace("[57344,36864,4096,4096]","[57344,40960,4096,4096]").replace("('north','r09_c15'),('east','r10_c16'),('west','r10_c14'),('south','r11_c15')","('north','r10_c15'),('east','r11_c16'),('west','r11_c14'),('south','r12_c15')")
start=s.index('    external=[]')
end=s.index('    now=datetime',start)
s=s[:start]+"    external=[] # Actual east natives will be explicitly bound after root has generated them.\n"+s[end:]
s=s.replace("'tile':'r10_c15'","'tile':'r11_c15'").replace('bound complete north r09_c15 SHA','bound complete north r10_c15 SHA').replace('rows1..4 col1 explicit immutable SHA bindings, no assumption of complete tile','pending real east native source; never synthesize absent context')
(r/'prepare_r11_c15.py').write_text(s)

