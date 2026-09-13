"""Rebuild deterministic media. Visual approval is reset and must be repeated."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,sys
root=Path(__file__).resolve().parent;common=root.parent
def run(script,*args):
    print('Running '+script.name,flush=True)
    subprocess.run([sys.executable,'-X','utf8','-B',str(script)]+[str(x) for x in args],check=True)
run(root/'assemble_corrections.py')
pairs={'s_e':('S','E'),'n_w':('N','W'),'ne_sw':('NE','SW'),'nw_se':('NW','SE')}
def pair(item):
    kind,(a,b)=item;ac,ar=(2,4) if a in ['S','N'] else (4,2);bc,br=(2,4) if b in ['S','N'] else (4,2)
    run(common/'assemble_raw.py','--kind',kind,'--first',root/f'source/walk-{a}.png','--second',root/f'source/walk-{b}.png','--first-cols',ac,'--first-rows',ar,'--second-cols',bc,'--second-rows',br,'--output',root/f'source/{kind}.png')
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(pair,pairs.items()))
args=['--character-dir',root,'--component-padding','0','--despill-magenta-edge']
for kind in pairs:args+=['--'+kind.replace('_','-'),root/f'source/{kind}.png']
args+=['--idle',root/'source/idle.png','--portrait-raw',root/'source/portrait-daoist.png']
run(common/'process_roster.py',*args)
run(common/'verify_delivery.py','--character-dir',root,'--allow-pending-visual')
print('Numeric media verification complete. Final visual review required.',flush=True)

