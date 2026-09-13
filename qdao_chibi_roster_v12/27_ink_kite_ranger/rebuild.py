from pathlib import Path
import subprocess,sys
c=Path(__file__).resolve().parent;r=c.parent;s=c/'source';p=c/'prompts'
def run(*args):subprocess.run([sys.executable,'-X','utf8','-B',*map(str,args)],check=True)
run(r/'inspect_sheet.py','--kind','NW','--rows',2,'--cols',4,'--component-padding',0,'--input',s/'walk-NW.png','--output-dir',c/'processing/inspect-NW-final')
for kind,a,b,ar,ac,br,bc in [('s_e','S','E-wide',4,2,2,4),('n_w','N','W',4,2,2,4),('ne_sw','NE','SW',2,4,2,4),('nw_se','NW','SE',2,4,2,4)]:
 run(r/'assemble_raw.py','--kind',kind,'--first',s/f'walk-{a}.png','--second',s/f'walk-{b}.png','--first-rows',ar,'--first-cols',ac,'--second-rows',br,'--second-cols',bc,'--output',s/f'pair-{kind}.png')
 (p/f'{kind}.txt').write_text('Deterministic rearrangement of individually generated and reviewed directions '+a+' and '+b+'. See original per-direction prompts and pair .assembly.json for all raw SHA and cell records.',encoding='utf-8')
run(r/'process_roster.py','--character-dir',c,'--s-e',s/'pair-s_e.png','--n-w',s/'pair-n_w.png','--ne-sw',s/'pair-ne_sw.png','--nw-se',s/'pair-nw_se.png','--idle',s/'idle.png','--portrait-raw',s/'portrait-daoist.png','--component-padding',0)
run(r/'verify_delivery.py','--character-dir',c,'--allow-pending-visual')
