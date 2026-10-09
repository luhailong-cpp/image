from pathlib import Path
import json,hashlib,sys
D=Path(sys.argv[1]);read=lambda p:json.loads(Path(p).read_text(encoding='utf-8-sig'));r=read(D/'request.json');r['payload']['referenced_image_paths'][1]=str(D.parent/'nearby-native-material-swatch.png');(D/'request.json').write_text(json.dumps(r,indent=2));p=read(D/'preparation.json');p['references']=[{'file':f,'sha256':hashlib.sha256(Path(f).read_bytes()).hexdigest()} for f in r['payload']['referenced_image_paths']];(D/'preparation.json').write_text(json.dumps(p,indent=2))
