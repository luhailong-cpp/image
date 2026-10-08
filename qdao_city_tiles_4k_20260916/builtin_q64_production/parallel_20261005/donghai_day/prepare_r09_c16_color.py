from pathlib import Path
R=Path(__file__).resolve().parent
src=R/'repair_r09_c15_color.py';dst=R/'repair_r09_c16_color.py'
assert not dst.exists()
s=src.read_text(encoding='utf-8').replace('r09_c15','r09_c16').replace('45a82a7b24818094fdb8a0b5ee6f3dd3ca554e2c01eff2c862de9184afa8bf66','ff169961a00d04558464d4436397938b02ac4e53fd492f7a74122b49eda53095')
dst.write_text(s,encoding='utf-8')
print(dst)
