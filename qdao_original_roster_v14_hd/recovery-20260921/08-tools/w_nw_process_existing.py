from pathlib import Path
import sys
sys.path.insert(0,str(Path('qdao_original_roster_v14_hd/recovery-20260921/08-tools').resolve()))
from process import process,GEN,OUT
for d in sorted(GEN.iterdir()):
 if ('-W-' in d.name or '-NW-' in d.name) and (d/'raw.png').exists() and not (OUT/d.name/'source.json').exists():
  print(process(d.name))

