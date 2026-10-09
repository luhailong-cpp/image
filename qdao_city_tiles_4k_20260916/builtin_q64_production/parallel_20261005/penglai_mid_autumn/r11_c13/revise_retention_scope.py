from pathlib import Path
import json,hashlib,shutil
R=Path(r'D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/penglai_mid_autumn')
for tile in ['r09_c15','r11_c13']:
 T=R/tile;plan=T/'retention-plan.json';h=hashlib.sha256(plan.read_bytes()).hexdigest();H=T/'retention-plan-history';H.mkdir(exist_ok=True)
 dest=H/f'plan-{h}.json';assert not dest.exists();shutil.copy2(plan,dest)
 prep=T/'prepare_retention.py';ph=hashlib.sha256(prep.read_bytes()).hexdigest();shutil.copy2(prep,H/f'prepare-{ph}.py')
 s=prep.read_text()
 start=s.index("assembly=read(T/'output/native-assembly.json')")
 end=s.index("for key,uses in extbinary.items()",start)
 if tile=='r09_c15':replacement="# Native/repair transform fields are historical processing artifacts. Preserve their TEXT, retire binaries after export.\n"
 else:replacement="""# Native transform and planning masks are historical processing artifacts, not runtime resources.
keep(T/'references/day-structure-snapshot.png','current_design','Current paired day layout snapshot retained with approved night design.')
keep(T/'references/north-native320.png','current_required_source','Exact frozen320px current north support; real neighbor canonical remains outside this scope untouched.')
"""
 s=s[:start]+replacement+s[end:]
 s=s.replace("actual final effective transform/color/opacity/mask fields retained.","all transform/mask numbers and source hashes remain in TEXT; final PNG no longer depends on processing fields.")
 s=s.replace("Current applied-v19 QA and effective fields retained.","Current applied-v19 QA and all TEXT retained.")
 s=s.replace("Current final QA and effective fields retained.","Current final QA and all TEXT retained.")
 prep.write_text(s,encoding='utf-8')
 print(tile,h)

