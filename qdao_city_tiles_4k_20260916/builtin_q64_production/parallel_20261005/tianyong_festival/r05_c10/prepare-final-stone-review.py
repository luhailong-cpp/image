from pathlib import Path
from PIL import Image
import json
B=Path(__file__).parent;Q=B/'full-tile-qa';c=json.loads((B/'local-source-checkpoint.json').read_text());I=Image.open(c['fragment']['file']);I.crop((1800,1900,2100,2180)).save(Q/'central-junction-detail-native.png')
