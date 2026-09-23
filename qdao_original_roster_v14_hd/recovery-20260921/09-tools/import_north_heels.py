"""Select individually generated north footwear corrections in an isolated revision."""
import subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
for arg in sys.argv[1:]:
    aid,slot=arg.split(':')
    assert aid.startswith('N') and '-heel-v' in aid
    cmd=[sys.executable,'-B',str(HERE/'export_frame.py'),'--archive',str(HERE.parent/'09-generation'/aid),'--direction','N','--kind','idle' if slot=='idle' else 'walk','--variant','heels','--chroma-profile','none']
    if slot!='idle':cmd+=['--frame',slot]
    subprocess.run(cmd,check=True)
