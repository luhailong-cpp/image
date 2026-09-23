"""Root-owned S and SE archived results; no generation or overwrite."""
import re, sys, subprocess, json
from pathlib import Path
HERE=Path(__file__).resolve().parent
GEN=HERE.parent/'09-generation'
for arg in sys.argv[1:]:
    aid, direction, frame=arg.split(':')
    assert direction in ('S','SE')
    p=GEN/aid
    hint=json.loads((p/'tool-result.json').read_text(encoding='utf-8'))['output_hint']
    original=re.search(r' as (.+?\.png) by default\.',hint).group(1)
    if not (p/'generation.json').exists():
        subprocess.run([sys.executable,'-B',str(HERE/'archive_generation.py'),'--archive',str(p),'--original',original,'--tool-result',str(p/'tool-result.json')],check=True)
    cmd=[sys.executable,'-B',str(HERE/'export_frame.py'),'--archive',str(p),'--direction',direction,'--kind','idle' if frame=='idle' else 'walk','--chroma-profile','none']
    if frame!='idle':cmd+=['--frame',frame]
    if direction=='S':cmd+=['--variant','native']
    subprocess.run(cmd,check=True)
