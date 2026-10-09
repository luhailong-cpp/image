from pathlib import Path
import json,hashlib
D=Path(__file__).parent;r=json.loads((D/'request.json').read_text());r['payload']['referenced_image_paths'][1]=str(D.parent/'r04_c01-v1/nearby-native-material-swatch.png');(D/'request.json').write_text(json.dumps(r,indent=2));p=json.loads((D/'preparation.json').read_text());p['references']=[{'file':f,'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()} for f in r['payload']['referenced_image_paths']];(D/'preparation.json').write_text(json.dumps(p,indent=2))
