from pathlib import Path
root=Path(__file__).resolve().parent
src=(root/'assembly_r09_c16.py').read_text(encoding='utf-8-sig')
dst=root/'assembly_r10_c16.py'
assert not dst.exists()
src=src.replace('r09','TEMP_R09').replace('r08','r09').replace('TEMP_R09','r10').replace('(61440, 32768)','(61440, 36864)')
dst.write_text(src,encoding='utf-8')
print(dst)
