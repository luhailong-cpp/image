"""Select north heel corrections, retaining each independently generated pose."""
import json, subprocess, sys
from pathlib import Path
from common import DELIVERY
here=Path(__file__).resolve().parent
src=DELIVERY/'work/N/variants/heels/sources'
for p in sorted(src.rglob('*.json')):
    r=json.loads(p.read_text(encoding='utf-8'))
    cmd=[sys.executable,'-B',str(here/'export_frame.py'),'--archive',str(Path(r['source']['path']).parent),'--direction','N','--kind',r['kind'],'--variant','finalheels','--chroma-profile','none']
    if r['kind']=='walk':
        cmd+=['--frame',str(r['frame'])]
        if r['frame']==14:
            cmd+=['--cell-scale','0.8272','--scale-evidence','Root and qa_complete09 independently observed N14 head, torso, garment and bow all about 6 percent larger than neighboring N13/N15/N16 in 1024 composites. Whole native canvas uniformly reduced by 6 percent; preserves joint geometry and recorded anchor. Not per-pose bbox height normalization.']
    subprocess.run(cmd,check=True)
