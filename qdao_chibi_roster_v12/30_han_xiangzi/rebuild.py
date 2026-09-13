"""Rebuild deterministic exports only; never generate or approve artwork."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import subprocess,sys
root=Path(__file__).resolve().parent
common=root.parent
python=[sys.executable,'-X','utf8','-B']
def run(script,*args):
    command=python+[str(script)]+[str(a) for a in args]
    print('Running '+str(script.name),flush=True)
    subprocess.run(command,check=True)
run(root/'assemble_corrections.py')
phase_args=[]
for i in range(1,9):phase_args+=['--phase',root/f'source/phase{i:02d}-turnaround.png']
run(common/'assemble_phases.py',*phase_args,'--output-dir',root/'phase-transposed')
pairs={'s_e':('S','E'),'n_w':('N','W'),'ne_sw':('NE','SW'),'nw_se':('NW','SE')}
def pair(item):
    kind,(first,second)=item
    run(common/'assemble_raw.py','--kind',kind,'--first',root/f'phase-transposed/walk-{first}.png','--second',root/f'phase-transposed/walk-{second}.png','--first-rows','2','--first-cols','4','--second-rows','2','--second-cols','4','--output',root/f'source/{kind}.png')
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(pair,pairs.items()))
args=['--character-dir',root,'--component-padding','1']
for kind in pairs:args+=['--'+kind.replace('_','-'),root/f'source/{kind}.png']
args+=['--idle',root/'source/idle.png']
run(common/'process_roster.py',*args)
run(root/'clean_export_edges.py')
run(common/'verify_delivery.py','--character-dir',root,'--allow-pending-visual')
print('Numeric exports complete; fresh visual review is required before game publication.',flush=True)
