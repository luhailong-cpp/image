from pathlib import Path
T=Path(__file__).resolve().parent
old=T.parent/'r10_c10'
for n in ['internal_qa.py','quilt_internal.py']:
 (T/n).write_text((old/n).read_text(encoding='utf8').replace('r10_c10','r11_c10'),encoding='utf8')
s=(old/'shared_task.py').read_text(encoding='utf8');s=s[:s.index('def setup():')]+s[s.index('def prepare('):];(T/'repair_task.py').write_text(s.replace(" if sys.argv[1]=='setup':setup()\n elif",' if'),encoding='utf8')
s=(old/'compose_shared.py').read_text(encoding='utf8');(T/'compose_patch.py').write_text(s[:s.index('def run():')],encoding='utf8')

