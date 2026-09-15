from pathlib import Path
import subprocess,sys,json
C=Path(__file__).resolve().parent
assert C.name=='26_osmanthus_healer' and C.parent.name=='candidate-stable-body'
ROOT=C.parent.parent;R=ROOT/'review/26_healer_natural_fixes';O=ROOT/'26_osmanthus_healer'
commands=[[sys.executable,str(R/'assemble_candidate.py')],[sys.executable,str(R/'verify_assembly.py')],[sys.executable,str(ROOT/'process_roster.py'),'--character-dir',str(C),'--s-e',str(C/'source/pair-s_e.png'),'--n-w',str(C/'source/pair-n_w.png'),'--ne-sw',str(C/'source/pair-ne_sw.png'),'--nw-se',str(C/'source/pair-nw_se.png'),'--idle',str(C/'source/idle.png'),'--portrait',str(O/'portrait.png'),'--alignment-version','3','--common-scale','1.0120481927710843','--component-padding','2','--despill-magenta-edge','--despill-radius','4'],[sys.executable,str(ROOT/'verify_delivery.py'),'--character-dir',str(C),'--allow-pending-visual'],[sys.executable,str(R/'make_export_evidence.py')]]
(C/'processing-commands.json').write_text(json.dumps(commands,indent=2),encoding='utf-8')
for c in commands:subprocess.run(c,check=True)
