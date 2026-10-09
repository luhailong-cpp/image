from pathlib import Path
R=Path(__file__).resolve().parent
dst=R/'assembly_r11_c16.py';assert not dst.exists()
s=(R/'assembly_r10_c16.py').read_text(encoding='utf-8-sig')
s=s.replace('r10','TEMP_R10').replace('r09','r10').replace('TEMP_R10','r11').replace('(61440, 36864)','(61440, 40960)')
dst.write_text(s,encoding='utf-8')
print(dst)
