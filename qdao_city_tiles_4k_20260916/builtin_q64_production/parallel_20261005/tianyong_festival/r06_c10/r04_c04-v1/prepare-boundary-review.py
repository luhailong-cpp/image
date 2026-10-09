from pathlib import Path
from PIL import Image
import json
D=Path(__file__).parent;F=D/'final-v4';cp=json.loads((D/'source-checkpoint-input.json').read_text(encoding='utf-8-sig'));a=Image.open(cp['coupledBottom']['file']).convert('RGB');j=Image.open(F/'joined.png').convert('RGB');a.paste(j.crop((0,1139,1139,1780)),(2957,0));a.crop((2797,0,3357,750)).save(F/'qa/left-return-boundary.png')
