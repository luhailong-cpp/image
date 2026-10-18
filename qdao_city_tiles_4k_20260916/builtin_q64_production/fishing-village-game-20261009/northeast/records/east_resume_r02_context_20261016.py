from pathlib import Path
from PIL import Image
import json,hashlib
z=Path(__file__).resolve().parent.parent
src=Path('D:/work/image/qdao_city_tiles_4k_20260916/builtin_q64_production/parallel_20261005/daylight-only-20261009/donghai-natural-stone-clear-routes-v10.png')
out=z/'guides/r02_c14.wider-boat-context-20261016.png'
assert not out.exists()
Image.open(src).crop((1140,65,1254,190)).resize((912,1000),Image.Resampling.NEAREST).save(out)
Path(str(out)+'.derived.json').write_text(json.dumps({'purpose':'layout context ONLY, never final pixels','operation':'integer crop114x125 then8xnearest readability','source':str(src),'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'sourceBox':[1140,65,1254,190]},indent=2))
