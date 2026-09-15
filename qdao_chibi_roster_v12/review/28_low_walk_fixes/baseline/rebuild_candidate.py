#!/usr/bin/env python3
"""Rebuild the independent pending 28 candidate. Does not seal or publish."""
from pathlib import Path
import subprocess,sys
root=Path(__file__).resolve().parent
base=root.parent.parent
source=root/"source"
subprocess.run([sys.executable,"-X","utf8","-B",str(source/"assemble_28_candidate.py")],check=True)
command=[sys.executable,"-X","utf8","-B",str(base/"process_roster.py"),"--character-dir",str(root)]
for flag,name in [("--s-e","s_e"),("--n-w","n_w"),("--ne-sw","ne_sw"),("--nw-se","nw_se"),("--idle","idle")]:command.extend([flag,str(source/(name+".png"))])
command.extend(["--portrait-raw",str(source/"portrait-daoist.png"),"--alignment-version","3","--common-scale","1.02941176470588","--despill-magenta-edge","--despill-radius","4"])
subprocess.run(command,check=True)
subprocess.run([sys.executable,"-X","utf8","-B",str(base/"verify_delivery.py"),"--character-dir",str(root),"--allow-pending-visual"],check=True)
